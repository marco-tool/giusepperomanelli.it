"""Ricostruisce gli indirizzi pubblici del vecchio WordPress e li confronta con il nuovo sito.

Legge l'export del database (Sql1247568_1.sql, che resta sul PC di Marco: contiene dati
riservati e NON va nel repository) e la build in dist/.
Scrive:
  - src/rimandi.json: vecchio indirizzo -> nuovo indirizzo, per le pagine di rimando generate in build
  - archivio/recupero-2026/vecchi-indirizzi.csv: tutti i vecchi indirizzi con l'esito
Uso: python3 scripts/vecchi_indirizzi.py /percorso/dump.sql
"""
import csv, json, pathlib, re, sys, unicodedata

DUMP = pathlib.Path(sys.argv[1])
ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
CONTENT = ROOT / "src" / "content"


# --- lettura del dump (INSERT di phpMyAdmin) ---
def tuples(values):
    i, n, rows, depth = 0, len(values), [], 0
    row, cur = [], None
    while i < n:
        c = values[i]
        if c == "'":
            j, buf = i + 1, []
            while True:
                d = values[j]
                if d == "\\":
                    buf.append(values[j + 1]); j += 2; continue
                if d == "'":
                    if j + 1 < n and values[j + 1] == "'":
                        buf.append("'"); j += 2; continue
                    break
                buf.append(d); j += 1
            cur = "".join(buf); i = j + 1; continue
        if c == "(" and depth == 0:
            depth, row, cur = 1, [], None; i += 1; continue
        if depth == 1 and c == ",":
            row.append(cur); cur = None; i += 1; continue
        if depth == 1 and c == ")":
            row.append(cur); rows.append(row); depth = 0; i += 1; continue
        if depth == 1 and not c.isspace():
            m = re.match(r"[^,)]+", values[i:]); tok = m.group(0).strip()
            cur = None if tok == "NULL" else tok; i += len(m.group(0)); continue
        i += 1
    return rows


sql = DUMP.read_text(encoding="utf-8", errors="replace")
tab, col = {}, {}
for m in re.finditer(r"INSERT INTO `(\w+)` \(([^)]*)\) VALUES\s*(.*?);\n(?=\n|--|INSERT|/\*|COMMIT|ALTER|CREATE)", sql, re.S):
    t = m.group(1)
    col[t] = [c.strip(" `") for c in m.group(2).split(",")]
    tab.setdefault(t, []).extend(tuples(m.group(3)))
rows = lambda t: [dict(zip(col[t], r)) for r in tab.get(t, [])]
P = {p["ID"]: p for p in rows("wp8q_posts")}
META = {}
for m in rows("wp8q_postmeta"):
    META.setdefault(m["post_id"], {})[m["meta_key"]] = m["meta_value"]


def esiste(u):
    return (DIST / u.strip("/") / "index.html").exists() if u != "/" else True


def norm(s):
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch)).lower()


# --- indirizzi delle pagine del vecchio sito ---
def page_path(p):
    parts, q = [], p
    while q:
        parts.append(q["post_name"])
        q = P.get(q["post_parent"]) if q["post_parent"] not in ("0", None) else None
    return "/" + "/".join(reversed(parts)) + "/"


CPT_BASE = {"oxy_portfolio_image": "opera"}  # dalle rewrite_rules del vecchio tema


def permalink(p):
    if p["post_type"] == "page":
        return page_path(p)
    if p["post_type"] in CPT_BASE:
        return f"/{CPT_BASE[p['post_type']]}/{p['post_name']}/"
    return None


# --- dove compare ogni immagine nel nuovo sito ---
def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    return m.group(1) if m else ""


dove = {}  # nome file normalizzato -> nuovo indirizzo (le schede opera hanno la precedenza)
for sezione, base in (("pagine", ""), ("mostre", "/mostre"), ("opere", "/opera")):
    for f in sorted((CONTENT / sezione).glob("*.md")):
        t = f.read_text(encoding="utf-8")
        fm = frontmatter(t)
        m = re.search(r'^slug:\s*"?([^"\n]+)"?', fm, re.M)
        sid = m.group(1) if m else f.stem
        if sezione == "pagine":
            url = "/" if sid == "home" else f"/{sid}/"
        else:
            url = f"{base}/{sid}/"
        if not esiste(url):
            continue
        for img in re.findall(r"[\w\-.() %àèéìòù]+\.(?:jpe?g|png|gif|webp)", t, re.I):
            k = norm(img)
            if sezione == "opere" or k not in dove:
                dove[k] = url

# doppioni già classificati nella contabilità della libreria ("stessa immagine di X")
for r in csv.DictReader((ROOT / "archivio" / "recupero-2026" / "contabilita-libreria.csv").open(encoding="utf-8")):
    m = re.search(r"(?:stessa immagine di|ritaglio quadrato .* da|versione ritagliata di|originale non ritagliato .* \()\s*([^\s:()]+\.(?:jpe?g|png))", r["motivo"])
    if m and norm(pathlib.Path(r["file"]).name) not in dove and norm(pathlib.Path(m.group(1)).name) in dove:
        dove[norm(pathlib.Path(r["file"]).name)] = dove[norm(pathlib.Path(m.group(1)).name)]
