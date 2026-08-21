# Installation locale — sécurisation de l’e-book

Cette archive contient uniquement les fichiers ajoutés ou modifiés. Elle ne contient ni votre base de données, ni votre fichier `.env`, ni votre PDF.

## Résultat obtenu

- après confirmation de KKiaPay, le client retrouve la page de remerciement déjà présente dans le projet ;
- il peut télécharger son e-book depuis la page et depuis le lien reçu par e-mail ;
- le lien personnel expire après 72 heures et accepte au maximum 3 téléchargements ;
- ces limites ne sont pas affichées au client ;
- le même template de remerciement affiche un message d’assistance lorsque le lien n’est plus disponible ;
- les tentatives sont enregistrées dans l’administration Django sans conserver l’adresse IP en clair ;
- un administrateur peut réactiver un lien depuis « Ebook achats » ;
- les secrets Django, de messagerie et KKiaPay sont lus depuis `.env` ;
- le PDF n’est plus livré directement depuis `/media/` ; il doit être conservé dans `private/ebook/`.

## 1. Remplacer les fichiers

Adaptez uniquement le chemin de l’archive si votre navigateur l’a enregistrée ailleurs.

```bash
cd /media/honorat/autres-os/backup_home/cefiis/cefiis

PATCH_ARCHIVE="/home/honorat/Téléchargements/CEFIIS_SECURISATION_EBOOK_V2.zip"
BACKUP_DIR="../sauvegarde_ebook_avant_securisation_$(date +%Y%m%d_%H%M%S)"

test -f "$PATCH_ARCHIVE" || { echo "Archive introuvable : $PATCH_ARCHIVE"; exit 1; }
mkdir -p "$BACKUP_DIR"

cp --parents \
  .gitignore \
  cefiis/settings/base.py \
  cefiis/settings/dev.py \
  ebook/admin.py \
  ebook/models.py \
  ebook/tests.py \
  ebook/views.py \
  ebook/templates/ebook/email_ebook.html \
  ebook/templates/ebook/merci.html \
  "$BACKUP_DIR"

unzip -o "$PATCH_ARCHIVE" -d .
```

Le dossier de sauvegarde affiché par la commande reste à côté du projet, dans `/media/honorat/autres-os/backup_home/cefiis/`.

## 2. Mettre le PDF hors du dossier public `media`

```bash
cd /media/honorat/autres-os/backup_home/cefiis/cefiis
mkdir -p private/ebook

cp media/ebook/De_l_Expert_au_Consultant_Professionnel.pdf \
   private/ebook/De_l_Expert_au_Consultant_Professionnel.pdf

test -f private/ebook/De_l_Expert_au_Consultant_Professionnel.pdf \
  && echo "PDF privé prêt" \
  || echo "PDF introuvable : vérifiez son nom actuel dans le dossier media/ebook"
```

Ne supprimez l’ancienne copie dans `media/ebook/` qu’après avoir vérifié que le nouveau téléchargement fonctionne. Une fois la vérification terminée, retirez-la afin d’empêcher un accès direct par `/media/...`.

## 3. Compléter `.env`

Générez d’abord une nouvelle clé Django :

```bash
cd /media/honorat/autres-os/backup_home/cefiis/cefiis
source ../env/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
nano .env
```

Ajoutez ou corrigez les lignes suivantes. Remplacez les valeurs indiquées, mais ne recopiez jamais vos secrets dans GitHub.

