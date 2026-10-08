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
python3 -m pytest                 # tests
```

`verifier-acces` lit ces variables d'environnement (secrets GitHub une fois en ligne) :

| Variable | Où l'obtenir |
| --- | --- |
| `YOUTUBE_API_KEY` | Google Cloud Console : créer un projet, activer « YouTube Data API v3 », créer une clé d'API |
| `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET` | dev.twitch.tv/console : enregistrer une application (catégorie « Other », adresse de redirection `http://localhost`) |

## Ajouter une chaîne

Ouvrir `config/chaines.yaml` sur GitHub, cliquer sur le crayon, copier une ligne,
l'adapter, puis « Commit changes ».
