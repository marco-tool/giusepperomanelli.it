import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { readdir, readFile, writeFile, mkdir, access } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Le immagini inserite nei testi (pagine delle mostre, curriculum, opere pubbliche) sono mostrate al massimo
// a 680 px, la larghezza della colonna di testo. Astro dà loro "sizes" uguale alla larghezza originale:
// qui lo correggiamo, così il telefono scarica la versione piccola e non la scansione intera.
const SIZES_TESTO = '(max-width: 720px) calc(100vw - 40px), 680px';
function sizesImmaginiNeiTesti() {
  return {
    name: 'sizes-immagini-nei-testi',
    hooks: {
      'astro:build:done': async ({ dir }) => {
        const root = fileURLToPath(dir);
        const files = (await readdir(root, { recursive: true })).filter((f) => f.endsWith('.html'));
        for (const f of files) {
          const p = join(root, f);
          const html = await readFile(p, 'utf8');
          const out = html.replace(/sizes="\(min-width: (\d+)px\) \1px, 100vw"/g, (m, w) => (Number(w) > 680 ? `sizes="${SIZES_TESTO}"` : m));
          if (out !== html) await writeFile(p, out);
        }
      },
    },
  };
}

// Vecchi indirizzi del WordPress (pagine degli allegati, categorie del portfolio, /home-4/):
// GitHub Pages non fa rimandi lato server, quindi per ognuno scriviamo una pagina minima che porta
// subito al nuovo indirizzo (meta refresh a 0 secondi, che Google tratta come rimando permanente).
// L'elenco è in src/rimandi.json, generato da scripts/vecchi_indirizzi.py; una pagina vera non viene mai sovrascritta.
const SITO = 'https://www.giusepperomanelli.it';
function rimandiVecchiIndirizzi() {
  return {
    name: 'rimandi-vecchi-indirizzi',
    hooks: {
      'astro:build:done': async ({ dir, logger }) => {
        const root = fileURLToPath(dir);
        const rimandi = JSON.parse(await readFile(new URL('./src/rimandi.json', import.meta.url), 'utf8'));
        let scritti = 0;
        for (const [vecchio, nuovo] of Object.entries(rimandi)) {
          const file = join(root, vecchio, 'index.html');
          try { await access(file); continue; } catch {}
          const html = `<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Pagina spostata | Giuseppe Romanelli</title>` +
            `<link rel="canonical" href="${SITO}${nuovo}"><meta http-equiv="refresh" content="0; url=${nuovo}"></head>` +
            `<body><p>Questa pagina ora è qui: <a href="${nuovo}">${SITO}${nuovo}</a></p></body></html>`;
          await mkdir(join(root, vecchio), { recursive: true });
          await writeFile(file, html);
          scritti++;
        }
        logger.info(`${scritti} pagine di rimando dai vecchi indirizzi`);
      },
    },
  };
}

export default defineConfig({
  site: SITO,
  trailingSlash: 'always',
  build: { format: 'directory' },
  image: {
    // srcset automatico anche per le immagini nei testi markdown
    layout: 'constrained',
    breakpoints: [480, 680, 960, 1360],
  },
  integrations: [
    sitemap({ filter: (page) => !page.includes('/404') }),
    sizesImmaginiNeiTesti(),
    rimandiVecchiIndirizzi(),
  ],
});
