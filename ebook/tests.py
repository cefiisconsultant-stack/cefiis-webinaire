import json
import uuid
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse

from .models import EbookAchat
from diagnostic.models import DiagnosticEvenement, DiagnosticReponse


@override_settings(
    KKIAPAY_PUBLIC_KEY="public-test",
    KKIAPAY_PRIVATE_KEY="private-test",
    KKIAPAY_SECRET_KEY="secret-test",
)
class PaiementEbookTests(TestCase):
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

    def test_thank_you_page_invites_buyer_to_shared_group(self):
        achat = EbookAchat.objects.create(
            transaction_id="TEST_thanks_123",
            email="aicha@example.com",
            prenom="Aïcha",
            montant=2000,
            statut="paye",
            diagnostic_session_id=uuid.uuid4(),
        )
        response = self.client.get(
            reverse("page_merci", args=[achat.token_telechargement])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cercle des Experts &amp; Consultants | Cefiis")
        self.assertContains(response, "Rejoindre le groupe WhatsApp")
