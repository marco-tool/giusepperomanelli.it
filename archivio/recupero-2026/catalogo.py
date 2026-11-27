"""Trasforma le 415 foto del catalogo 2019 (uploads/Opere/<Cartella>/) in schede opera.

Fonte dei dati: il nome del file, es. "1948-L.carpino-Il-dono-2-min.jpg"
  -> anno 1948, tecnica "Legno di carpino", titolo "Il dono", variante 2.
Le varianti della stessa opera (2, 3, _0001, -min-1...) finiscono nella stessa scheda.
"""
import json, re, csv, unicodedata
from collections import defaultdict, OrderedDict

M = json.load(open("raw/media.json"))
cat = [m for m in M if "/uploads/Opere/" in m["source_url"]]

CATEGORIA = {
    "Alabastri": "alabastri", "Bronzi": "bronzi", "Incisioni": "incisioni", "Legni": "legni",
    "Rame_sbalzato": "rame", "Terracotta": "terracotta", "Disegni": "disegni",
}  # tutte le altre cartelle -> altri-materiali

# abbreviazioni usate nei nomi file -> tecnica estesa (ordine: le più lunghe prima)
ABBR = [
    (r"T\.?\s?[Cc]\.?", "Terracotta"), (r"R\.S\.", "Rame sbalzato"), (r"R\.", "Rame sbalzato"),
    (r"B\.", "Bronzo"), (r"b\.", "Bronzo"), (r"L\.?", "Legno"), (r"M\.", "Marmo"), (r"G\.", "Gesso"),
    (r"C\.", "Creta"), (r"d\.", "Disegno"), (r"a\.", "Alabastro"),
]
LEGNI = ["carpino", "faggio", "cedro", "gelso", "mansonia", "pesco", "cipresso", "tiglio"]
ALAB = ["bianco", "bardiglio", "corniola e rame", "corniola", "agata", "rosa"]
# parole tecniche (prefissi del nome file dopo l'anno), dalla più lunga
TECNICHE = [
    "acquaforte, bulino e acquatinta", "acquaforte bulino e acquatinta", "acqua forte e acquatinta",
    "acquaforte e acquatinta", "acquaforte e bulino", "acquaforte e punta secca", "bulino e acquaforte",
    "bulino e acquatinta", "bulino e punta secca", "bulino e puntasecca", "puntasecca e acquaforte",
    "vernice molle", "acquaforte", "acuaforte", "bulino", "puntasecca", "incisione",
    "disegno a matita copiativa",
    "bronzo e rame", "bronzo traforato", "bronzo",
    "rame sbalzato e oselle d'argento", "rame sbalzato e ottone", "rame sbalzato e traforato", "rame sbalzato",
    "argento e oro sbalzati", "argento sbalzato", "oro sbalzato e zaffiro", "oro sbalzato e turchesi", "oro sbalzato",
    "or0 sbalzato e zaffiro", "argento", "rame sbalzato",
    "marmo di carrara", "pietra d'istria", "legno faggio", "legno",
    "terracotta", "ceramica", "cemento", "vetro murina soffiato", "vetro soffiato", "vetro inciso", "vetro",
    "pannelli roll bond alluminio",
]
APOS = {  # apostrofi persi nei nomi file
    "nell-acqua": "nell'acqua", "Quarto-dAltino": "Quarto d'Altino",
    "nellacqua": "nell'acqua", "nell acqua": "nell'acqua", "dIstria": "d'Istria", "distria": "d'Istria",
    "Limmagine": "L'immagine", "dargento": "d'argento",
}
NOTITLE = {"", "min", "img", "romanelli"}


def clean(s):
    s = s.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip(" .,")
    return s


# casi che il nome file non permette di leggere da solo
OVERRIDE = {
    "1950-b.-S.Michele-1956-b.-S.Antonio-1960-b.-S.Ilario-min.jpg": ("1950-1960", "Bronzo", "S. Michele (1950), S. Antonio (1956), S. Ilario (1960)"),
    "1961-B.-Ragazze-che-si-sp...-min.jpg": ("1961", "Bronzo", "Ragazze che si specchiano nell'acqua"),
    "1958-rame-sbalzato.-Figure-che-si-specchiano-nellacqua-1965-rame-sbalzato-Acrobati-min.jpg": ("1958-1965", "Rame sbalzato", "Figure che si specchiano nell'acqua (1958), Acrobati (1965)"),
    "1972-acquaforte-.bulino-e-acquatinta-Teste-min.jpg": ("1972", "Acquaforte, bulino e acquatinta", "Teste"),
    "0001-spille-in-oro-argentorame-sbalzati-min.jpg": (None, "Oro, argento e rame sbalzati", "Spille"),
    "0002-anello-e-orecchini-min.jpg": (None, None, "Anello e orecchini"),
    "Cancello_bronzo.jpg": (None, "Bronzo", "Cancello"), "Cancello_2_bronzo.jpg": (None, "Bronzo", "Cancello"),
    "Cancello_3.jpg": (None, "Bronzo", "Cancello"), "Cancello_4.jpg": (None, "Bronzo", "Cancello"),
    "Cristo_bronzo.jpg": (None, "Bronzo", "Cristo"),
    "1972argentoLeon-Moeca-min.jpg": ("1972", "Argento", "Leon Moeca"),
    "1940-50T.c.-min.jpg": ("1940-1950", "Terracotta", ""),
}
# refusi e grafie diverse della stessa opera nei nomi file
NORMALIZZA = [
    (r"\bstratofera\b", "stratosfera"), (r"\bOperpsità\b", "Operosità"), (r"^Cieca$", "La cieca"),
    (r"^Crocifisso$", "Crocefisso"), (r"Donna\.?dei", "Donna dei"), (r"\bS\.\s?(?=[A-Z])", "S. "),
    (r"(?<=[a-zà-ù])\d+$", ""), (r"\.$", ""),
]


