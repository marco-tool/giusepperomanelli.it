import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Pagine fisse: Home, Biografia, Curriculum, Opere pubbliche, Contatti, Credits, introduzione Mostre
const pagine = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/pagine' }),
  schema: z.object({ title: z.string() }),
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
    }),
});

// Una opera = un file. Categoria = materiale principale.
const opere = defineCollection({
  loader: glob({ pattern: '*.md', base: './src/content/opere' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      anno: z.number().optional(),
      categoria: z.enum(['alabastri', 'bronzi', 'incisioni', 'legni', 'rame', 'terracotta', 'altri-materiali']),
      materiale: z.string().optional(),
      dimensioni: z.string().optional(),
      immagini: z.array(image()).min(1),
      da_completare: z.boolean().default(false),
    }),
});

export const collections = { pagine, mostre, opere };
