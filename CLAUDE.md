# Grille politique Présidentielle 2027

Lire `CAHIER_DES_CHARGES.md`. Le projet avance lot par lot : ne réaliser que le lot
demandé, puis s'arrêter pour faire vérifier le critère « Terminé quand ».

## Consigne permanente

Écrire un test par collecteur à partir d'une réponse enregistrée de la source
(`tests/reponses/`), pour repérer tout de suite un changement de format.

## Repères

- Python 3.11 ou plus ; dépendances dans `requirements.txt` ; tests : `python -m pytest`.
- Configuration modifiable sans code : `config/chaines.yaml` (une ligne par chaîne) et `config/politique.yaml`.
- Base SQLite `data/grille.sqlite` (ignorée par Git), table `emissions`, `chaines_resolues` (identifiants YouTube), `collectes` (comptes rendus) et `envois` (emails envoyés) (`grille/db.py`). Heures en ISO 8601, fuseau Europe/Paris.
- Collecteurs : `grille/tv.py` (lot 2), `grille/youtube.py` et `grille/twitch.py` (lot 3). Filtre politique commun : `grille/filtre.py`.
- Page web (lot 4) : `grille/page.py` intègre les données dans `grille/modele_page/index.html` ; sortie dans `site/` (ignoré par Git). Aperçu : `python -m grille apercu`.
- En ligne (lot 5) : `.github/workflows/collecte.yml` (chaque heure, publie la page) et `courriel.yml` (7 h, Paris). Base sur la branche `donnees` (`.github/scripts/base.sh`), jamais dans `main`.
- Secrets en local : fichier `.env` (modèle `.env.exemple`), ignoré par Git.
- Secrets uniquement en variables d'environnement : `YOUTUBE_API_KEY`, `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`, `SMTP_SERVEUR`, `SMTP_UTILISATEUR`, `SMTP_MOT_DE_PASSE`, `EMAIL_DESTINATAIRE`, plus tard `ANTHROPIC_API_KEY`. Le dépôt est public : aucune adresse email ni clé dans les fichiers.
- Points d'accès et quotas confirmés : `docs/VERIFICATIONS.md`.
- Code, messages et commentaires en français.
