import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { readdir, readFile, writeFile } from 'node:fs/promises';
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

export default defineConfig({
  site: 'https://www.giusepperomanelli.it',
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
  ],
});
