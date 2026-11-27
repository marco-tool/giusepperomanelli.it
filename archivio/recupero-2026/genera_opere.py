"""Genera le schede opera (src/content/opere/*.md) dal catalogo 2019.

- foto identiche o quasi identiche nella stessa opera: tenuta una sola (hash percettivo)
- le 6 opere già pubblicate mantengono il loro indirizzo e ricevono le foto del catalogo
- immagini ridotte a max 2000 px in src/assets/opere/<cartella>/
"""
import json, os, re, unicodedata
from PIL import Image

REPO = "/home/claude/giusepperomanelli.it"
LIB = "libreria"
OUT_IMG = f"{REPO}/src/assets/opere"
OUT_MD = f"{REPO}/src/content/opere"
MAX = 2000

opere = json.load(open("raw/catalogo-opere.json"))


def ahash(path, n=16):
    im = Image.open(path).convert("L").resize((n, n), Image.LANCZOS)
    px = list(im.get_flattened_data()) if hasattr(im, "get_flattened_data") else list(im.getdata()); m = sum(px) / len(px)
    return sum(1 << i for i, p in enumerate(px) if p > m)


def dist(a, b):
    return bin(a ^ b).count("1")


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def salva(rel):
    src = f"{LIB}/{rel}"
    dst_rel = rel.split("Opere/", 1)[1] if "Opere/" in rel else rel
    dst = f"{OUT_IMG}/{dst_rel}"
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        im = Image.open(src)
        if max(im.size) > MAX:
            im.thumbnail((MAX, MAX), Image.LANCZOS)
        if im.mode not in ("RGB", "L"):
            im = im.convert("RGB")
        im.save(dst, quality=86, optimize=True)
    return f"../../assets/opere/{dst_rel}"


# opere già pubblicate: (titolo, anno) del catalogo -> slug esistente
ESISTENTI = {  # (cartella, titolo, anno)
    ("Alabastri", "collant", "1976"): "1976-bianco-collant",
    ("Alabastri", "le amiche", "1977"): "1977-bianco-le-amiche",
    ("Alabastri", "angoscia", "1978"): "1978-a-bardiglio-angoscia",
    ("Alluminio", "spirali dialettica", "1978"): "1978-pannelli-roll-bond-alluminio-spirali-dialettica",
    ("Argento", "santa chiara", None): "argento-santa-chiara",
}


def front_esistente(slug):
    s = open(f"{OUT_MD}/{slug}.md").read()
    imgs = re.findall(r'^\s+- "([^"]+)"', s, re.M)
    return s, imgs


mancanti, scartate, usati = [], 0, set()
out = []
for o in opere:
    files = [r for r in o["immagini"] if os.path.exists(f"{LIB}/{r}")]
    mancanti += [r for r in o["immagini"] if r not in files]
    if not files:
        continue
    # deduplica dentro l'opera
    tenute, hashes = [], []
    for r in files:
        h = ahash(f"{LIB}/{r}")
        if any(dist(h, x) <= 6 for x in hashes):
            scartate += 1
            continue
        tenute.append(r); hashes.append(h)
    o["tenute"], o["hashes"] = tenute, hashes
    out.append(o)

# fusione con le opere già pubblicate
for o in out:
    key = (o["cartella"], o["title"].lower(), o["anno"])
    slug = ESISTENTI.get(key)
    if o["cartella"] == "Bassorilievi" and o["tenute"][0].endswith("P2020006-min.jpg"):
        slug = "bassorilievo-1"
    o["slug_esistente"] = slug

n_new = 0
for o in out:
    imgs = [salva(r) for r in o["tenute"]]
    if o["slug_esistente"]:
        slug = o["slug_esistente"]
        s, old = front_esistente(slug)
        # confronto percettivo con le foto già nella scheda
        old_h = [ahash(f"{REPO}/src/content/opere/{p}") for p in old]
        nuove = [p for p, h in zip(imgs, o["hashes"]) if all(dist(h, x) > 6 for x in old_h)]
        tutte = old + nuove
        s = re.sub(r"immagini: \n(  - .*\n)+", "immagini: \n" + "".join(f'  - "{p}"\n' for p in tutte), s)
        s = s.replace('materiale: ""', f'materiale: "{o["materiale"] or ""}"')
        if "fonte:" not in s:
            s = s.replace("da_completare:", 'fonte: "sito 2019 + libreria 2019"\nda_completare:')
        open(f"{OUT_MD}/{slug}.md", "w").write(s)
        usati.add(slug)
        continue
    base = "-".join(x for x in [str(o["anno"] or ""), o["materiale"] or o["cartella"], o["title"]] if x)
    slug = slugify(base)[:80].strip("-")
    k = 2
    while slug in usati or os.path.exists(f"{OUT_MD}/{slug}.md"):
        slug = f"{slugify(base)[:76]}-{k}"; k += 1
    usati.add(slug)
    anno = o["anno"]
    fm = ["---", f'title: {json.dumps(o["title"], ensure_ascii=False)}']
    if anno:
        fm.append(f"anno: {anno}" if re.fullmatch(r"\d{4}", anno) else f"anno: {json.dumps(anno, ensure_ascii=False)}")
    fm.append(f'categoria: "{o["categoria"]}"')
    if o["materiale"]:
        fm.append(f'materiale: {json.dumps(o["materiale"], ensure_ascii=False)}')
    fm.append("immagini: ")
    fm += [f'  - "{p}"' for p in imgs]
    fm.append('fonte: "libreria 2019"')
    fm.append("da_completare: true")
    fm.append("---\n")
    open(f"{OUT_MD}/{slug}.md", "w").write("\n".join(fm) + "\n")
    n_new += 1

print("opere nuove:", n_new, "| fuse con esistenti:", sorted(usati & set(ESISTENTI.values()) | ({"bassorilievo-1"} & usati)))
print("foto doppie scartate:", scartate, "| foto non ancora scaricate:", len(mancanti))
