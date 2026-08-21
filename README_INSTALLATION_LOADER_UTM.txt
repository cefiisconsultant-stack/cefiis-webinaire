CEFIIS — CORRECTIF FINAL LOADER KKIAPAY + SEGMENTATION UTM
==========================================================

CONTENU
-------
1. Le loader élégant reste visible dès le clic de paiement.
2. Il couvre l'iframe tant que KKiaPay n'a pas réellement initialisé son interface.
3. Le formulaire KKiaPay passe ensuite au-dessus et reste entièrement utilisable.
4. Le loader continue derrière le widget pendant le paiement.
5. Après succès : affichage « Paiement reçu. Vérification sécurisée en cours… »,
   vérification par Django, puis redirection vers la page de téléchargement.
6. Après échec, abandon ou fermeture : arrêt du loader et retour au formulaire.
7. Ajout de utm_source_info pour segmenter les audiences jusqu'à l'achat.

REMPLACEMENT EN LOCAL
---------------------
L'archive doit se trouver dans votre dossier Téléchargements.

1. Arrêter le serveur Django avec Ctrl+C.

2. Exécuter :

cd /media/honorat/autres-os/backup_home/cefiis/cefiis
cp -a diagnostic diagnostic_backup_loader_utm_20260821
unzip -o ~/Téléchargements/CEFIIS_loader_KKiaPay_UTM_final_v1.zip -d .

3. Activer l'environnement et appliquer la migration :

source /home/honorat/cefiis/env/bin/activate
DJANGO_ENV=development python manage.py migrate diagnostic
DJANGO_ENV=development python manage.py check
DJANGO_ENV=development python manage.py test diagnostic.tests ebook.tests -v 1
DJANGO_ENV=development python manage.py runserver

4. Ouvrir une fenêtre privée et tester avec le cache désactivé.

FICHIERS MODIFIÉS
-----------------
diagnostic/models.py
diagnostic/views.py
diagnostic/admin.py
diagnostic/static/diagnostic/diagnostic.js
diagnostic/static/diagnostic/resultat.js
diagnostic/static/diagnostic/diagnostic.css
diagnostic/templates/diagnostic/quiz.html
diagnostic/templates/diagnostic/resultat.html
diagnostic/management/commands/rapport_diagnostic.py
diagnostic/tests.py

NOUVEAU FICHIER
---------------
diagnostic/migrations/0004_utm_source_info.py

CONVENTION UTM VALIDÉE
----------------------
utm_source       = plateforme             Exemple : whatsapp
utm_medium       = canal                  Exemple : social
utm_campaign     = campagne               Exemple : diagnostic_consultant_v1
utm_content      = format                 Exemple : affiche
utm_source_info  = audience détaillée     Exemple : groupe_consultants

Exemple :

http://127.0.0.1:8000/diagnostic/?utm_source=whatsapp&utm_medium=social&utm_campaign=diagnostic_consultant_v1&utm_content=affiche&utm_source_info=groupe_consultants

Autres valeurs possibles pour utm_source_info :
groupe_entrepreneurs
groupe_experts_rh
liste_diffusion
contact_individuel

Utiliser uniquement des minuscules, des chiffres et des underscores.
Ne jamais placer un nom, une adresse email ou un numéro de téléphone dans un UTM.

RAPPORT PAR AUDIENCE
--------------------
Pour obtenir les vues, démarrages, diagnostics terminés et achats par audience :

DJANGO_ENV=development python manage.py rapport_diagnostic --jours 30

Le rapport contient maintenant une section :
PAR AUDIENCE (UTM_SOURCE_INFO)

GOOGLE ANALYTICS 4
------------------
Les paramètres standards sont automatiquement reconnus par GA4.
Pour afficher utm_source_info dans les explorations GA4, créer une dimension
personnalisée de portée « Événement » avec le paramètre d'événement exact :

utm_source_info

TESTS MANUELS À EFFECTUER
-------------------------
1. Première visite privée, cache désactivé : le loader apparaît immédiatement.
2. Le formulaire KKiaPay apparaît au-dessus du loader et reste cliquable.
3. Fermeture avec la croix KKiaPay : retour au formulaire de paiement.
4. Paiement refusé : message clair et possibilité de réessayer.
5. Paiement réussi : message de vérification, puis page merci/téléchargement.
6. Diagnostic ouvert avec l'URL d'exemple : vérifier utm_source_info dans
   l'administration Django et dans rapport_diagnostic.

IMPORTANT
---------
Le prix, les clés KKiaPay et le mode sandbox/production ne sont pas modifiés
par cette archive.
