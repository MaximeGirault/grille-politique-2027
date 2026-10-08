"""Base SQLite : une table `emissions`, une ligne par diffusion.

Conventions de stockage :
- `debut`, `fin`, `vu_le` : texte ISO 8601 avec décalage, fuseau Europe/Paris
  (ex. 2027-03-15T21:00:00+01:00) ; `fin` peut être NULL.
- `invites` et `lien` : listes JSON, pour qu'une émission fusionnée porte
  plusieurs liens (télévision + YouTube, par exemple).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

CHEMIN_BASE = Path(__file__).resolve().parent.parent / "data" / "grille.sqlite"
VERSION_SCHEMA = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS emissions (
    id          TEXT PRIMARY KEY,                 -- source:identifiant d'origine, ex. youtube:abc123
    titre       TEXT NOT NULL,
    debut       TEXT NOT NULL,
    fin         TEXT,
    plateforme  TEXT NOT NULL CHECK (plateforme IN ('tv', 'youtube', 'twitch', 'web')),
    chaine      TEXT NOT NULL,
    categorie   TEXT CHECK (categorie IN ('débat', 'interview', 'meeting', 'analyse')),
    invites     TEXT NOT NULL DEFAULT '[]',
    lien        TEXT NOT NULL DEFAULT '[]',
    statut      TEXT NOT NULL DEFAULT 'annoncé'
                CHECK (statut IN ('annoncé', 'en direct', 'terminé', 'annulé')),
    filtre      TEXT CHECK (filtre IN ('liste blanche', 'mots-clés', 'modèle')),
    vu_le       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS emissions_debut ON emissions (debut);
"""


def ouvrir(chemin: Path = CHEMIN_BASE) -> sqlite3.Connection:
    """Ouvre la base et crée la table si besoin (sans effacer l'existant)."""
    chemin.parent.mkdir(parents=True, exist_ok=True)
    connexion = sqlite3.connect(chemin)
    connexion.executescript(SCHEMA)
    connexion.execute(f"PRAGMA user_version = {VERSION_SCHEMA}")
    connexion.commit()
    return connexion


def enregistrer_collecte(
    connexion: sqlite3.Connection,
    emissions: list[dict],
    plateforme: str,
    chaines_couvertes: set[str],
    maintenant: datetime,
) -> int:
    """Écrit les émissions d'une collecte et renvoie le nombre d'émissions passées en « annulé ».

    Une émission déjà connue (même id) est mise à jour, pas recréée. Une émission
    à venir, d'une chaîne couverte par cette collecte, qui n'a pas été revue passe
    en « annulé ». Les chaînes absentes de la source ne sont pas touchées : une
    panne de source ne doit pas tout annuler.
    """
    vu_le = maintenant.isoformat(timespec="seconds")
    for e in emissions:
        connexion.execute(
            """
            INSERT INTO emissions (id, titre, debut, fin, plateforme, chaine, categorie, invites, lien, statut, filtre, vu_le)
            VALUES (:id, :titre, :debut, :fin, :plateforme, :chaine, :categorie, :invites, :lien, :statut, :filtre, :vu_le)
            ON CONFLICT (id) DO UPDATE SET
                titre = excluded.titre, debut = excluded.debut, fin = excluded.fin, chaine = excluded.chaine,
                categorie = excluded.categorie, invites = excluded.invites, lien = excluded.lien,
                statut = excluded.statut, filtre = excluded.filtre, vu_le = excluded.vu_le
            """,
            {**e, "invites": json.dumps(e["invites"], ensure_ascii=False),
             "lien": json.dumps(e["lien"], ensure_ascii=False), "vu_le": vu_le},
        )
    ids_vus = {e["id"] for e in emissions}
    annulees = [
        id_
        for id_, debut, chaine in connexion.execute(
            "SELECT id, debut, chaine FROM emissions WHERE plateforme = ? AND statut != 'annulé'", (plateforme,)
        )
        if id_ not in ids_vus and chaine in chaines_couvertes and datetime.fromisoformat(debut) > maintenant
    ]
    connexion.executemany("UPDATE emissions SET statut = 'annulé', vu_le = ? WHERE id = ?", [(vu_le, i) for i in annulees])
    connexion.commit()
    return len(annulees)


def lister(connexion: sqlite3.Connection, depuis: datetime, jusqua: datetime) -> list[dict]:
    """Émissions non annulées qui se terminent après `depuis` et commencent avant `jusqua`, par heure de début."""
    connexion.row_factory = sqlite3.Row
    lignes = [dict(r) for r in connexion.execute("SELECT * FROM emissions WHERE statut != 'annulé'")]
    connexion.row_factory = None
    resultat = []
    for e in lignes:
        debut = datetime.fromisoformat(e["debut"])
        fin = datetime.fromisoformat(e["fin"]) if e["fin"] else debut
        if fin > depuis and debut < jusqua:
            e["invites"], e["lien"] = json.loads(e["invites"]), json.loads(e["lien"])
            resultat.append(e)
    return sorted(resultat, key=lambda e: (datetime.fromisoformat(e["debut"]), e["chaine"]))
