# Déploiement BDC Lecteur v2

L'application est hébergée dans le dossier `bdc-lecteur/` du dépôt `vb-factotum`,
déjà publié par GitHub Pages. Aucun dépôt séparé n'est nécessaire.

## URL

```
https://yoannstegle-crypto.github.io/vb-factotum/bdc-lecteur/
```

(`index.html` redirige vers `BDC_lecteur_v2.html`, accessible aussi directement.)

## Mettre à jour l'application

**Via l'interface web GitHub :**
1. Ouvrir le dossier `bdc-lecteur/` du dépôt
2. "Add file" → "Upload files" → déposer le nouveau `BDC_lecteur_v2.html` (il remplace l'ancien)
3. "Commit changes" sur la branche `main`

**Via terminal :**
```bash
cp /chemin/vers/nouveau/BDC_lecteur_v2.html bdc-lecteur/
git add bdc-lecteur/BDC_lecteur_v2.html
git commit -m "Mise à jour BDC Lecteur v2"
git push
```

GitHub Pages se met à jour automatiquement en ~1 minute après chaque push sur `main`.

## Notes

- La page est publique (accessible sans compte GitHub), comme le reste du site.
- Aucune clé API n'est stockée dans le code : chaque utilisateur saisit la sienne,
  conservée uniquement dans le `localStorage` de son navigateur.
- Les projets et profils sont eux aussi stockés localement dans le navigateur
  (pas de synchronisation entre appareils).
