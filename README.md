# VB-Factory

Outil de suivi des projets d'installation machine (Vernet Behringer).

Application web **d'un seul fichier** (`index.html`) : aucun build, aucune dépendance à
installer. Elle s'ouvre telle quelle dans un navigateur.

---

## Architecture

| Élément | Où |
|---|---|
| Front-end | `index.html`, servi publiquement par GitHub Pages |
| Données | Google Drive de l'utilisateur — `My Drive/VB-Factory/vb-factory-data.json` |
| Sauvegardes | `My Drive/VB-Factory/backups/vb-factory-AAAA-MM-JJ.json` |
| Cache local | `localStorage` (accès instantané + tampon hors-ligne) |

Le front est public, **les données ne le sont pas** : elles vivent dans le Drive du
compte Google qui se connecte. Le code ne contient aucun secret — l'ID client OAuth est
public par conception, c'est précisément ce qui permet de publier le dépôt.

L'authentification utilise le scope `drive.file` : l'application n'a accès qu'aux
fichiers **qu'elle a elle-même créés**, jamais au reste du Drive.

---

## Configuration initiale (à faire une seule fois)

### 1. Créer l'ID client Google

1. Ouvrir [console.cloud.google.com](https://console.cloud.google.com) → créer un projet
   (nom libre, ex. `VB-Factory`).
2. Menu **API et services → Bibliothèque** → rechercher **Google Drive API** → *Activer*.
3. Menu **API et services → Écran de consentement OAuth** :
   - Type d'utilisateur : **Externe**
   - Nom de l'application : `VB-Factory`, e-mail d'assistance : le vôtre
   - Aucun scope à ajouter à la main sur cet écran
   - Ajouter votre adresse Google en **utilisateur test**
   - Une fois l'écran validé, cliquer **Publier l'application** (statut *En production*).
     Avec le seul scope `drive.file`, qui est **non sensible**, aucune vérification
     Google n'est requise. En statut *Test*, le consentement doit être re-accordé
     régulièrement — d'où la publication.
4. Menu **API et services → Identifiants** → *Créer des identifiants* → **ID client OAuth** :
   - Type d'application : **Application Web**
   - **Origines JavaScript autorisées** — ajouter les deux :
     - `https://yoannstegle-crypto.github.io`
     - `http://localhost:8000` (développement local)
   - **Aucune URI de redirection** n'est nécessaire (le flux par jeton n'en utilise pas)
5. Copier l'**ID client** (`…apps.googleusercontent.com`) et le renseigner dans
   `index.html`, constante `VB_GOOGLE_CLIENT_ID`.

> ⚠️ Ne créez **pas** le dossier `VB-Factory` à la main dans Drive. Avec le scope
> `drive.file`, l'application ne voit que ce qu'elle a créé : elle doit le créer
> elle-même au premier lancement, sinon elle ne le retrouvera jamais.

### 2. Activer GitHub Pages

Dépôt → **Settings → Pages** → Source : branche de publication, dossier `/` (racine).
L'application sera servie à l'adresse `https://yoannstegle-crypto.github.io/vb-factotum/`.

> Une page GitHub Pages est **publiquement lisible, même depuis un dépôt privé**.
> Aucune donnée client ne doit donc se trouver dans `index.html`.

---

## Développement local

```bash
python3 -m http.server 8000
# puis http://localhost:8000
```

Servir par HTTP est **nécessaire** : l'authentification Google ne fonctionne pas depuis
une URL `file://` (origine nulle), et certaines logiques de stockage s'en trouvent
faussées.

---

## Versionnage

`index.html` est le point d'entrée stable — c'est l'URL que l'on met en favori, elle ne
change jamais. Le numéro de révision s'affiche dans la barre latérale (`nav-ver`) et
dans le titre de l'onglet ; l'historique git et les tags tiennent lieu d'archive des
versions précédentes.

```bash
git tag rev-10.1.2 && git push --tags
```

---

## Sauvegardes

Trois filets superposés :

1. **`backups/` dans Drive** — une copie horodatée par jour d'utilisation, les 30
   dernières conservées.
2. **Historique de versions natif de Drive** — clic droit sur `vb-factory-data.json` →
   *Gérer les versions*.
3. **Export manuel** — bouton 💾 de la barre latérale, télécharge un JSON complet
   (projets + templates + configuration).

Le cache `localStorage` protège en plus du hors-ligne : une modification faite sans
réseau est conservée localement et renvoyée vers Drive dès la reconnexion.
