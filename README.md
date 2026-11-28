# giusepperomanelli.it

Sito statico (Astro) dello scultore Giuseppe Romanelli (Venezia 1916–1982).

## Dove stanno i contenuti

| Cosa | Dove | Come si modifica |
|---|---|---|
| Biografia, Curriculum, Opere pubbliche, Contatti, Credits, testo Home | `src/content/pagine/*.md` | Si modifica il testo Markdown |
| Mostre | `src/content/mostre/AAAA-MM-GG.md` | Un file per mostra. Se il file ha testo o foto, la mostra ha una sua pagina; se è vuoto compare solo nell'elenco |
| Opere | `src/content/opere/*.md` | Un file per opera: titolo, anno, categoria, materiale, immagini |
| Immagini | `src/assets/uploads/` | Si richiamano dai Markdown con percorso relativo. Astro le converte in WebP in più misure |

### Aggiungere un'opera

```md
---
title: "Nome dell'opera"
anno: 1965
categoria: "bronzi"   # alabastri | bronzi | incisioni | legni | rame | terracotta | disegni | altri-materiali
materiale: "Bronzo"
dimensioni: "cm 40 x 20 x 15"
immagini:
  - "../../assets/uploads/opere/nome-opera.jpg"
---

Testo facoltativo.
```

Una categoria compare nel sito solo quando contiene almeno un'opera.

## Comandi

```
npm install
npm run dev      # anteprima su http://localhost:4321
npm run build    # genera dist/ (sito definitivo, con le pagine di rimando)
npm run controllo  # controlli sulla build prima della pubblicazione
```

## Pubblicazione

- Workflow `Pubblicazione su GitHub Pages` (`.github/workflows/pubblica.yml`), a ogni push su main. La variabile `MODALITA` decide cosa va online:
  - `anteprima` (oggi): https://marco-tool.github.io/giusepperomanelli.it/, con `scripts/anteprima.py` che adatta gli indirizzi alla sottocartella, aggiunge la fascia "Anteprima" e il noindex.
  - `definitivo`: https://www.giusepperomanelli.it/, indicizzabile. Si attiva solo insieme al dominio personalizzato: vedi `archivio/passaggio-dominio.md`.
- Ogni build passa da `scripts/controllo_definitivo.py` (`npm run controllo`): noindex, indirizzi dell'anteprima, canonical, robots.txt, sitemap, collegamenti interni rotti, dimensione. Se un controllo fallisce non si pubblica nulla.
- Vecchi indirizzi del WordPress: `scripts/vecchi_indirizzi.py` li ricostruisce dall'export del database (che resta sul PC di Marco) e scrive `src/rimandi.json` e `archivio/recupero-2026/vecchi-indirizzi.csv`. In build, per ogni vecchio indirizzo che non esiste più, viene scritta una pagina di rimando (meta refresh a 0 secondi più canonical). Le pagine, le mostre e le 6 opere del vecchio portfolio hanno lo stesso indirizzo di prima.
- Il deploy su Aruba via FTP e il workflow di backup sono stati tolti il 28/11/2026: backup fatto, il sito va su GitHub Pages. Se nel repository ci sono ancora i secret `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`, `FTP_SERVER_DIR`, `BACKUP_PASSWORD`, vanno cancellati (Settings > Secrets and variables > Actions).

## Note sul recupero dal vecchio WordPress (27/11/2026)

- Il catalogo opere (316 schede, `fonte: "libreria 2019"`) viene dalle 415 foto caricate nel 2019 nella libreria media di WordPress (cartelle `uploads/Opere/<Materiale>/`) e mai pubblicate. Anno, tecnica e titolo sono letti dai nomi dei file: vedi `archivio/recupero-2026/catalogo-parsing.csv` per la corrispondenza foto → scheda e `catalogo.py` per le regole.
- Le schede hanno `da_completare: true`: misure, collocazione e descrizioni vanno aggiunte a mano.
- Ogni immagine della libreria WordPress (629 allegati nel database) è classificata in `archivio/recupero-2026/contabilita-libreria.csv`: 523 nel sito, 50 doppioni, 56 scartate con motivo. Le 70 non leggibili dall'esterno sono state controllate sul backup FTP del 28/11/2026: 41 immagini dimostrative del tema, 29 già nel sito (stesso file, doppione o ritaglio quadrato per lo slider). Nessuna immagine nuova.
- Il backup FTP e l'export del database restano solo sul PC di Marco (contengono la password del database): non vanno nel repository. Sul server le foto delle opere sono in alta risoluzione (fino a 4752 px); nel repository sono ridotte a 2000 px.
- Link esterni non più attivi (ASAC Biennale, Quadriennale, pagina di Manlio Alzetta) puntano a copie su archive.org: dettagli in `archivio/recupero-2026/link-esterni.json`.

- Testi e 93 immagini recuperati dal sito pubblico e dalla REST API di WordPress.
- Le categorie Bronzi, Incisioni, Legni, Rame e Terracotta erano vuote; le 6 schede opera avevano testi segnaposto del tema (`da_completare: true`).
- La Biografia pubblicata (Beaver Builder) è diversa dal testo salvato nel database, più lungo e narrativo: quest'ultimo è conservato in `archivio/biografia-versione-database.md`.
