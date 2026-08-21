import json
import tempfile
import uuid
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import EbookAchat, EbookTelechargementEvenement
from diagnostic.models import DiagnosticEvenement, DiagnosticReponse


@override_settings(
    KKIAPAY_PUBLIC_KEY="public-test",
    KKIAPAY_PRIVATE_KEY="private-test",
    KKIAPAY_SECRET_KEY="secret-test",
    EBOOK_PRICE=2000,
    EBOOK_DOWNLOAD_MAX=3,
    EBOOK_DOWNLOAD_EXPIRY_HOURS=72,
    EBOOK_SUPPORT_EMAIL="support@example.com",
)
class PaiementEbookTests(TestCase):
    def setUp(self):
        self.media_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_directory.cleanup)
        self.media_override = override_settings(MEDIA_ROOT=self.media_directory.name)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)

        self.ebook_path = (
            Path(self.media_directory.name)
            / "ebook"
            / "De_l_Expert_au_Consultant_Professionnel.pdf"
        )
        self.ebook_path.parent.mkdir(parents=True, exist_ok=True)
        self.ebook_path.write_bytes(b"%PDF-1.4\n% test ebook\n")
        self.ebook_override = override_settings(EBOOK_FILE_PATH=str(self.ebook_path))
        self.ebook_override.enable()
        self.addCleanup(self.ebook_override.disable)

    def create_paid_purchase(self, transaction_id="TEST_download_123"):
        now = timezone.now()
        return EbookAchat.objects.create(
            transaction_id=transaction_id,
            email="aicha@example.com",
            prenom="Aïcha",
            montant=2000,
            statut="paye",
            date_paiement=now,
            expiration_telechargement=now + timedelta(hours=72),
        )

    def response_kkiapay(self, *, status="SUCCESS", amount=2000):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"status": status, "amount": amount}
        return response

    @patch("ebook.views.envoyer_ebook_par_email")
    @patch("ebook.views.requests.post")
    def test_payment_requires_success_and_exact_launch_price(self, post, send_email):
        post.return_value = self.response_kkiapay()
        response = self.client.post(
            reverse("verifier_paiement"),
            data=json.dumps(
                {
                    "transactionId": "TEST_transaction_123",
                    "prenom": "Aïcha",
                    "email": "aicha@example.com",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        purchase = EbookAchat.objects.get()
        self.assertEqual(purchase.montant, 2000)
        self.assertEqual(purchase.statut, "paye")
        self.assertEqual(purchase.nombre_telechargements, 0)
        self.assertIsNotNone(purchase.expiration_telechargement)
        self.assertGreater(
            purchase.expiration_telechargement,
            purchase.date_paiement + timedelta(hours=71),
        )
        send_email.assert_called_once()
        headers = post.call_args.kwargs["headers"]
        self.assertEqual(headers["x-secret-key"], "secret-test")

    @patch("ebook.views.requests.post")
    def test_payment_with_wrong_amount_does_not_deliver_ebook(self, post):
        post.return_value = self.response_kkiapay(amount=100)
        response = self.client.post(
            reverse("verifier_paiement"),
            data=json.dumps(
                {
                    "transactionId": "TEST_transaction_456",
                    "prenom": "Aïcha",
                    "email": "aicha@example.com",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(EbookAchat.objects.get().statut, "echec")

    def test_sales_page_displays_2000_fcfa(self):
        response = self.client.get(reverse("vente_ebook"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Payer et recevoir l'ebook")
        self.assertContains(response, "2000")
        self.assertTrue(uuid.UUID(response.context["diagnostic_session"]))
        self.assertTrue(
            DiagnosticEvenement.objects.filter(nom="checkout_view").exists()
        )

    @override_settings(EBOOK_PRICE=100)
    @patch("ebook.views.envoyer_ebook_par_email")
    @patch("ebook.views.requests.post")
    def test_sandbox_price_is_shared_by_display_and_server(
        self,
        post,
        send_email,
    ):
        sales_page = self.client.get(reverse("vente_ebook"))
        self.assertEqual(sales_page.context["prix"], 100)

        post.return_value = self.response_kkiapay(amount=100)
        response = self.client.post(
            reverse("verifier_paiement"),
            data=json.dumps(
                {
                    "transactionId": "TEST_sandbox_price_100",
                    "prenom": "Aïcha",
                    "email": "aicha@example.com",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EbookAchat.objects.get().montant, 100)
        send_email.assert_called_once()

    @patch("ebook.views.envoyer_ebook_par_email")
    @patch("ebook.views.requests.post")
    def test_purchase_is_attributed_to_the_diagnostic(self, post, send_email):
        post.return_value = self.response_kkiapay()
        diagnostic = DiagnosticReponse.objects.create(
            prenom="Aïcha",
            whatsapp="+2290197345232",
            pays="BJ",
            indicatif="+229",
            numero_national="0197345232",
            domaine="rh",
            experience="10a20",
            situation="poste",
            sollicitation="souvent",
            motivation="valorisation",
            difficulte="temps",
            consentement_diagnostic=True,
        )
        response = self.client.post(
            reverse("verifier_paiement"),
            data=json.dumps({
                "transactionId": "TEST_attribution_789",
                "prenom": "Aïcha",
                "email": "aicha@example.com",
                "diagnosticId": str(diagnostic.public_id),
                "diagnosticSession": str(diagnostic.session_id),
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        achat = EbookAchat.objects.get()
        self.assertEqual(achat.diagnostic, diagnostic)
        diagnostic.refresh_from_db()
        self.assertTrue(diagnostic.ebook_achete)
        self.assertTrue(
            DiagnosticEvenement.objects.filter(
                session_id=diagnostic.session_id, nom="purchase"
            ).exists()
        )

    def test_thank_you_page_presents_the_download_without_group_invitation(self):
        achat = self.create_paid_purchase("TEST_thanks_123")
        response = self.client.get(
            reverse("page_merci", args=[achat.token_telechargement])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Votre paiement a été confirmé")
        self.assertContains(response, "Votre ebook est prêt")
        self.assertContains(response, "Télécharger mon ebook")
        self.assertNotContains(response, "Rejoindre le groupe WhatsApp")
        self.assertNotContains(response, "3 téléchargements")
        self.assertNotContains(response, "72 heures")
        self.assertContains(response, 'name="viewport"')

    def test_three_downloads_are_allowed_and_the_fourth_is_refused(self):
        achat = self.create_paid_purchase()
        url = reverse("telecharger_ebook", args=[achat.token_telechargement])

        for _ in range(3):
            response = self.client.get(
                url,
                HTTP_USER_AGENT="Test Browser",
                REMOTE_ADDR="192.0.2.10",
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Cache-Control"], "private, no-store, max-age=0")
            self.assertEqual(
                response["X-Robots-Tag"],
                "noindex, nofollow, noarchive",
            )
            b"".join(response.streaming_content)

        achat.refresh_from_db()
        self.assertEqual(achat.nombre_telechargements, 3)
        self.assertIsNotNone(achat.dernier_telechargement_at)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 410)
        self.assertContains(
            response,
            "Ce lien n’est plus disponible.",
            status_code=410,
        )
        self.assertEqual(
            achat.evenements_telechargement.filter(
                resultat=EbookTelechargementEvenement.Resultat.AUTORISE
            ).count(),
            3,
        )
        self.assertTrue(
            achat.evenements_telechargement.filter(
                resultat=EbookTelechargementEvenement.Resultat.LIMITE
            ).exists()
        )
        event = achat.evenements_telechargement.filter(
            resultat=EbookTelechargementEvenement.Resultat.AUTORISE
        ).first()
        self.assertEqual(event.user_agent, "Test Browser")
        self.assertEqual(len(event.empreinte_ip), 64)
        self.assertNotEqual(event.empreinte_ip, "192.0.2.10")

    def test_expired_download_link_is_refused_without_incrementing_counter(self):
        achat = self.create_paid_purchase("TEST_expired_123")
        achat.expiration_telechargement = timezone.now() - timedelta(minutes=1)
        achat.save(update_fields=["expiration_telechargement"])

        response = self.client.get(
            reverse("telecharger_ebook", args=[achat.token_telechargement])
        )

        self.assertEqual(response.status_code, 410)
        achat.refresh_from_db()
        self.assertEqual(achat.nombre_telechargements, 0)
        self.assertTrue(
            achat.evenements_telechargement.filter(
                resultat=EbookTelechargementEvenement.Resultat.EXPIRE
            ).exists()
        )

    def test_missing_file_does_not_consume_a_download(self):
        achat = self.create_paid_purchase("TEST_missing_file_123")
        self.ebook_path.unlink()

        response = self.client.get(
            reverse("telecharger_ebook", args=[achat.token_telechargement])
        )

        self.assertEqual(response.status_code, 503)
        achat.refresh_from_db()
        self.assertEqual(achat.nombre_telechargements, 0)
        self.assertTrue(
            achat.evenements_telechargement.filter(
                resultat=EbookTelechargementEvenement.Resultat.FICHIER_ABSENT
            ).exists()
        )

    def test_unpaid_purchase_cannot_download(self):
        achat = EbookAchat.objects.create(
            transaction_id="TEST_unpaid_123",
            email="aicha@example.com",
            statut="en_attente",
            expiration_telechargement=timezone.now() + timedelta(hours=72),
        )
        response = self.client.get(
            reverse("telecharger_ebook", args=[achat.token_telechargement])
        )
        self.assertEqual(response.status_code, 404)

    @patch("ebook.views.envoyer_ebook_par_email")
    @patch("ebook.views.requests.post")
    def test_rechecking_same_payment_does_not_extend_download_expiration(
        self,
        post,
        send_email,
    ):
        post.return_value = self.response_kkiapay()
        payload = json.dumps(
            {
                "transactionId": "TEST_same_payment_123",
                "prenom": "Aïcha",
                "email": "aicha@example.com",
            }
        )
        first_response = self.client.post(
            reverse("verifier_paiement"),
            data=payload,
            content_type="application/json",
        )
        self.assertEqual(first_response.status_code, 200)
        achat = EbookAchat.objects.get(transaction_id="TEST_same_payment_123")
        first_expiration = achat.expiration_telechargement

        second_response = self.client.post(
            reverse("verifier_paiement"),
            data=payload,
            content_type="application/json",
        )
        self.assertEqual(second_response.status_code, 200)
        achat.refresh_from_db()
        self.assertEqual(achat.expiration_telechargement, first_expiration)
