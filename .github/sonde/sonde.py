"""Sonde temporaire (lot 6) : ce que renvoient les sites susceptibles d'annoncer les invités."""
import json
import re
import sys

import requests

ADRESSES = [
    "https://www.france.tv/france-2/franc-jeu/",
    "https://www.france.tv/france-2/franc-jeu/toutes-les-videos/",
    "https://www.francetvpro.fr/contenu-de-presse/78602613",
    "https://www.francetvpro.fr/contenu-de-presse/france-2/all",
    "https://www.francetvpro.fr/contenu-de-presse",
    "https://www.programme-tv.net/programme/chaine/programme-france-2-4.html",
    "https://www.programme-tv.net/programme/programme-tnt.html",
    "https://www.telerama.fr/tele/programmes-tv/france-2",
    "https://www.radiofrance.fr/franceinter/podcasts/franc-jeu",
]
EN_TETES = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Safari/605.1.15", "Accept-Language": "fr-FR,fr;q=0.9"}


def texte(html):
    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


for url in ADRESSES:
    print("=" * 100)
    print(url)
    try:
        r = requests.get(url, headers=EN_TETES, timeout=30)
    except requests.RequestException as e:
        print("  ERREUR", e)
        continue
    print(f"  HTTP {r.status_code} ; {r.headers.get('content-type')} ; {len(r.text)} caractères ; finale : {r.url}")
    h = r.text
    t = re.search(r"(?is)<title>(.*?)</title>", h)
    print("  titre :", t.group(1).strip() if t else "-")
    for bloc in re.findall(r'(?is)<script[^>]+application/ld\+json[^>]*>(.*?)</script>', h)[:4]:
        print("  JSON-LD :", bloc.strip()[:1500])
    for m in re.findall(r'(?i)(?:href|src)="([^"]*(?:api|json|rss|feed)[^"]*)"', h)[:15]:
        print("  lien API/RSS ?", m)
    nxt = re.search(r'(?is)<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h)
    if nxt:
        print("  __NEXT_DATA__ :", len(nxt.group(1)), "caractères ; extrait :", nxt.group(1)[:800])
    brut = texte(h)
    vus = 0
    for m in re.finditer(r"(?i)invit|franc-jeu|franc jeu|duhamel", brut):
        print("  …", brut[max(0, m.start() - 200): m.start() + 250])
        vus += 1
        if vus >= 12:
            break
sys.exit(0)