def parse(fn, folder):
    if fn in OVERRIDE:
        a, t, ti = OVERRIDE[fn]
        return a, t, ti, None
    base = re.sub(r"\.(jpe?g|png)$", "", fn, flags=re.I)
    base = re.sub(r"(-min)(-\d)?$", "", base)           # suffissi di compressione
    base = re.sub(r"JPG$", "", base)
    for k, v in APOS.items():
        base = base.replace(k, v)
    anno, resto = None, base
    m = re.match(r"^(19XX|19\d{2}-50|19\d{2}|195|19|0{3}\d)[-\s]?(.*)$", base)
    if m:
        a = m.group(1)
        anno = {"19XX": None, "195": "anni '50", "19": None}.get(a, a)
        if a.startswith("000"):
            anno = None
        if a.endswith("-50"):
            anno = "1940-1950"
        resto = m.group(2)
    resto = resto.lstrip("-. ")
    # varianti: "-2", "_0001", "_1"
    variante = None
    mv = re.search(r"(?:[-_ ](\d{1,4}))$", resto)
    if mv and not re.search(r"(^|-)\d+$", resto.split("-")[0] if resto else ""):
        variante = mv.group(1)
        resto = resto[: mv.start()]
    # tecnica abbreviata (B. / T.C. / L.carpino / a.bianco)
    tecnica = None
    for pat, nome in ABBR:
        mm = re.match(r"^" + pat + r"(?=[-\s.]|[a-zà-ù]|$)", resto)
        if mm:
            tecnica = nome
            resto = resto[mm.end():].lstrip("-. ")
            if nome == "Legno":
                for l in LEGNI:
                    if resto.lower().startswith(l):
                        tecnica = f"Legno di {l}"
                        resto = resto[len(l):].lstrip("-. ")
                        break
            if nome == "Alabastro":
                for l in ALAB:
                    lc = l.replace(" ", "-")
                    if resto.lower().startswith(lc) or resto.lower().startswith(l):
                        tecnica = f"Alabastro {l}"
                        resto = resto[len(l):].lstrip("-. ")
                        break
            break
    if tecnica is None:
        r = clean(resto).lower()
        for t in TECNICHE:
            if r.startswith(t):
                tecnica = t
                resto = clean(resto)[len(t):].strip()
                break
    titolo = clean(resto)
    titolo = re.sub(r"\s*particolare\s*$", "", titolo, flags=re.I)
    titolo = re.sub(r"^\.?spilla\s+", "Spilla ", titolo)
    if tecnica:
        tecnica = tecnica[0].upper() + tecnica[1:]
        tecnica = (tecnica.replace("Or0", "Oro").replace("Acuaforte", "Acquaforte")
                   .replace("Acqua forte", "Acquaforte").replace("Legno faggio", "Legno di faggio")
                   .replace("carrara", "Carrara").replace("d'istria", "d'Istria")
                   .replace("Pannelli roll bond alluminio", "Pannelli roll-bond in alluminio"))
    if titolo.lower() in NOTITLE or titolo.lower().startswith("img ") or re.fullmatch(r"(IMG|P)\d+|\d+", titolo or ""):
        titolo = ""
    for pat, rep in NORMALIZZA:
        titolo = re.sub(pat, rep, titolo).strip()
    if titolo:
        titolo = titolo[0].upper() + titolo[1:]
    return anno, tecnica, titolo, variante


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


opere = OrderedDict()
log = []
for m in sorted(cat, key=lambda m: m["source_url"]):
    rel = m["source_url"].split("/uploads/")[1]
    folder, fn = rel.split("/")[1], rel.split("/")[-1]
    anno, tecnica, titolo, variante = parse(fn, folder)
    categoria = CATEGORIA.get(folder, "altri-materiali")
    if not tecnica:
        tecnica = {"Bassorilievi": "Bassorilievo", "Osso": "Osso", "Disegni": "Disegno",
                   "Incisioni": "Incisione", "Marmo": "Marmo"}.get(folder)
    # chiave dell'opera: stessa cartella + anno + titolo; senza titolo = una scheda per foto
    if titolo:
        key = (folder, anno, titolo.lower())
    else:
        key = (folder, anno, fn)
    if key not in opere:
        opere[key] = {"title": titolo or (f"{tecnica or folder}, senza titolo"), "anno": anno,
                      "categoria": categoria, "materiale": tecnica, "cartella": folder,
                      "immagini": [], "file": [], "senza_titolo": not titolo}
    opere[key]["immagini"].append(rel)
    opere[key]["file"].append(fn)
    log.append([folder, fn, anno or "", tecnica or "", titolo, variante or "", categoria])

with open("raw/catalogo-parsing.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cartella", "file", "anno", "tecnica", "titolo", "variante", "categoria"])
    w.writerows(log)
json.dump(list(opere.values()), open("raw/catalogo-opere.json", "w"), indent=1, ensure_ascii=False)
from collections import Counter
print("foto", len(cat), "-> opere", len(opere))
print(Counter(o["categoria"] for o in opere.values()))
print("senza titolo:", sum(o["senza_titolo"] for o in opere.values()))
print("senza anno:", sum(1 for o in opere.values() if not o["anno"]))
