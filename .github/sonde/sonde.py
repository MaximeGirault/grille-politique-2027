"""Sonde temporaire (lot 6) : HTML brut des agendas RN, UPR et Édouard Philippe."""
import re

import requests

EN_TETES = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Safari/605.1.15", "Accept-Language": "fr-FR,fr;q=0.9"}
for url, reperes in (("https://rassemblementnational.fr/agenda", ["Kotarac", "Chenu"]),
                     ("https://upr.fr/agenda", ["Villefagnan", "Voir l"]),
                     ("https://www.edouardphilippe.fr/agenda", ["Aucun"])):
    r = requests.get(url, headers=EN_TETES, timeout=25)
    r.encoding = "utf-8"
    h = r.text
    print("=" * 90)
    print(url, r.status_code, len(h))
    for repere in reperes:
        positions = [m.start() for m in re.finditer(re.escape(repere), h)]
        print(f"--- « {repere} » trouvé {len(positions)} fois ; HTML autour de la première occurrence ---")
        if positions:
            i = positions[0]
            print(re.sub(r"\n\s*\n+", "\n", h[max(0, i - 3000): i + 3000]))
