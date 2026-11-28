"""Adatta la build (dist/) per l'anteprima su GitHub Pages, servita in una sottocartella.

- prefissa con BASE tutti gli indirizzi interni che iniziano con "/" (href, src, srcset, url() nei CSS)
- aggiunge <meta name="robots" content="noindex"> per non far indicizzare l'anteprima
- aggiunge una fascia "Anteprima" in cima a ogni pagina
Uso: python3 scripts/anteprima.py /giusepperomanelli.it
"""
import pathlib, re, sys

BASE = sys.argv[1].rstrip("/")
DIST = pathlib.Path("dist")


def pref(u: str) -> str:
    if u.startswith("/") and not u.startswith("//") and not u.startswith(BASE + "/"):
        return BASE + u
    return u


FASCIA = (
    '<div style="background:#17223a;color:#f4f1ea;font:14px/1.4 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;'
    'padding:8px 16px;text-align:center">Anteprima del nuovo sito giusepperomanelli.it: non ancora online</div>'
)

n = 0
for f in DIST.rglob("*.html"):
    s = f.read_text(encoding="utf-8")
    s = re.sub(r'(\s(?:href|src|action|content)=")(/[^"]*)"', lambda m: m.group(1) + pref(m.group(2)) + '"', s)
    s = re.sub(r'srcset="([^"]*)"', lambda m: 'srcset="' + ", ".join(
        " ".join([pref(p.split()[0])] + p.split()[1:]) for p in m.group(1).split(",") if p.strip()) + '"', s)
    s = s.replace("<head>", '<head><meta name="robots" content="noindex, nofollow">', 1)
    s = re.sub(r"(<body[^>]*>)", r"\1" + FASCIA, s, count=1)
    f.write_text(s, encoding="utf-8"); n += 1
for f in DIST.rglob("*.css"):
    s = f.read_text(encoding="utf-8")
    s = re.sub(r"url\((['\"]?)(/[^)'\"]*)\1\)", lambda m: f"url({m.group(1)}{pref(m.group(2))}{m.group(1)})", s)
    f.write_text(s, encoding="utf-8")
(DIST / ".htaccess").unlink(missing_ok=True)
(DIST / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
print(f"anteprima: {n} pagine adattate a {BASE}/")
