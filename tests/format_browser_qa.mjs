// Entrée historique conservée : déléguer à la recette complète de l’interface actuelle.
// Les contrôles de distributions, historiques, instruments, genres, données et
// infobulles sont dans format_ux_browser_qa.mjs, y compris les anciens survols.
// L’ancien argument --genres-only lance désormais la recette complète.
if(!['avant','apres'].includes(process.argv[2]))process.argv[2]='apres';
await import('./format_ux_browser_qa.mjs');
