# Vidéo → Art-Net → WLED (Gledopto GL-C-618WL)

Envoie une vidéo (fichier, ou n'importe quel onglet/fenêtre comme YouTube) vers une
matrice LED pilotée par WLED, en Art-Net, via le câble Ethernet.

```
[Navigateur : index.html] --HTTP local--> [artnet_bridge.py] --UDP Art-Net--> [WLED]
```

Un navigateur ne sait pas envoyer d'UDP : `artnet_bridge.py` fait le relais.
Il n'a besoin que de Python, sans aucun module à installer.

## 1. Installer Python (une seule fois)

https://www.python.org/downloads/ → installer, en **cochant « Add python.exe to PATH »**.

## 2. Réseau (câble direct PC ↔ boîtier)

Le PC et le boîtier doivent être sur le même réseau. Détails complets dans le manuel
intégré (onglet Manuel → chapitre 4).

**A. Sans droits administrateur (conseillé)** : sans box, Windows se donne une adresse
`169.254.x.x` sur la carte Ethernet (visible avec `ipconfig`). Dans l'application,
« 🔍 Rechercher les boîtiers » affiche l'adresse à mettre dans WLED, par exemple
`169.254.134.50`, masque `255.255.0.0`, passerelle `0.0.0.0`. Dans WLED : Config → WiFi
Setup → *Ethernet Type* « Gledopto Series With Ethernet » + *Static IP* → enregistrer,
redémarrer, puis relancer la recherche et cliquer sur « Choisir ».

**B. Avec droits administrateur** : PC en `192.168.50.1` / `255.255.255.0`
(`netsh interface ipv4 set address name="Ethernet" static 192.168.50.1 255.255.255.0`),
WLED en `192.168.50.2` / `255.255.255.0`.

**C. Via la box ou un routeur** : WLED en adresse automatique, le PC le trouve avec
« 🔍 Rechercher les boîtiers ».

## 3. Réglages WLED

- **Config → LED Preferences** : nombre total de LEDs (ex. 5 barres × 120 = **600**),
  bon type de LED et bonne broche. *Maximum current* selon l'alimentation.
- **Config → 2D Configuration** : **désactivé (1D)**. C'est la page web qui connaît la
  position de chaque LED et envoie les couleurs directement dans l'ordre du fil.
- **Config → Sync Interfaces → Realtime** :
  - *Receive UDP realtime* : coché
  - *Type* : **Art-Net**
  - *Start universe* : **1**
  - *DMX start address* : **1**
  - *DMX mode* : **Multi RGB**
  - *Timeout* : 2500 ms (WLED reprend son effet normal quand on arrête)

170 LEDs par univers : 600 LEDs = 4 univers (1 à 4).

## 4. Décrire l'installation (disposition des barres)

Chaque barre est un segment : **point de début** (côté où arrive le fil de données),
**point de fin**, **nombre de LEDs**. Coordonnées en cm, vue de face, X vers la droite,
Y vers le haut. L'ordre des barres dans le tableau = l'ordre sur le fil.

Chaque LED prend la couleur de la vidéo à sa position réelle : barres horizontales,
verticales, espacements différents ou barres en biais sont tous gérés de la même façon.

- **Créer une disposition** : génère des barres régulières (nombre, longueur, LEDs,
  espacement, orientation, coin de départ du fil, serpentin). Par défaut : 5 barres
  horizontales de 2 m / 120 LEDs, espacées de 50 cm, départ en bas à droite, serpentin.
- **Éditeur** : glisser les poignées (● début, ■ fin) ou le milieu d'une barre.
  Déplacement par paliers (10 cm, 25 cm, 50 cm, 1 m) ; **Alt** pour un placement libre.
- **Tableau** : saisie précise en cm, ▲▼ pour l'ordre, ⇄ pour inverser le sens.
- **Enregistrer / Charger** : sauvegarde la disposition dans un fichier `.json`.

## 5. Utilisation

1. Double-cliquer sur **`lancer.bat`** → une fenêtre noire s'ouvre (à laisser ouverte),
   puis le navigateur s'ouvre sur http://localhost:8080.
2. Vérifier l'IP du WLED (`192.168.50.2`) et l'univers (1).
3. Cliquer sur **Mire** : chaque barre s'allume dans sa couleur (pastille du tableau),
   en dégradé du début (sombre) vers la fin (clair). Si une barre n'a pas la bonne
   couleur → ordre à corriger (▲▼) ; si le dégradé est à l'envers → ⇄.
4. Choisir une source :
   - **Fichier vidéo** : « Ouvrir un fichier vidéo ».
   - **YouTube** : ouvrir la vidéo dans une autre fenêtre, cliquer « Capturer un onglet /
     une fenêtre » et la sélectionner. Garder les deux fenêtres visibles côte à côte.
5. **Cadrage** : zoom et décalages choisissent quelle partie de la vidéo tombe sur les
   barres (la vidéo est affichée en transparence derrière les barres dans l'éditeur).
   *Épaisseur captée* : largeur de la bande de vidéo moyennée autour de chaque barre.

6. **Simulation** : affichée à côté de l'éditeur, elle montre le rendu de
   l'installation à l'écran (⛶ plein écran possible). Décocher « Envoyer aux LEDs » pour
   travailler sans boîtier.

Le manuel complet est dans l'application : onglet **📖 Manuel utilisateur**, ou boutons
**?** à côté de chaque bloc.

Utiliser Chrome ou Edge (la capture d'onglet y fonctionne le mieux).
