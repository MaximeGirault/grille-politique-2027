"""Sonde temporaire (lot 6) : pages d'agenda des candidats et des partis."""
import re

import requests

ADRESSES = [
    "https://actionpopulaire.fr/evenements/", "https://actionpopulaire.fr/api/evenements/rechercher/",
    "https://lafranceinsoumise.fr/agenda/", "https://melenchon.fr/agenda/",
    "https://parti-renaissance.fr/evenements", "https://parti-renaissance.fr/agenda",
    "https://rassemblementnational.fr/agenda", "https://rassemblementnational.fr/evenements",
    "https://republicains.fr/agenda", "https://republicains.fr/evenements",
    "https://horizonsleparti.fr/agenda", "https://horizonsleparti.fr/evenements",
    "https://www.parti-reconquete.fr/agenda", "https://www.parti-reconquete.fr/evenements",
    "https://www.parti-socialiste.fr/agenda", "https://placepublique.eu/agenda",
    "https://lesecologistes.fr/agenda", "https://www.pcf.fr/agenda",
    "https://www.lutte-ouvriere.org/agenda", "https://www.lutte-ouvriere.org/reunions-publiques",
    "https://www.upr.fr/agenda", "https://www.debout-la-france.fr/agenda", "https://lespatriotes.fr/agenda",
    "https://nouvelle-energie.fr/agenda", "https://www.revolutionpermanente.fr/agenda",
]
EN_TETES = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Safari/605.1.15", "Accept-Language": "fr-FR,fr;q=0.9"}
MOIS = r"(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)"

for url in ADRESSES:
    print("=" * 90)
    print(url)
    try:
        r = requests.get(url, headers=EN_TETES, timeout=25)
    except requests.RequestException as e:
        print("  ERREUR", type(e).__name__, str(e)[:150])
        continue
    h = r.text
    t = re.search(r"(?is)<title>(.*?)</title>", h)
    print(f"  HTTP {r.status_code} ; {r.headers.get('content-type')} ; {len(h)} car. ; finale {r.url}")
    print("  titre :", (t.group(1).strip()[:100] if t else "-"))
    print("  Event JSON-LD :", len(re.findall(r'"@type"\s*:\s*"Event"', h)), "; .ics/webcal :",
          sorted(set(re.findall(r'(?:href|src)="([^"]*(?:\.ics|webcal:)[^"]*)"', h)))[:5],
          "; RSS :", sorted(set(re.findall(r'href="([^"]*(?:rss|feed)[^"]*)"', h)))[:3])
    texte = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)))
    dates = re.findall(rf"(?i)\b\d{{1,2}}(?:er)?\s+{MOIS}(?:\s+20\d\d)?", texte)
    print("  dates trouvées :", len(dates), dates[:8])
    for m in list(re.finditer(rf"(?i)\b\d{{1,2}}(?:er)?\s+{MOIS}", texte))[:3]:
        print("  …", texte[max(0, m.start() - 120): m.start() + 180])
    if "json" in (r.headers.get("content-type") or ""):
        print("  JSON :", h[:800])
