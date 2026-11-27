export const CATEGORIE = {
  alabastri: 'Alabastri',
  bronzi: 'Bronzi',
  incisioni: 'Incisioni',
  legni: 'Legni',
  rame: 'Rame',
  terracotta: 'Terracotta',
  disegni: 'Disegni',
  'altri-materiali': 'Altri materiali',
} as const;
export type Categoria = keyof typeof CATEGORIE;

/** Anno come numero per ordinare: 1964, "anni '50" -> 1950, "1940-1950" -> 1940, assente -> 9999 */
export function annoOrdine(a: number | string | undefined): number {
  if (typeof a === 'number') return a;
  const m = String(a ?? '').match(/(\d{4})|'(\d{2})/);
  if (!m) return 9999;
  return m[1] ? Number(m[1]) : 1900 + Number(m[2]);
}
