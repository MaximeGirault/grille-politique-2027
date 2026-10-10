"""Sonde temporaire (lot 6) : collecteur d'annonces sur le vrai site, et cartes lues page par page."""
import subprocess
import sys

import requests

from grille import annonces, config
from grille.acces import FRANCETVPRO
from grille.filtre import FiltrePolitique
from grille.tv import EN_TETES, PARIS
from datetime import datetime

filtre = FiltrePolitique(config.charger())
aujourdhui = datetime.now(PARIS).date()
for page in range(4):
    h = requests.get(FRANCETVPRO, params={"page": page}, headers=EN_TETES, timeout=30).text
    print(f"--- page {page} : {h.count('card__title')} titres de carte dans le HTML")
    for m in annonces._CARTE.finditer(h):
        parties = [annonces._texte(x) for x in m["titre"].replace("<br>", "\n").split("\n")]
        print("  ", " / ".join(p for p in parties if p)[:90], "|", annonces._texte(m["date"])[:70],
              "|", annonces.lire_date(annonces._texte(m["date"]), aujourdhui) if m["date"] else None)
sys.stdout.flush()
subprocess.run([sys.executable, "-m", "grille", "--base", "/tmp/sonde.sqlite", "collecter-annonces"])
