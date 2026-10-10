import sqlite3

import pytest

from grille import db


def test_ouvrir_cree_une_base_vide_et_reste_idempotent(tmp_path):
    chemin = tmp_path / "sous-dossier" / "grille.sqlite"
    db.ouvrir(chemin).close()
    connexion = db.ouvrir(chemin)
    colonnes = [ligne[1] for ligne in connexion.execute("PRAGMA table_info(emissions)")]
    assert colonnes == [
        "id", "titre", "debut", "fin", "plateforme", "chaine", "categorie",
        "invites", "lien", "statut", "filtre", "vu_le",
    ]
    assert connexion.execute("SELECT COUNT(*) FROM emissions").fetchone()[0] == 0
    assert connexion.execute("PRAGMA user_version").fetchone()[0] == db.VERSION_SCHEMA


def test_valeurs_hors_liste_refusees(tmp_path):
    connexion = db.ouvrir(tmp_path / "g.sqlite")
    with pytest.raises(sqlite3.IntegrityError):
        connexion.execute(
            "INSERT INTO emissions (id, titre, debut, plateforme, chaine, vu_le) VALUES (?, ?, ?, ?, ?, ?)",
            ("fax:1", "x", "2027-03-15T21:00:00+01:00", "fax", "x", "2027-03-15T20:00:00+01:00"),
        )
