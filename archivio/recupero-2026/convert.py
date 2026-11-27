"""Converte l'HTML scaricato in contenuti Markdown per il sito Astro."""
import json, re, os
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from PIL import Image

SITE = "site"
ASSETS = f"{SITE}/src/assets/uploads"
SIZE = re.compile(r"-\d+x\d+(?=\.(jpe?g|png|gif)$)", re.I)
MAX = 2000

def full(url):
    return SIZE.sub("", url.replace("http://", "https://").split("?")[0])

def local_img(url):
    rel = full(url).split("/wp-content/uploads/")[1]
    src, dst = f"img/{rel}", f"{ASSETS}/{rel}"
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = Image.open(src)
        if max(im.size) > MAX:
            im.thumbnail((MAX, MAX), Image.LANCZOS)
        if im.mode in ("RGBA", "P") and dst.lower().endswith((".jpg", ".jpeg")):
            im = im.convert("RGB")
        kw = {"quality": 86, "optimize": True} if dst.lower().endswith((".jpg", ".jpeg")) else {}
        im.save(dst, **kw)
    return f"../../assets/uploads/{rel}"

def content_el(slug):
    soup = BeautifulSoup(open(f"html/{slug}.html", errors="ignore").read(), "html.parser")
    c = soup.select_one("#content")
    for bad in c.select("script, style, nav, .portfolio-header, .portfolio-filters, .portfolio, footer, form"):
        bad.decompose()
    for a in c.find_all("a"):
        h = a.get("href", "")
        # tolgo solo i link che avvolgono un'immagine o puntano a un file immagine
        if a.find("img") or re.search(r"\.(jpe?g|png|gif)$", h, re.I) or not h:
            a.unwrap()
            continue
        # link interni: da assoluti a relativi alla radice del sito
        h = re.sub(r"^https?://(www\.)?giusepperomanelli\.it", "", h)
        a.attrs = {"href": h or "/"}
    for img in c.find_all("img"):
        src = img.get("src") or ""
        if "/wp-content/uploads/" in src:
            img["src"] = local_img(src)
            for k in ["srcset", "sizes", "class", "width", "height", "style"]:
                img.attrs.pop(k, None)
        else:
            img.decompose()
    return c

def to_md(c, drop_titles=()):
    t = md(str(c), heading_style="ATX", bullets="-")
    t = t.replace("\xa0", " ")
    t = re.sub(r"^(Ingrandire|Vai all'opera)\s*$", "", t, flags=re.M)
    lines = t.split("\n")
    out = []
    for ln in lines:
        s = re.sub(r"^#+\s*", "", ln).strip()
        if ln.startswith("#") and s.lower() in [d.lower() for d in drop_titles]:
            continue
        out.append(ln.rstrip())
    t = "\n".join(out)
    t = re.sub(r"\n\s*\n+", "\n\n", t).strip()
    return t + "\n"

def fm(d):
    def q(v):
        if isinstance(v, bool) or isinstance(v, (int, float)):
            return str(v).lower() if isinstance(v, bool) else str(v)
        if isinstance(v, list):
            return "\n" + "\n".join(f"  - {json.dumps(x, ensure_ascii=False)}" for x in v)
        return json.dumps(v, ensure_ascii=False)
    return "---\n" + "\n".join(f"{k}: {q(v)}" for k, v in d.items()) + "\n---\n\n"

