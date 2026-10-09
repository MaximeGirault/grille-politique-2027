# grille-politique-2027

Grille des émissions politiques (télévision, YouTube, Twitch, Web) jusqu'au second
tour de la présidentielle 2027. Cahier des charges : `CAHIER_DES_CHARGES.md`.

## Installation

```bash
python3 -m pip install -r requirements.txt
```

## Commandes

```bash
python3 -m grille init            # crée data/grille.sqlite si besoin et lit la configuration
python3 -m grille verifier-acces  # teste le guide XMLTV et les API YouTube et Twitch
python3 -m grille collecter-tv    # télécharge le guide TV, garde le politique, écrit en base, affiche la grille
python3 -m grille collecter-tv --motifs   # idem, avec la règle qui a retenu chaque émission
python3 -m grille collecter-youtube  # directs YouTube programmés et en cours des chaînes suivies
python3 -m grille collecter-twitch   # chaînes Twitch en direct et plannings publiés
python3 -m grille collecter       # les trois sources à la suite ; si l'une tombe, les autres continuent
python3 -m grille lister          # affiche la grille enregistrée (aujourd'hui et les 7 jours suivants)
python3 -m grille page            # génère la page web dans le dossier site/
python3 -m grille apercu          # génère la page et l'affiche sur le téléphone (même Wi-Fi)
python3 -m pytest                 # tests
```

## Voir la page sur le téléphone

Avant la mise en ligne (lot 5), le Mac peut servir la page sur le réseau Wi-Fi :

1. `python3 -m grille collecter` pour remplir la base, puis `python3 -m grille apercu`.
2. La commande affiche une adresse du type `http://192.168.1.20:8000` : l'ouvrir dans
   Safari sur l'iPhone, connecté au même Wi-Fi. Si macOS demande d'autoriser les
   connexions entrantes pour Python, accepter.
3. `Ctrl + C` dans le Terminal pour arrêter.

L'installation sur l'écran d'accueil et le mode hors connexion demandent une adresse
en HTTPS : ils fonctionneront une fois la page publiée sur GitHub Pages (lot 5).

## Clés d'API

YouTube et Twitch demandent des clés. Sur ton ordinateur, copie `.env.exemple` en
`.env` (même dossier) et remplis-le : ce fichier est ignoré par Git, il ne sera
jamais publié. Une fois en ligne (lot 5), les mêmes valeurs iront dans les secrets
GitHub.

**YouTube (`YOUTUBE_API_KEY`)**
1. console.cloud.google.com, connecté avec un compte Google ; créer un projet (« grille-politique »).
2. Menu « API et services » → « Bibliothèque » → « YouTube Data API v3 » → « Activer ».
3. « API et services » → « Identifiants » → « Créer des identifiants » → « Clé API ».
4. Conseillé : « Restreindre la clé » → restriction d'API : YouTube Data API v3 seulement.

**Twitch (`TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`)**
1. dev.twitch.tv/console, connecté avec un compte Twitch (l'authentification à deux facteurs est exigée).
2. « Enregistrer votre application » : nom libre, URL de redirection `https://localhost` (Twitch exige HTTPS ;
   elle ne sert pas ici, le champ est seulement obligatoire),
   catégorie « Other », type de client « Confidentiel ».
3. « Gérer » : copier l'identifiant client, puis « Nouveau secret » et copier le secret.

Vérification : `python3 -m grille verifier-acces` doit afficher trois `ok`.

## Ajouter une chaîne

Ouvrir `config/chaines.yaml` sur GitHub, cliquer sur le crayon, copier une ligne,
l'adapter, puis « Commit changes ».

## Régler le filtre politique

Tout se passe dans `config/politique.yaml`. Si une émission sans rapport apparaît,
`collecter-tv --motifs` montre la règle responsable : retirer ou préciser le mot-clé,
le déplacer dans `mots_cles_titre` (cherché dans le titre seulement), ou marquer le
parti `ambigu: true`. Si une émission politique manque, ajouter son
titre exact sous `liste_blanche: emissions:`.
