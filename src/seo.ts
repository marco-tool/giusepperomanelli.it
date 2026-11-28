// Dati comuni per SEO: persona, immagini di anteprima, dati strutturati (schema.org)
import { getImage } from 'astro:assets';
import type { ImageMetadata } from 'astro';
import ritratto from './assets/uploads/2019/05/giuseppe-romanelli.jpg';

export const SITE = 'https://www.giusepperomanelli.it';
export const PERSON_ID = `${SITE}/#giuseppe-romanelli`;
export const SUFFISSO = 'scultore veneziano (1916–1982)';

/** Immagine di anteprima per social e dati strutturati: JPEG largo al massimo 1200 px, URL assoluto */
export async function ogImage(src: ImageMetadata = ritratto): Promise<string> {
  const img = await getImage({ src, width: Math.min(1200, src.width), format: 'jpg', quality: 75, layout: 'none' });
  return new URL(img.src, SITE).href;
}

export async function persona() {
  return {
    '@type': 'Person',
    '@id': PERSON_ID,
    name: 'Giuseppe Romanelli',
    birthDate: '1916-03-02',
    birthPlace: { '@type': 'Place', name: 'Venezia' },
    deathDate: '1982-07-02',
    deathPlace: { '@type': 'Place', name: 'Venezia' },
    nationality: { '@type': 'Country', name: 'Italia' },
    jobTitle: 'Scultore',
    alumniOf: { '@type': 'CollegeOrUniversity', name: 'Accademia di Belle Arti di Venezia' },
    description: 'Scultore veneziano (1916–1982), allievo di Arturo Martini. Ha esposto alla Biennale di Venezia e alla Quadriennale di Roma.',
    image: await ogImage(),
    url: `${SITE}/`,
  };
}

/** Riferimento breve alla persona, da usare dentro altri oggetti */
export const autore = { '@type': 'Person', '@id': PERSON_ID, name: 'Giuseppe Romanelli' };

export function briciole(voci: [string, string][]) {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: voci.map(([name, path], i) => ({ '@type': 'ListItem', position: i + 1, name, item: new URL(path, SITE).href })),
  };
}

/** Taglia un testo a max caratteri senza spezzare le parole */
export function taglia(t: string, max = 158): string {
  const s = t.replace(/\s+/g, ' ').trim();
  if (s.length <= max) return s;
  return s.slice(0, s.lastIndexOf(' ', max - 1)).replace(/[,;:.\s]+$/, '') + '…';
}

/** Prima frase leggibile di un testo markdown (link, enfasi e titoli tolti) */
export function primaFrase(md: string | undefined): string {
  const t = (md ?? '')
    .replace(/<[^>]+>/g, ' ')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, ' ')
    .replace(/\[([^\]]*)\]\([^)]*\)/g, '$1')
    .replace(/^#+\s*/gm, '')
    .replace(/[*_`>|]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  const m = t.match(/^(.+?[.!?])(\s|$)/);
  return (m ? m[1] : t).trim();
}

// Titolo per Google: "Omaggio alla partigiana, bronzo 1964"; "Terracotta senza titolo, 1940-1950"
export function titoloSeo(d: { title: string; materiale?: string; anno?: number | string }): string {
  const senza = /senza titolo/i.test(d.title);
  const t = senza ? d.title.replace(/,\s*senza titolo/i, ' senza titolo') : d.title;
  const mat = d.materiale && !senza && !d.title.toLowerCase().startsWith(d.materiale.toLowerCase()) ? d.materiale.toLowerCase() : '';
  const resto = [mat, d.anno].filter(Boolean).join(' ');
  return resto ? `${t}, ${resto}` : t;
}
