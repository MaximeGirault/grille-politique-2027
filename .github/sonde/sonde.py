"""Sonde temporaire (lot 6) : liens d'agenda depuis les pages d'accueil ; structure RN et UPR."""
import re

import requests

EN_TETES = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Safari/605.1.15", "Accept-Language": "fr-FR,fr;q=0.9"}
ACCUEILS = ["https://lafranceinsoumise.fr/", "https://melenchon.fr/", "https://parti-renaissance.fr/",
            "https://republicains.fr/", "https://horizonsleparti.fr/", "https://www.parti-reconquete.fr/",
            "https://lesecologistes.fr/", "https://www.lutte-ouvriere.org/", "https://www.debout-la-france.fr/",
            "https://www.revolutionpermanente.fr/", "https://placepublique.fr/", "https://www.placepublique.eu/",
            "https://www.les-patriotes.fr/", "https://www.francoisruffin.fr/", "https://www.parti-socialiste.fr/",
            "https://www.ensemble-ensemble.fr/", "https://www.reconquete.app/", "https://www.zemmour2027.fr/",
            "https://www.attal2027.fr/", "https://www.gabrielattal.fr/", "https://www.edouardphilippe.fr/",
            "https://www.marine2027.fr/", "https://www.retailleau2027.fr/", "https://www.melenchon2027.fr/",
            "https://www.lisnard2027.fr/", "https://www.nouvelleenergie.fr/", "https://debout.fr/"]


def get(url):
    try:
        return requests.get(url, headers=EN_TETES, timeout=20)
    except requests.RequestException as e:
        print("  ERREUR", type(e).__name__, str(e)[:120])


for url in ACCUEILS:
    print("=" * 80)
    print(url)
    r = get(url)
    if r is None:
        continue
    t = re.search(r"(?is)<title>(.*?)</title>", r.text)
    print(f"  HTTP {r.status_code} → {r.url} ; titre : {(t.group(1).strip()[:80] if t else '-')}")
    liens = sorted(set(re.findall(r'href="([^"#]*(?:agenda|evenement|événement|event|meeting|rendez-vous|rdv)[^"]*)"', r.text, re.I)))
    print("  liens agenda :", liens[:12])

for url, motif in (("https://rassemblementnational.fr/agenda", "Agenda"), ("https://upr.fr/agenda", "Voir l")):
    print("=" * 80)
    r = get(url)
    h = r.text
    i = h.find(">" + motif) if motif == "Agenda" else h.find(motif)
    print(url, "HTTP", r.status_code, "encodage", r.encoding, r.apparent_encoding, "; position", i)
    print(h[max(0, i - 2500): i + 4500])
