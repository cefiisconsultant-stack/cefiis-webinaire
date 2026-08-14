import json
import uuid
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import DiagnosticEvenement, DiagnosticReponse


class DiagnosticViewsTests(TestCase):
    def setUp(self):
        self.session_id = uuid.uuid4()
        self.payload = {
            "session_id": str(self.session_id),
            "prenom": "Aïcha",
            "pays": "BJ",
            "numero_national": "0197345232",
            "email": "aicha@example.com",
            "domaine": "rh",
            "domaine_autre": "",
            "experience": "10a20",
            "situation": "poste",
            "situation_autre": "",
            "sollicitation": "souvent",
            "motivation": "valorisation",
            "motivation_autre": "",
            "elements": ["positionnement", "offre"],
            "difficulte": "temps",
            "difficulte_autre": "",
            "anciennete_consultant": "",
            "duree_secondes": 118,
            "utm_source": "whatsapp",
            "utm_campaign": "lancement-aout",
            "utm_content": "groupe-01-soir",
            "device": "mobile",
            "landing_path": "/diagnostic/",
            "consentement_diagnostic": True,
            "consentement_marketing": True,
        }

    def post_json(self, url, payload):
        return self.client.post(url, data=json.dumps(payload), content_type="application/json")

    def test_quiz_is_available(self):
        response = self.client.get(reverse("diagnostic:quiz"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Votre expérience peut-elle devenir")

    def test_valid_submission_creates_private_result_url(self):
        response = self.post_json(reverse("diagnostic:enregistrer"), self.payload)
        self.assertEqual(response.status_code, 200)
        reponse = DiagnosticReponse.objects.get()
        self.assertEqual(reponse.whatsapp, "+2290197345232")
        self.assertEqual(reponse.score, 2)
        self.assertEqual(reponse.segment, "structuration")
        self.assertTrue(reponse.consentement_marketing)
        self.assertIn(str(reponse.public_id), response.json()["redirect"])
        self.assertEqual(DiagnosticEvenement.objects.filter(nom="complete").count(), 1)

    def test_invalid_choice_is_rejected_instead_of_defaulted(self):
        self.payload["situation"] = "valeur_inventee"
        response = self.post_json(reverse("diagnostic:enregistrer"), self.payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(DiagnosticReponse.objects.count(), 0)

    def test_other_situation_requires_text(self):
        self.payload["situation"] = "autre"
        response = self.post_json(reverse("diagnostic:enregistrer"), self.payload)
        self.assertEqual(response.status_code, 400)

    def test_contact_consent_is_required(self):
        self.payload["consentement_diagnostic"] = False
        response = self.post_json(reverse("diagnostic:enregistrer"), self.payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(DiagnosticReponse.objects.count(), 0)

    def test_consultant_branch_uses_consultant_fields(self):
        self.payload.update({"situation": "consultant", "anciennete_consultant": "1a3", "difficulte": "missions"})
        response = self.post_json(reverse("diagnostic:enregistrer"), self.payload)
        self.assertEqual(response.status_code, 200)
        reponse = DiagnosticReponse.objects.get()
        self.assertEqual(reponse.difficulte_consultant, "missions")
        self.assertEqual(reponse.difficulte, "")

    def test_feedback_accepts_only_one_to_five(self):
        self.post_json(reverse("diagnostic:enregistrer"), self.payload)
        reponse = DiagnosticReponse.objects.get()
        url = reverse("diagnostic:avis", args=[reponse.public_id])
        bad = self.post_json(url, {"note": 6})
        self.assertEqual(bad.status_code, 400)
        good = self.post_json(url, {"note": 5, "commentaire": "Très clair"})
        self.assertEqual(good.status_code, 200)
        reponse.refresh_from_db()
        self.assertEqual(reponse.note_formulaire, 5)

    def test_telemetry_rejects_unknown_event(self):
        response = self.post_json(reverse("diagnostic:evenement"), {"session_id": str(self.session_id), "nom": "capture_email"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(DiagnosticEvenement.objects.count(), 0)

    def test_telemetry_deduplicates_funnel_events(self):
        event = {
            "session_id": str(self.session_id),
            "nom": "step_view",
            "ecran": "domaine",
            "etape": 2,
            "utm_source": "whatsapp",
        }
        self.post_json(reverse("diagnostic:evenement"), event)
        self.post_json(reverse("diagnostic:evenement"), event)
        self.assertEqual(DiagnosticEvenement.objects.count(), 1)

    def test_telemetry_refuses_explicit_cross_origin_posts(self):
        response = self.client.post(
            reverse("diagnostic:evenement"),
            data=json.dumps({"session_id": str(self.session_id), "nom": "view", "ecran": "intro"}),
            content_type="application/json",
            HTTP_ORIGIN="https://example.org",
        )
        self.assertEqual(response.status_code, 403)

    def test_result_uses_profile_market_signal_and_attributed_checkout(self):
        self.post_json(reverse("diagnostic:enregistrer"), self.payload)
        reponse = DiagnosticReponse.objects.get()
        response = self.client.get(reverse("diagnostic:resultat", args=[reponse.public_id]))
        self.assertContains(response, "Expert salarié en transition progressive")
        self.assertContains(response, "Le marché vous envoie déjà un signal fort")
        self.assertContains(response, f"diagnostic={reponse.public_id}")

    def test_report_is_unique_and_machine_readable(self):
        self.post_json(reverse("diagnostic:enregistrer"), self.payload)
        self.post_json(reverse("diagnostic:evenement"), {
            "session_id": str(self.session_id), "nom": "view", "ecran": "intro"
        })
        output = StringIO()
        call_command("rapport_diagnostic", jours=30, format="json", stdout=output)
        report = json.loads(output.getvalue())
        self.assertEqual(report["funnel"]["vues_uniques"], 1)
        self.assertEqual(report["funnel"]["termines"], 1)
        self.assertIn("Structuration", report["segments"])
