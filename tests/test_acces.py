"""Vérification des accès, à partir de réponses enregistrées (tests/reponses/)."""

import gzip
import io
import json
from pathlib import Path

import pytest

from grille import acces, config

REPONSES = Path(__file__).parent / "reponses"


class FausseReponse:
    def __init__(self, status_code=200, corps=b"", headers=None):
        self.status_code = status_code
        self._corps = corps
        self.text = corps.decode("utf-8", "replace") if isinstance(corps, bytes) else corps
        self.headers = headers or {}
        self.raw = io.BytesIO(corps)

    def json(self):
        return json.loads(self._corps)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FausseSession:
    def __init__(self, reponses):
        self.reponses = reponses  # url -> FausseReponse
        self.appels = []

    def _repondre(self, url, **kwargs):
        self.appels.append((url, kwargs))
        return self.reponses[url]

    get = post = _repondre


@pytest.fixture
def conf():
    return config.charger()


def test_youtube_non_configure(conf, monkeypatch):
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    assert acces.verifier_youtube(conf, FausseSession({})).etat == "non configuré"


def test_youtube_ok(conf, monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "cle")
    corps = (REPONSES / "youtube_channels.json").read_bytes()
    session = FausseSession({f"{acces.YOUTUBE_API}/channels": FausseReponse(corps=corps)})
    r = acces.verifier_youtube(conf, session)
    assert r.etat == "ok", r.detail
    assert "UUhdZt5gOhGQqVBHbw0cYVtw" in r.detail
    assert session.appels[0][1]["params"]["forHandle"] == "HugoauPerchoir"


def test_youtube_cle_refusee(conf, monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "mauvaise")
    session = FausseSession({f"{acces.YOUTUBE_API}/channels": FausseReponse(400, b'{"error": "API key not valid"}')})
    r = acces.verifier_youtube(conf, session)
    assert r.etat == "erreur" and "400" in r.detail


def test_twitch_ok_signale_les_comptes_introuvables(conf, monkeypatch):
    monkeypatch.setenv("TWITCH_CLIENT_ID", "id")
    monkeypatch.setenv("TWITCH_CLIENT_SECRET", "secret")
    session = FausseSession({
        acces.TWITCH_TOKEN: FausseReponse(corps=(REPONSES / "twitch_token.json").read_bytes()),
        f"{acces.TWITCH_API}/users": FausseReponse(corps=(REPONSES / "twitch_users.json").read_bytes()),
    })
    r = acces.verifier_twitch(conf, session)
    assert r.etat == "ok", r.detail
    nb_twitch = sum(c.plateforme == "twitch" for c in conf.chaines)
    assert f"2/{nb_twitch}" in r.detail and "mediapart" in r.detail
    en_tetes = session.appels[1][1]["headers"]
    assert en_tetes == {"Authorization": "Bearer jeton-de-test", "Client-Id": "id"}


def test_xmltv_ok():
    corps = gzip.compress((REPONSES / "xmltv_extrait.xml").read_bytes())
    session = FausseSession({acces.XMLTV_TNT: FausseReponse(corps=corps, headers={"Last-Modified": "hier"})})
    assert acces.verifier_xmltv(session).etat == "ok"


def test_xmltv_page_html_au_lieu_du_guide():
    session = FausseSession({acces.XMLTV_TNT: FausseReponse(corps=b"<html>maintenance</html>")})
    r = acces.verifier_xmltv(session)
    assert r.etat == "erreur" and "gzip" in r.detail


def test_estimation_quota_sous_la_limite(conf):
    nb = sum(1 for c in conf.chaines if c.plateforme == "youtube")
    assert acces.estimer_quota_youtube(nb) < acces.YOUTUBE_QUOTA_JOUR