SPECIALI = {"giuseppe-romanelli.jpg": "/", "giuseppe-romanelli-opere.jpg": "/opere/", "giuseppe-romanelli-mostre.jpg": "/mostre/", "404_alt.jpg": "/",
            "img_0001.jpg": "/"}
# copertine delle categorie nella vecchia pagina Opere
for vecchio_nome, cat in {"alabastri": "alabastri", "bronzi": "bronzi", "incisioni": "incisioni", "legno": "legni", "materiali": "altri-materiali", "rame": "rame"}.items():
    SPECIALI[f"romanelli-{vecchio_nome}.jpg"] = f"/opere/{cat}/"
# disegni doppi tolti dal catalogo (stesso disegno, scansione diversa: verificati a vista il 28/11/2026)
for doppio, originale in {"1971-d.-min.jpg": "1971-d.-9-min.jpg", "1971-d.-8-min.jpg": "1971-d.-6-min.jpg"}.items():
    dove[norm(doppio)] = dove[norm(originale)]


def trova(nome):
    k = norm(nome)
    if k in SPECIALI:
        return SPECIALI[k]
    if k in dove:
        return dove[k]
    k2 = re.sub(r"-\d+(\.\w+)$", r"\1", k)  # copia caricata due volte: "-1", "-2"
    return dove.get(k2)


# --- elenco dei vecchi indirizzi ---
righe, rimandi = [], {}
DEMO = {"project", "profile", "oxy_testimonial", "oxy_modal", "oxy_stack", "oxy_mega_menu", "oxy_mega_columns"}
for p in P.values():
    if p["post_status"] != "publish":
        continue
    u = permalink(p)
    if not u:
        if p["post_type"] in DEMO:
            righe.append([f"(contenuto demo del tema) {p['post_type']}/{p['post_name']}", p["post_type"], p["post_title"], "", "non migrato: contenuto dimostrativo del tema"])
        continue
    if p["ID"] == "993":  # pagina impostata come home
        righe.append(["/", "home", p["post_title"], "/", "stesso indirizzo"])
        righe.append([u, "page", p["post_title"], "/", "rimando"]); rimandi[u] = "/"
        continue
    if esiste(u):
        righe.append([u, p["post_type"], p["post_title"], u, "stesso indirizzo"])
    else:
        righe.append([u, p["post_type"], p["post_title"], "", "MANCANTE"])

# pagine degli allegati (WordPress 5.0: una pagina per ogni immagine)
for a in P.values():
    if a["post_type"] != "attachment":
        continue
    file = META.get(a["ID"], {}).get("_wp_attached_file", "")
    if file.startswith("2016/") or not re.search(r"\.\w{3,4}$", file):
        continue  # immagini demo del tema e cartelle del plugin delle cartelle
    par = P.get(a["post_parent"]) if a["post_parent"] != "0" else None
    if par and par["post_type"] in DEMO | {"oxy_slideshow_image"}:
        par = None if par["post_type"] == "oxy_slideshow_image" else par
        if par:
            continue
    nome = ("attachment/" + a["post_name"]) if a["post_name"].isdigit() else a["post_name"]
    vecchio = (page_path(par) if par and par["post_type"] == "page" else permalink(par) if par else "/") + nome + "/" if par else f"/{a['post_name']}/"
    nuovo = trova(pathlib.Path(file).name)
    if not nuovo and par:
        nuovo = permalink(par) if par["ID"] != "993" else "/"
        nuovo = nuovo if nuovo and esiste(nuovo) else None
    nuovo = nuovo or "/opere/"
    if esiste(vecchio):
        righe.append([vecchio, "allegato", file, vecchio, "stesso indirizzo (pagina vera, nessun rimando)"])
        continue
    righe.append([vecchio, "allegato", file, nuovo, "rimando"])
    rimandi[vecchio] = nuovo

# tassonomia del vecchio portfolio
CAT = {"alabastri": "alabastri", "bronzi": "bronzi", "incisioni": "incisioni", "legni": "legni", "terracotta": "terracotta",
       "rame-sbalzato": "rame", "disegni": "disegni"}
T = {t["term_id"]: t for t in rows("wp8q_terms")}
for x in rows("wp8q_term_taxonomy"):
    if x["taxonomy"] != "oxy_portfolio_categories":
        continue
    s = T[x["term_id"]]["slug"]
    v, n = f"/oxy_portfolio_categories/{s}/", f"/opere/{CAT.get(s, 'altri-materiali')}/"
    righe.append([v, "categoria portfolio", s, n, "rimando"]); rimandi[v] = n

righe.sort(key=lambda r: (r[4] != "MANCANTE", r[1], r[0]))
out = ROOT / "archivio" / "recupero-2026" / "vecchi-indirizzi.csv"
with out.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["vecchio indirizzo", "tipo", "titolo o file", "nuovo indirizzo", "esito"])
    w.writerows(righe)
(ROOT / "src" / "rimandi.json").write_text(json.dumps(dict(sorted(rimandi.items())), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
from collections import Counter
print(Counter(r[4] for r in righe))
print("rimandi:", len(rimandi), "| mancanti:", [r[0] for r in righe if r[4] == "MANCANTE"])
