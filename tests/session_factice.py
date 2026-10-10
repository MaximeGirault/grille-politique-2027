"""Fausse session HTTP : rejoue des réponses enregistrées selon l'URL et les paramètres."""

import json
from pathlib import Path

REPONSES = Path(__file__).parent / "reponses"


class Reponse:
    def __init__(self, status_code=200, corps=None):
        self.status_code = status_code
        self._corps = corps if corps is not None else {}
        self.text = json.dumps(self._corps)

    def json(self):
        return self._corps

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"HTTP {self.status_code}")


def charger(nom: str) -> dict:
    return json.loads((REPONSES / nom).read_text(encoding="utf-8"))


class Session:
    """`routeur(methode, url, params)` renvoie une Reponse ; chaque appel est noté dans `appels`."""

    def __init__(self, routeur):
        self.routeur = routeur
        self.appels = []

    def get(self, url, params=None, **kwargs):
        self.appels.append(("GET", url, params))
        return self.routeur("GET", url, params)

    def post(self, url, data=None, json=None, **kwargs):
        corps = data if json is None else json  # formulaire (Twitch) ou JSON (GraphQL Radio France)
        self.appels.append(("POST", url, corps))
        return self.routeur("POST", url, corps)