```dotenv
SECRET_KEY=collez-ici-la-nouvelle-cle-generee
DEBUG=True
SITE_URL=http://127.0.0.1:8000

KKIAPAY_PUBLIC_KEY=votre-cle-publique
KKIAPAY_PRIVATE_KEY=votre-cle-privee
KKIAPAY_SECRET_KEY=votre-cle-secrete
KKIAPAY_SANDBOX=True

EBOOK_PRICE=100
EBOOK_DOWNLOAD_MAX=3
EBOOK_DOWNLOAD_EXPIRY_HOURS=72
EBOOK_FILE_PATH=/media/honorat/autres-os/backup_home/cefiis/cefiis/private/ebook/De_l_Expert_au_Consultant_Professionnel.pdf
EBOOK_SUPPORT_EMAIL=etiennegbedagbe@cefiis.com

DIAGNOSTIC_WHATSAPP_GROUP_NAME=De l'Expert au Consultant - Cefiis
DIAGNOSTIC_WHATSAPP_GROUP_URL=

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_USE_TLS=False
EMAIL_HOST_USER=etiennegbedagbe@cefiis.com
EMAIL_HOST_PASSWORD=votre-nouveau-mot-de-passe-smtp
DEFAULT_FROM_EMAIL=etiennegbedagbe@cefiis.com
SERVER_EMAIL=etiennegbedagbe@cefiis.com
```

Laissez `DIAGNOSTIC_WHATSAPP_GROUP_URL` vide si l’invitation ne doit plus apparaître. Si vous souhaitez conserver la section déjà présente dans le template, placez son URL dans `.env`.

Les statuts de paiement (`en_attente`, `paye`, `echec`) restent dans le modèle Django : ce sont des états métier, pas des réglages. Seuls le maximum de téléchargements et la durée d’accès doivent être modifiables dans `.env`.

`EBOOK_PRICE` est la source unique du prix vérifié par le serveur. Pour un test sandbox à 100 FCFA, utilisez `EBOOK_PRICE=100`. Avant la mise en production, utilisez `EBOOK_PRICE=2000` et `KKIAPAY_SANDBOX=False`. Redémarrez Django après chaque changement de `.env`.

Le projet reçu contenait en clair une clé Django, un mot de passe SMTP Hostinger et un ancien mot de passe d’application Gmail commenté. Considérez-les comme exposés : changez-les chez les fournisseurs concernés. Les clés KKiaPay du projet étaient déjà chargées depuis `.env` ; ne les remplacez que si elles ont aussi été publiées ailleurs.

Si vous utilisez temporairement Gmail, remplacez uniquement la partie messagerie par :

```dotenv
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_SSL=False
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-adresse@gmail.com
EMAIL_HOST_PASSWORD=votre-nouveau-mot-de-passe-application-google
DEFAULT_FROM_EMAIL=votre-adresse@gmail.com
SERVER_EMAIL=votre-adresse@gmail.com
```

## 4. Appliquer la migration et vérifier

```bash
cd /media/honorat/autres-os/backup_home/cefiis/cefiis
source ../env/bin/activate

python manage.py migrate
python manage.py check
python manage.py test ebook
python manage.py runserver
```

Ouvrez ensuite le parcours de paiement en local et utilisez une transaction de test KKiaPay. Avec `KKIAPAY_SANDBOX=True`, n’utilisez que l’environnement de test.

## 5. Ce que voit le client après paiement

Le template existant conserve son apparence et affiche :

1. « Merci [Prénom] » ;
2. « Votre paiement a été confirmé. Votre ebook est prêt » ;
3. le bouton « Télécharger mon ebook » ;
4. l’indication que le même lien personnel a été envoyé par e-mail.

Lorsque l’accès n’est plus disponible, le client lit : « Ce lien n’est plus disponible. » puis une consigne lui demandant de contacter l’assistance avec l’adresse utilisée lors du paiement, sans effectuer un nouveau paiement.

## 6. Administration

Dans l’administration Django :

- ouvrez « Ebook achats » pour voir le compteur, l’expiration et le dernier téléchargement ;
- ouvrez un achat pour consulter ses événements de téléchargement ;
- sélectionnez un achat payé, puis lancez l’action « Réactiver le lien de téléchargement sélectionné » si un client légitime a besoin d’aide.

La limitation protège le lien, pas le fichier déjà enregistré sur l’appareil. Empêcher ou mesurer le transfert direct du PDF demandera une seconde version, par exemple avec filigrane personnalisé par acheteur. Ce mécanisme n’est volontairement pas inclus dans cette mise à jour.
