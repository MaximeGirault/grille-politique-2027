"""Sonde temporaire (lot 6) : structure des pages d'agenda trouvées."""
import json
import re

import requests

EN_TETES = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Safari/605.1.15", "Accept-Language": "fr-FR,fr;q=0.9"}
PAGES = ["https://rassemblementnational.fr/agenda", "https://upr.fr/agenda",
         "https://horizonsleparti.fr/category/agenda/", "https://horizonsleparti.fr/categorie-evenement/evenement-du-parti/",
         "https://www.ericzemmour.fr/agenda", "https://actionpopulaire.fr/agenda/national/",
         "https://utilisateur.parti-renaissance.fr/grand-rassemblement",
         "https://utilisateur.parti-renaissance.fr/grand-rassemblement/meeting-regional-lyon",
         "https://www.lisnard2027.fr/agenda", "https://gabrielattal.fr/agenda", "https://www.edouardphilippe.fr/agenda"]
DATE = re.compile(r"(?i)\b\d{1,2}(?:er)?\s*(?:&nbsp;)?\s*(?:janv|févr|fevr|mars|avr|mai|juin|juil|août|aout|sept|oct|nov|déc|dec)")

for url in PAGES:
    print("=" * 90)
    try:
        r = requests.get(url, headers=EN_TETES, timeout=25)
    except requests.RequestException as e:
        print(url, "ERREUR", type(e).__name__, str(e)[:120])
        continue
    r.encoding = r.apparent_encoding if r.encoding in (None, "ISO-8859-1") else r.encoding
    h = r.text
    print(url, "→ HTTP", r.status_code, r.url, len(h), "car.")
    dp = re.search(r'data-page="([^"]+)"', h)
    if dp:
        import html as H
        donnees = H.unescape(dp.group(1))
        print("  data-page (Inertia) :", donnees[:3000])
    nx = re.search(r'(?is)<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', h)
    if nx:
        print("  __NEXT_DATA__ :", nx.group(1)[:3000])
    for bloc in re.findall(r'(?is)<script[^>]+application/ld\+json[^>]*>(.*?)</script>', h)[:3]:
        if "Event" in bloc:
            print("  JSON-LD Event :", bloc.strip()[:1500])
    corps = re.sub(r"(?is)<(script|style|svg|head)[^>]*>.*?</\1>", " ", h)
    m = DATE.search(corps)
    if m:
        print("  --- HTML brut autour de la première date ---")
        print(re.sub(r"\n\s*\n+", "\n", corps[max(0, m.start() - 1500): m.start() + 3500]))
    else:
        print("  aucune date ; texte :", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", corps))[:600])