def write(path, front, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(fm(front) + body)

# --- Pagine fisse
pagine = {
    "home-4": ("home", "Giuseppe Romanelli"),
    "biografia": ("biografia", "Biografia"),
    "curriculum": ("curriculum", "Curriculum"),
    "opere-pubbliche": ("opere-pubbliche", "Opere pubbliche"),
    "contatti": ("contatti", "Contatti"),
    "credits": ("credits", "Credits"),
}
for slug, (name, title) in pagine.items():
    c = content_el(slug)
    body = to_md(c, drop_titles=[title, "Biografia", "Curriculum", "OPERE PUBBLICHE", "Contatti", "Credits", "Mostre"])
    if name == "home":
        body = re.split(r"\n\n\[?Alabastri", body)[0]
        body = re.sub(r"^- !\[.*$\n?", "", body, flags=re.M)          # immagini dello slider
        body = re.sub(r"^## L.artista\s*$", "", body, flags=re.M)
        body = re.sub(r"Maggiori dettagli sono disponibili nella sezione \[?Biografia(\]\([^)]*\))?\.", "[Leggi la biografia completa →](/biografia/)", body)
        body = re.sub(r"\n\s*\n+", "\n\n", body).strip() + "\n"
    write(f"{SITE}/src/content/pagine/{name}.md", {"title": title}, body)

# --- Mostre: elenco completo dalla pagina Mostre, dettaglio dove esiste
elenco = [
    ("1963-10-05", "1963, dal 5 al 18 ottobre", "Venezia", "1963-dal-5-al-18-ottobre"),
    ("1964-03-14", "1964, dal 14 al 26 marzo", "Brescia", "1964-14-26-marzo"),
    ("1967-09-10", "1967, dal 10 settembre al 10 ottobre", "Venezia", "1967-dal-10-settembre-al-10-ottobre"),
    ("1968-08-03", "1968, dal 3 al 23 agosto", "Lido di Jesolo (Venezia)", "1968-dal-3-al-23-agosto"),
    ("1969-05-18", "1969, dal 18 al 29 maggio", "Bologna", "1969-dal-18-al-29-maggio"),
    ("1969-12-31", "1969, Istituto Federale delle Casse di Risparmio delle Venezie", "", "1969-istituto-federale-delle-casse-di-risparmio-delle-venezie"),
    ("1970-06-13", "1970, dal 13 al 30 giugno", "Rovereto", "1970-dal-13-al-30-giugno"),
    ("1970-08-22", "1970, dal 22 al 28 agosto", "Folgaria (Trento)", "1970-dal-22-al-28-agosto"),
    ("1970-09-19", "1970, dal 19 settembre al 2 ottobre", "Venezia", "1970-dal-19-sett-al-2-ottobre"),
    ("1970-12-19", "1970, dal 19 dicembre al 4 gennaio", "Padova", "1970-dal-19-dicembre-al-4-gennaio"),
    ("1973-02-24", "1973, dal 24 febbraio", "Venezia", "1973-dal-24-febbraio"),
    ("1974-05-16", "1974, dal 16 al 26 maggio", "Roma", "1974-dal-16-al-26-maggio"),
    ("1975-11-17", "1975, dal 17 novembre al 13 dicembre", "Austria", "1975-dal-17-novembre-al-13-dicembre"),
    ("1976-02-07", "1976, 7 febbraio", "Klagenfurt (Austria)", None),
    ("1977-07-04", "1977, dal 4 al 28 luglio", "Klagenfurt (Austria)", None),
    ("1978-05-18", "1978, dal 18 maggio al 15 luglio", "Venezia", None),
    ("1980-03-14", "1980, 14 marzo", "Venezia", None),
    ("1980-09-01", "1980, dal 1 settembre al 5 ottobre", "Venezia", None),
    ("1982-03-30", "1982, dal 30 marzo al 10 aprile", "Austria", None),
]
for data, titolo, citta, slug in elenco:
    body, cover = "", None
    if slug:
        c = content_el(slug)
        body = to_md(c, drop_titles=[titolo, json.load(open("raw/extracted.json"))[slug]["title"].split(" | ")[0]])
        m = re.search(r"!\[[^\]]*\]\(([^)\s]+)", body)
        cover = m.group(1) if m else None
    front = {"title": titolo, "slug": slug or data, "data": data, "luogo": citta}
    if cover:
        front["copertina"] = cover
    write(f"{SITE}/src/content/mostre/{data}.md", front, body)

def pulisci_mostre(t):
    t = re.split(r"\n- \[?1963", t)[0]
    # "[XXIII](u)[Biennale di Venezia](u)" -> un solo link
    t = re.sub(r"\[([XVI]+)\]\(([^)]+)\)\s*\[Biennale di Venezia\]\(\2\)", r"[\1 Biennale di Venezia](\2)", t)
    t = re.sub(r"(\)),\s*$", r"\1", t, flags=re.M)  # virgole finali nell'elenco
    return t.strip() + "\n"

# Biennali e Quadriennali: solo elenco, nessun materiale
open(f"{SITE}/src/content/pagine/mostre.md", "w").write(fm({"title": "Mostre"}) + pulisci_mostre(to_md(content_el("mostre"), ["Mostre"])))

# --- Opere
ext = json.load(open("raw/extracted.json"))
alab = {i["url"] for i in ext["alabastri"]["images"]}
opere = {
    "1976-bianco-collant": ("Collant", 1976, "Alabastro bianco"),
    "1977-bianco-le-amiche": ("Le amiche", 1977, "Alabastro bianco"),
    "1978-a-bardiglio-angoscia": ("Angoscia", 1978, "Alabastro bardiglio"),
    "1978-pannelli-roll-bond-alluminio-spirali-dialettica": ("Spirali dialettica", 1978, "Pannelli roll-bond in alluminio"),
    "argento-santa-chiara": ("Santa Chiara", None, "Argento"),
    "bassorilievo-1": ("Bassorilievo", None, ""),
}
for slug, (titolo, anno, materiale) in opere.items():
    imgs = [i["url"] for i in ext[f"opera/{slug}"]["images"]]
    # la prima immagine è l'opera; le successive sono miniature di "Altre opere"
    main = imgs[:1]
    if slug in ("1978-a-bardiglio-angoscia", "bassorilievo-1"):
        main = imgs[:2]
    cat = "alabastri" if any(u in alab for u in imgs[:1]) or "Alabastro" in materiale else "altri-materiali"
    front = {"title": titolo, "categoria": cat, "materiale": materiale, "immagini": [local_img(u) for u in main], "da_completare": True}
    if anno:
        front = {"title": titolo, "anno": anno, **{k: v for k, v in front.items() if k != "title"}}
    write(f"{SITE}/src/content/opere/{slug}.md", front, "")
print("ok")

# Curriculum: la foto iniziale era attaccata al primo paragrafo
p = f"{SITE}/src/content/pagine/curriculum.md"
s = open(p).read()
s = re.sub(r"(!\[\]\(([^)]+IMG_0006-1\.jpg)\))", r"![Giuseppe Romanelli](\2)\n\n", s, count=1)
open(p, "w").write(s)
