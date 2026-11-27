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
npm run build    # genera dist/
```

## Pubblicazione

Workflow manuale `Deploy su Aruba` (GitHub Actions). Secret richiesti nel repository:
`FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`, `FTP_SERVER_DIR` (cartella del sito sull'hosting).

## Note sul recupero dal vecchio WordPress (27/11/2026)

- Il catalogo opere (316 schede, `fonte: "libreria 2019"`) viene dalle 415 foto caricate nel 2019 nella libreria media di WordPress (cartelle `uploads/Opere/<Materiale>/`) e mai pubblicate. Anno, tecnica e titolo sono letti dai nomi dei file: vedi `archivio/recupero-2026/catalogo-parsing.csv` per la corrispondenza foto → scheda e `catalogo.py` per le regole.
- Le schede hanno `da_completare: true`: misure, collocazione e descrizioni vanno aggiunte a mano.
- Link esterni non più attivi (ASAC Biennale, Quadriennale, pagina di Manlio Alzetta) puntano a copie su archive.org: dettagli in `archivio/recupero-2026/link-esterni.json`.

- Testi e 93 immagini recuperati dal sito pubblico e dalla REST API di WordPress.
- Le categorie Bronzi, Incisioni, Legni, Rame e Terracotta erano vuote; le 6 schede opera avevano testi segnaposto del tema (`da_completare: true`).
- La Biografia pubblicata (Beaver Builder) è diversa dal testo salvato nel database, più lungo e narrativo: quest'ultimo è conservato in `archivio/biografia-versione-database.md`.
