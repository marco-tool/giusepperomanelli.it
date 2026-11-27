export const CATEGORIE = {
  alabastri: 'Alabastri',
  bronzi: 'Bronzi',
  incisioni: 'Incisioni',
  legni: 'Legni',
  rame: 'Rame',
  terracotta: 'Terracotta',
  'altri-materiali': 'Altri materiali',
} as const;
export type Categoria = keyof typeof CATEGORIE;
