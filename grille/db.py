"""Base SQLite : une table `emissions`, une ligne par diffusion.

Conventions de stockage :
- `debut`, `fin`, `vu_le` : texte ISO 8601 avec décalage, fuseau Europe/Paris
  (ex. 2027-03-15T21:00:00+01:00) ; `fin` peut être NULL.
- `invites` et `lien` : listes JSON, pour qu'une émission fusionnée porte
  plusieurs liens (télévision + YouTube, par exemple).
"""

from __future__ import annotations

import sqlite3
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
