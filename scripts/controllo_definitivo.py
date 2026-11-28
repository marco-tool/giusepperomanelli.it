"""Controlli sulla build (dist/) prima di pubblicare il sito definitivo su www.giusepperomanelli.it.

Gira su ogni build, anche in modalità anteprima, così un errore si vede prima del passaggio di dominio.
Esce con errore se:
  - una pagina ha noindex o contiene indirizzi dell'anteprima (marco-tool.github.io)
  - robots.txt blocca i motori o non indica la sitemap del dominio
  - un canonical o og:url non è sul dominio definitivo
  - un collegamento interno (href, src, srcset, rimandi) porta a un file che non esiste
  - la build supera 900 MB (il limite di GitHub Pages è 1 GB)
Uso: python3 scripts/controllo_definitivo.py
"""
import json, pathlib, re, sys
from urllib.parse import unquote

DIST = pathlib.Path("dist")
SITO = "https://www.giusepperomanelli.it"
errori = []


def esiste(u: str) -> bool:
    u = unquote(u.split("#")[0].split("?")[0])
    if not u.startswith("/") or u.startswith("//"):
        return True
    p = DIST / u.lstrip("/")
    return p.is_file() or (p / "index.html").is_file()


pagine = list(DIST.rglob("*.html"))
rimandi = 0
for f in pagine:
    s = f.read_text(encoding="utf-8")
    rel = "/" + str(f.parent.relative_to(DIST)).replace("\\", "/") + "/"
    if 'http-equiv="refresh"' in s:
        rimandi += 1
    if re.search(r'name="robots"[^>]*noindex', s):
        errori.append(f"{rel}: noindex")
    if "marco-tool.github.io" in s:
        errori.append(f"{rel}: indirizzo dell'anteprima")
    for m in re.finditer(r'<link rel="canonical" href="([^"]+)"|property="og:url" content="([^"]+)"', s):
        u = m.group(1) or m.group(2)
        if not u.startswith(SITO + "/"):
            errori.append(f"{rel}: canonical/og:url fuori dominio {u}")
    link = re.findall(r'\s(?:href|src)="(/[^"]*)"', s)
    link += [p.strip().split()[0] for v in re.findall(r'srcset="([^"]*)"', s) for p in v.split(",") if p.strip()]
    link += re.findall(r'content="\d+;\s*url=(/[^"]*)"', s)
    for u in link:
        if not esiste(u):
            errori.append(f"{rel}: collegamento interno rotto {u}")

robots = (DIST / "robots.txt").read_text() if (DIST / "robots.txt").exists() else ""
if re.search(r"^Disallow:\s*/\s*$", robots, re.M) or f"Sitemap: {SITO}/sitemap-index.xml" not in robots:
    errori.append("robots.txt non adatto al sito definitivo")
if not (DIST / "sitemap-index.xml").exists():
    errori.append("manca la sitemap")
if not (DIST / "404.html").exists():
    errori.append("manca 404.html")
attesi = len(json.loads(pathlib.Path("src/rimandi.json").read_text(encoding="utf-8")))
if rimandi < attesi * 0.95:
    errori.append(f"pagine di rimando: {rimandi}, attese circa {attesi}")
mb = sum(p.stat().st_size for p in DIST.rglob("*") if p.is_file()) / 1e6
if mb > 900:
    errori.append(f"build di {mb:.0f} MB, troppo vicina al limite di 1 GB")

print(f"controllo: {len(pagine)} pagine HTML ({rimandi} di rimando), {mb:.0f} MB")
if errori:
    print(f"{len(errori)} problemi:")
    for e in errori[:60]:
        print(" -", e)
    sys.exit(1)
print("ok: pronto per www.giusepperomanelli.it")
