import pytest

from grille import config, filtre


@pytest.fixture(scope="module")
def politique():
    conf = config.charger()
    chaines = {c.nom: c for c in conf.chaines}
    return filtre.FiltrePolitique(conf), chaines


def test_normaliser():
    assert filtre.normaliser("  L'Élysée : DÉBAT d'entre-deux-tours ! ") == "l elysee debat d entre deux tours"


@pytest.mark.parametrize(
    "titre, description, attendu",
    [
        ("Les quatre vérités", "", ("liste blanche", "interview")),
        ("Soirée électorale", "Résultats du second tour", ("mots-clés", "analyse")),
        ("Le grand entretien", "Avec Marine Tondelier", ("mots-clés", "interview")),
        ("Météo", "", None),
        ("Élection de Miss France 2027", "", None),
        ("Les Horizons perdus", "Film d'aventure", None),  # parti ambigu
        ("Attalens, village suisse", "", None),  # « Attal » seulement en mot entier
    ],
)
def test_decider(politique, titre, description, attendu):
    f, chaines = politique
    decision = f.decider(chaines["France 2"], titre, description)
    assert (decision and (decision.filtre, decision.categorie)) == attendu or (attendu is None and decision is None)


def test_chaine_de_parti_toujours_retenue(politique):
    f, chaines = politique
    decision = f.decider(chaines["Rassemblement National"], "Vlog du dimanche", "")
    assert decision.filtre == "liste blanche"
