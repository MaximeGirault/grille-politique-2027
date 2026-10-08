# Réponses enregistrées

Exemples de réponses des sources, utilisés par les tests pour repérer tout
changement de format. Les fichiers actuels sont **reconstitués** à partir de
la documentation, parce que l'environnement de développement des lots 1 et 2
n'avait pas accès à ces sites. Il faut les remplacer par de vraies réponses,
en retirant clés et jetons.

- `xmltv_tnt_extrait.xml` : guide télévision. Pour en faire un vrai, télécharger
  `https://xmltvfr.fr/xmltv/xmltv_tnt.xml.gz`, le décompresser, garder l'en-tête,
  les balises `<channel>` et une dizaine de `<programme>` des chaînes configurées,
  puis adapter les identifiants et dates attendus dans `tests/test_tv.py`.
  Prévu au lot 5, depuis les serveurs GitHub qui, eux, ont accès au site.
- `youtube_channels.json`, `twitch_token.json`, `twitch_users.json` : vérification des accès (lot 1).
- `youtube_api.json`, `twitch_api.json` : collecteurs YouTube et Twitch (lot 3).
