# Passaggio di giusepperomanelli.it a GitHub Pages

Preparato il 28/11/2026. Stato: il sito definitivo è pronto (controlli di `scripts/controllo_definitivo.py` superati, 341 pagine, 598 rimandi dai vecchi indirizzi, 252 MB). Il backup del vecchio WordPress e del database è fatto.

Il vecchio sito dal 28/11/2026 (almeno) risponde "Error establishing a database connection" su tutte le pagine: Aruba ha spostato il database su un altro server (phpMyAdmin si collega a 31.11.38.60, wp-config.php punta ancora a 89.46.111.72). Non è un danno da riparare: il passaggio lo sostituisce.

Chi fa cosa: **M** = Marco (pannelli GitHub e Aruba, Claude non ci arriva), **C** = Claude.

## 1. GitHub: verifica del dominio (M, consigliato, 5 minuti)
Impedisce che qualcun altro usi il dominio su GitHub Pages.
1. github.com, foto profilo, Settings, Pages (menu a sinistra, sezione "Code, planning, and automation"), "Add a domain": `giusepperomanelli.it`.
2. GitHub mostra un record TXT (nome `_github-pages-challenge-marco-tool`, valore casuale): va aggiunto nei DNS su Aruba (passo 2), poi "Verify".

## 2. Aruba: DNS (M, con screenshot a C)
Nel pannello Aruba del dominio, gestione DNS. Prima di cambiare, uno screenshot dei record attuali (serve per tornare indietro).
- Record **A** di `giusepperomanelli.it` (dominio nudo): togliere quello dell'hosting Aruba e mettere i quattro di GitHub
  `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
- Facoltativi, **AAAA** (IPv6): `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`
- **www**: un solo record **CNAME** verso `marco-tool.github.io` (se oggi c'è un record A per www, va tolto)
- Il TXT del passo 1
- Non toccare **MX** e gli altri record della posta

## 3. GitHub: dominio del repository (M) e modalità definitiva (C), insieme
1. M: repository giusepperomanelli.it, Settings, Pages, "Custom domain": `www.giusepperomanelli.it`, Save. Da quel momento l'anteprima su marco-tool.github.io rimanda al dominio.
2. C, subito dopo: in `.github/workflows/pubblica.yml` `MODALITA: definitivo`, push. La build (circa 4 minuti) pubblica il sito senza fascia e senza noindex.
3. M, quando GitHub ha emesso il certificato (da pochi minuti a 24 ore): spuntare "Enforce HTTPS".

## 4. Controlli dopo l'accensione (C)
- https://www.giusepperomanelli.it/ e https://giusepperomanelli.it/ (deve rimandare a www) rispondono con il sito nuovo, in HTTPS
- campione di vecchi indirizzi da `archivio/recupero-2026/vecchi-indirizzi.csv`: stesse pagine e rimandi
- robots.txt, sitemap-index.xml, pagina 404

## 5. Google Search Console (M con C)
1. search.google.com/search-console, "Aggiungi proprietà", tipo **Dominio**: `giusepperomanelli.it`. Google dà un record TXT da aggiungere su Aruba.
2. Dopo la verifica: Sitemap, inviare `https://www.giusepperomanelli.it/sitemap-index.xml`.
3. Dopo 2-4 settimane: rapporto "Pagine" (404 e pagine escluse) e immagini cercate con i vecchi indirizzi /wp-content/uploads/ (decidere se ripubblicarne qualcuna).

## 6. Aruba: da hosting a solo dominio (M)
Solo dopo che il sito nuovo risponde da qualche giorno.
1. Mail Admin: ci sono caselle @giusepperomanelli.it in uso? No: "Dominio" (14,63 €/anno). Sì: "Dominio con email" (20,12 €/anno).
2. Cambio servizio da Hosting Linux a Dominio (circa 12,20 € una tantum). Cancella lo spazio web e il vecchio WordPress: il backup è sul PC di Marco.
3. Subito dopo, ricontrollare che i record DNS del passo 2 ci siano ancora.
4. Database Sql1247568: lasciarlo scadere il 10/9/2027.

## Per tornare indietro
Rimettere in Aruba i record DNS dello screenshot del passo 2 e togliere il dominio in Settings, Pages. C rimette `MODALITA: anteprima`.
