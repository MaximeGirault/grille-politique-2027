# Vérification des détails techniques (lot 1, 8 octobre 2026)

Le cahier des charges donne de mémoire les quotas, les points d'accès et le flux
XMLTV. Voici ce qui a été confirmé, et d'après quelle source.

Limite de l'environnement de travail : son réseau bloquait developers.google.com,
dev.twitch.tv et xmltvfr.fr. La consultation s'est donc faite par trois voies :
le document de découverte officiel de l'API YouTube, les fichiers source de
XML-TV-Fr sur GitHub, et des recherches web citant les pages officielles.
Chaque ligne indique son niveau de preuve.

## YouTube Data API v3

| Point | Constat | Source | Preuve |
| --- | --- | --- | --- |
| Quota par défaut | 10 000 unités par jour et par projet ; remise à zéro à minuit, heure du Pacifique | [Quota costs](https://developers.google.com/youtube/v3/determine_quota_cost), via recherche | Officielle, citée |
| Coût d'une lecture `list` | 1 unité (`channels`, `playlistItems`, `videos`) | idem et [Getting started](https://developers.google.com/youtube/v3/getting-started) | Officielle, citée |
| Coût de `search.list` | 100 unités, donc à éviter | idem | Officielle, citée |
| Base des appels | `https://youtube.googleapis.com/youtube/v3/` | [Document de découverte](https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest), révision 20261006 | Officielle, lue directement |
| Chaîne par pseudo `@…` | `channels.list` avec `forHandle` | idem | Officielle, lue directement |
| Playlist des vidéos mises en ligne | `contentDetails.relatedPlaylists.uploads` | idem | Officielle, lue directement |
| Directs programmés | `videos.list` avec `part=snippet,liveStreamingDetails` : `snippet.liveBroadcastContent` vaut `none`, `upcoming`, `live` ou `completed` ; `liveStreamingDetails.scheduledStartTime` est en date-heure ISO | idem ; `videos.list` accepte plusieurs `id` | Officielle, lue directement |

Méthode retenue pour le lot 3 : par chaîne, `playlistItems.list` (1 unité), puis
`videos.list` sur les nouvelles vidéos, 50 au plus par appel (1 unité). Pour
110 chaînes et 24 collectes, cela fait environ **5 280 unités par jour**, sous
la limite de 10 000. Résoudre les pseudos `@…` en identifiants (`channels.list`)
ne coûte qu'une fois par chaîne.

Point à surveiller : un direct programmé apparaît-il dans la playlist des vidéos
mises en ligne avant son début ? À vérifier au lot 3 avec une vraie clé.

## Twitch Helix

| Point | Constat | Source | Preuve |
| --- | --- | --- | --- |
| Jeton d'application | `POST https://id.twitch.tv/oauth2/token` avec `client_id`, `client_secret`, `grant_type=client_credentials` (paramètres de formulaire, pas en-têtes) | [Getting OAuth Access Tokens](https://dev.twitch.tv/docs/authentication/getting-tokens-oauth/), via recherche | Officielle, citée |
| En-têtes | `Authorization: Bearer <jeton>` et `Client-Id: <id>` | idem | Officielle, citée |
| Planning d'une chaîne | `GET https://api.twitch.tv/helix/schedule?broadcaster_id=…` ; jeton d'application accepté ; `data.segments[]` avec `start_time`, `end_time`, `title`, `canceled_until`, `is_recurring` ; par défaut, seulement les créneaux à venir | [Scheduling Broadcasts](https://dev.twitch.tv/docs/api/schedule/), via recherche | Officielle, citée |
| État « en direct » | `GET https://api.twitch.tv/helix/streams?user_login=…`, jusqu'à 100 `user_login` répétés par appel | référence de l'API, via recherche | Officielle, citée |
| Login vers identifiant | `GET https://api.twitch.tv/helix/users?login=…`, 100 au plus, paramètre répété (pas de virgules) ; avec un jeton d'application, au moins un paramètre est obligatoire | tutoriels et [forum développeurs Twitch](https://discuss.dev.twitch.tv/t/cannot-get-multiple-users/23429) | Secondaire |

Le planning demande `broadcaster_id`, pas le login : il faudra résoudre les
logins de `chaines.yaml` via `helix/users`. C'est ce que fait déjà
`verifier-acces`.

## Guide télévision XMLTV

| Point | Constat | Source | Preuve |
| --- | --- | --- | --- |
| Flux gratuit | XML TV Fr (projet libre, Apache 2.0) publie `https://xmltvfr.fr/xmltv/xmltv_tnt.xml.gz` | [dépôt racacax/XML-TV-Fr](https://github.com/racacax/XML-TV-Fr), [documentation](https://xmltvfr.fr/docs.php), [ticket 220](https://github.com/racacax/XML-TV-Fr/issues/220) | Projet, citée ; fichier non téléchargé ici |
| Horizon | Configuration par défaut : aujourd'hui + 7 jours (`fetch_policies` de 0 à 7) | `docs/configuration.md` du dépôt | Projet, lue directement |
| Identifiants de chaînes | `TF1.fr`, `France2.fr`, `France3.fr`, `France5.fr`, `M6.fr`, `Arte.fr`, `BFMTV.fr`, `CNews.fr`, `LCI.fr`, `FranceInfo.fr`, `LaChaineParlementaire.fr` (LCP et Public Sénat partagent le canal) | `resources/channel_config/channels_orange.json` et `channels_telerama.json` | Projet, lue directement |
| Solution de repli | xmltv.ch couvre aussi la TNT française, sur environ 12 jours | [linuxfr.org](https://linuxfr.org/users/vmagnin/journaux/script-pour-surveiller-les-chaines-de-la-tnt) | Secondaire |

Reste à confirmer au lot 2 : que le fichier `xmltv_tnt.xml.gz` contient bien ces
11 identifiants. Le test se lance avec `python -m grille verifier-acces` depuis
un réseau ouvert.

## Lot 2 (8 octobre 2026)

Le collecteur suit le format XMLTV standard : `<programme start stop channel>`,
dates `AAAAMMJJhhmmss ±hhmm`, balises `title`, `sub-title`, `desc`. Le site
xmltvfr.fr restait inaccessible depuis l'environnement de développement : le
contenu réel du fichier n'a pas pu être vérifié. `collecter-tv` signale toute
chaîne configurée absente du guide.

Les adresses de direct (`direct:` dans `chaines.yaml`) sont données de mémoire,
à vérifier dans un navigateur.
