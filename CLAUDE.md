# Grille politique Présidentielle 2027

Lire `CAHIER_DES_CHARGES.md`. Le projet avance lot par lot : ne réaliser que le lot
demandé, puis s'arrêter pour faire vérifier le critère « Terminé quand ».

## Consigne permanente

Écrire un test par collecteur à partir d'une réponse enregistrée de la source
(`tests/reponses/`), pour repérer tout de suite un changement de format.

## Repères

- Python 3.11 ou plus ; dépendances dans `requirements.txt` ; tests : `python -m pytest`.
- Configuration modifiable sans code : `config/chaines.yaml` (une ligne par chaîne) et `config/politique.yaml`.
- Base SQLite `data/grille.sqlite`, table unique `emissions` (`grille/db.py`). Heures en ISO 8601, fuseau Europe/Paris.
- Secrets uniquement en variables d'environnement : `YOUTUBE_API_KEY`, `TWITCH_CLIENT_ID`, `TWITCH_CLIENT_SECRET`.
- Points d'accès et quotas confirmés : `docs/VERIFICATIONS.md`.
- Code, messages et commentaires en français.
