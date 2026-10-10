"""Sonde temporaire (lot 6) : structure HTML des communiqués de francetvpro.fr."""
import re

import requests

EN_TETES = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/17.0 Safari/605.1.15", "Accept-Language": "fr-FR,fr;q=0.9"}


def get(url):
    r = requests.get(url, headers=EN_TETES, timeout=30)
    print("=" * 100)
    print(url, "→ HTTP", r.status_code, len(r.text), "caractères")
    return r.text


h = get("https://www.francetvpro.fr/contenu-de-presse")
i = h.find("FRANC-JEU")
print("--- HTML autour du premier FRANC-JEU ---")
print(h[max(0, i - 3000): i + 2500])
print("--- liens contenant 'contenu-de-presse' (distincts) ---")
for lien in sorted(set(re.findall(r'href="([^"]*contenu-de-presse[^"]*)"', h)))[:80]:
    print(" ", lien)
print("--- rss / feed / page= ---")
for lien in sorted(set(re.findall(r'href="([^"]*(?:rss|feed|xml|page=)[^"]*)"', h)))[:30]:
    print(" ", lien)
print("--- formulaires / select ---")
for f in re.findall(r"(?is)<(?:form|select)[^>]*>", h)[:20]:
    print(" ", f[:300])
for url in ("https://www.francetvpro.fr/contenu-de-presse?page=1", "https://www.francetvpro.fr/rss.xml",
            "https://www.francetvpro.fr/contenu-de-presse/rss.xml"):
    t = get(url)
    print(t[:600] if "xml" in url else re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))[3000:4500])
