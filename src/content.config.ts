import { defineCollection } from 'astro:content';
import { glob, file } from 'astro/loaders';
import { z } from 'astro/zod';

// Pagine fisse: Home, Biografia, Curriculum, Opere pubbliche, Contatti, Credits, introduzione Mostre
const pagine = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/pagine' }),
  schema: z.object({
    title: z.string(),
    // meta description per Google (max ~155 caratteri)
    descrizione: z.string().optional(),
  }),
});

// Una mostra = un file. Se il file ha testo o foto, la mostra ha una sua pagina.
const mostre = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/mostre' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      data: z.coerce.date(),
      luogo: z.string().optional(),
      copertina: image().optional(),
      // per titolo, descrizione e dati strutturati (solo mostre con pagina)
      sede: z.string().optional(),
      citta: z.string().optional(),
      paese: z.string().default('IT'),
      fine: z.coerce.date().optional(),
      // true se "data" è solo un segnaposto per l'anno
      solo_anno: z.boolean().default(false),
      descrizione: z.string().optional(),
      // mostra nota solo da fonti esterne (non dai materiali di famiglia): chi la documenta
      fonte: z.string().optional(),
    }),
});

// Una opera = un file. Categoria = materiale principale.
const opere = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/opere' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      // anno: numero (1964) oppure testo per date incerte ("anni '50", "1940-1950")
      anno: z.union([z.number(), z.string()]).optional(),
      categoria: z.enum(['alabastri', 'bronzi', 'incisioni', 'legni', 'rame', 'terracotta', 'disegni', 'altri-materiali']),
      materiale: z.string().optional(),
      dimensioni: z.string().optional(),
      immagini: z.array(image()).min(1),
      // didascalie delle singole foto, nello stesso ordine di "immagini" (facoltative)
      didascalie: z.array(z.string()).optional(),
      // da dove viene la scheda: "sito 2019" (pubblicata) o "libreria 2019" (catalogo caricato e mai pubblicato)
      fonte: z.string().optional(),
      da_completare: z.boolean().default(false),
    }),
});

// Pagine esterne che parlano di Romanelli (pagina /riferimenti/): un elemento del file YAML = una fonte
const link = z.object({ etichetta: z.string(), url: z.string() });
const riferimenti = defineCollection({
  loader: file('./src/content/riferimenti.yaml'),
  schema: z.object({
    gruppo: z.enum(['enciclopedie', 'opere', 'archivi', 'studi', 'biblioteche', 'altro', 'stampa']),
    titolo: z.string(),
    fonte: z.string(),
    anno: z.string().optional(),
    descrizione: z.string().default(''),
    url: z.url().optional(),
    lingua: z.string().optional(),
    altri: z.array(link).optional(),
    sul_sito: link.optional(),
  }),
});

// Opere pubbliche: una scheda per luogo (chiesa, scuola, cimitero, museo), pagina /opere-pubbliche/<id>/
const luoghi = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/luoghi' }),
  schema: z.object({
    title: z.string(),
    ordine: z.number(),
    zona: z.enum(['venezia', 'isole', 'terraferma', 'provincia', 'veneto', 'italia', 'musei']),
    luogo: z.string(),
    citta: z.string(),
    anno: z.string().optional(),
    opere: z.array(z.string()).min(1),
    fonti: z.array(z.object({ etichetta: z.string(), url: z.url().optional() })).min(1),
  }),
});

export const collections = { pagine, mostre, opere, riferimenti, luoghi };
