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

Pas de box, donc adresses fixes :

| Appareil | IP | Masque |
|---|---|---|
| Boîtier WLED | `192.168.50.2` | `255.255.255.0` |
| PC (carte Ethernet) | `192.168.50.1` | `255.255.255.0` |

**PC Windows** : Paramètres → Réseau et Internet → Ethernet → Attribution d'adresse IP
→ Modifier → Manuel → IPv4 : IP `192.168.50.1`, masque `255.255.255.0`
(passerelle et DNS vides).

**WLED** (en le joignant d'abord par son Wi-Fi) :
- Config → WiFi Setup → *Ethernet Type* : **Gledopto Series With Ethernet** → enregistrer, redémarrer.
- Config → WiFi Setup → *Static IP* `192.168.50.2`, *Subnet* `255.255.255.0`
  (*Gateway* `192.168.50.1`).
- Vérifier : http://192.168.50.2 doit s'ouvrir depuis le PC avec le câble branché.

Si le pare-feu Windows le demande au premier lancement, autoriser Python sur les réseaux privés.

## 3. Réglages WLED

- **Config → LED Preferences** : 480 LEDs (4 × 120), bon type de LED et bonne broche.
- **Config → 2D Configuration** : *2D Matrix*, 1 panneau, largeur **120**, hauteur **4**,
  coin de départ et *Serpentine* selon le câblage réel.
- **Config → Sync Interfaces → Realtime** :
  - *Receive UDP realtime* : coché
  - *Type* : **Art-Net**
  - *Start universe* : **1**
  - *DMX start address* : **1**
  - *DMX mode* : **Multi RGB**
  - *Timeout* : 2500 ms (WLED reprend son effet normal quand on arrête)

480 LEDs = 3 univers : 1 (LEDs 1–170), 2 (171–340), 3 (341–480).

## 4. Utilisation

1. Double-cliquer sur **`lancer.bat`** → une fenêtre noire s'ouvre (à laisser ouverte),
   puis le navigateur s'ouvre sur http://localhost:8080.
2. Vérifier l'IP du WLED (`192.168.50.2`), l'univers (1) et la taille (120 × 4).
3. Cliquer sur **Mire** : ligne 1 rouge, 2 vert, 3 bleu, 4 blanc, dégradé de gauche à droite.
   - Si c'est bon, tout est en place.
   - Si une ligne sur deux est à l'envers, active la *Serpentine* dans WLED (2D Configuration)
     ou coche « Câblage en zigzag » dans la page.
   - Si l'image est inversée, utilise « Miroir horizontal / vertical ».
4. Choisir une source :
   - **Fichier vidéo** : « Ouvrir un fichier vidéo ».
   - **YouTube** : ouvrir la vidéo dans une autre fenêtre, cliquer « Capturer un onglet /
     une fenêtre » et la sélectionner. Mieux vaut que les deux fenêtres soient côte à
     côte et visibles.
5. Régler la zone :
   - « Image entière » : toute la hauteur de la vidéo est écrasée sur les 4 lignes.
   - « Bande aux vraies proportions » : seule une fine bande horizontale est envoyée
     (une matrice 120 × 4 est 30 fois plus large que haute) ; « Position verticale »
     choisit laquelle. Le cadre bleu dans l'aperçu montre la zone envoyée.

Utiliser Chrome ou Edge (la capture d'onglet y fonctionne le mieux).
