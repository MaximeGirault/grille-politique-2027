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
        ("28 minutes", "Le magazine de débat d'Arte sur l'actualité.", None),  # « débat » hors du titre
        ("28 minutes", "Débat avec Raphaël Glucksmann.", ("mots-clés", "débat")),  # mais un candidat suffit
        ("Le débat de la semaine", "", ("mots-clés", "débat")),
        ("Franc-jeu", "", ("liste blanche", "analyse")),  # titre commençant par une émission de la liste
        ("Franc jeu — Gabriel Attal face à Marion Maréchal", "", ("liste blanche", "analyse")),
        ("Franchise", "", None),
        ("Face à face", "Avec un ministre", None),  # « Face à face » réservé à BFMTV
        ("Réunion publique à Saint-Ouen | Présidentielle 2027", "", ("mots-clés", "meeting")),
        ("L'heure de vérité", "Avec Édouard Philippe", ("mots-clés", "interview")),
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


def test_emission_limitee_a_une_chaine(politique):
    f, chaines = politique
    assert f.decider(chaines["BFMTV"], "Face-à-Face", "").filtre == "liste blanche"
    assert f.decider(chaines["France 5"], "Face à face avec les requins", "") is None
