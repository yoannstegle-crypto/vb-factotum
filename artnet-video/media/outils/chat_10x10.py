#!/usr/bin/env python3
"""
Genere la video « chat » pour une matrice 10 x 10 :
10 barres horizontales de 15 cm, 10 LEDs par barre, espacement 2 cm
(depart en bas a gauche, serpentin -- le cablage est gere par l'application).

La video est calee pour l'application avec : Zoom 100 %, decalages 0 %,
Epaisseur captee = fine (0). Chaque pixel de la matrice = un bloc de la video
centre exactement sur la LED correspondante.

Usage : python3 chat_10x10.py sortie.mp4 [attendu.json]
(necessite ffmpeg ; aucune dependance Python)
"""
import json
import math
import subprocess
import sys

FPS = 30
DUR = 28.0
N = 10                      # 10 x 10
PITCH, GAP = 1.5, 2.0       # cm : pas des LEDs, ecart entre barres
MARGIN = 1.5                # marge de la "scene" calculee par l'application
STAGE_W = N * PITCH + 2 * MARGIN                          # 15 + 3 = 18 cm
STAGE_H = (N - 1) * GAP + 2 * MARGIN                       # 18 + 3 = 21 cm
SCALE = 100 / 3             # px par cm  -> video 600 x 700
W, H = round(STAGE_W * SCALE), round(STAGE_H * SCALE)

COL = {
    "O": (255, 110, 0),     # pelage orange
    "P": (255, 40, 110),    # rose (oreilles, nez, langue)
    "G": (0, 255, 70),      # yeux verts
    "W": (255, 255, 255),   # moustaches
    "R": (255, 0, 30),      # coeur
    "K": (0, 0, 0),         # noir (LED eteinte)
}


def cat(eyes="open", look=0, mouth="neutral", whisk=0, ear=False):
    g = [list("." * N) for _ in range(N)]
    rows = [
        ".O......O.",
        ".OP....PO.",
        ".OOOOOOOO.",
        "OOOOOOOOOO",
        "OOOOOOOOOO",
        "OOOOOOOOOO",
        "OOOOPPOOOO",
        "OOOOOOOOOO",
        ".OOOOOOOO.",
        "..OOOOOO..",
    ]
    for r, line in enumerate(rows):
        g[r] = list(line)
    if ear:                              # l'oreille gauche frémit
        g[0][1], g[0][0] = ".", "O"
    # yeux : 2 x 2 (lignes 4-5, colonnes 1-2 et 7-8)
    pupil = {-1: (1, 7), 0: (2, 7), 1: (2, 8)}[look]
    for side, (c0, c1) in enumerate(((1, 2), (7, 8))):
        state = eyes
        if eyes == "wink":
            state = "open" if side == 0 else "closed"
        if state == "open":
            g[4][c0] = g[4][c1] = "G"
        if state in ("open", "half"):
            g[5][c0] = g[5][c1] = "G"
            g[5][pupil[side]] = "K"
        if state == "closed":
            g[5][c0] = g[5][c1] = "K"
    # moustaches
    r = 6 + whisk
    g[r][0] = g[r][9] = "W"
    # bouche
    if mouth == "neutral":
        g[7][4] = g[7][5] = "K"
    elif mouth == "smile":
        g[7][2] = g[7][7] = "K"
        for c in (3, 4, 5, 6):
            g[8][c] = "K"
    elif mouth == "open":
        g[7][3] = g[7][4] = g[7][5] = g[7][6] = "K"
        g[8][4] = g[8][5] = "P"
    return g


HEART = [list(s) for s in (
    ".RR....RR.",
    "RRRR..RRRR",
    "RRRRRRRRRR",
    "RRRRRRRRRR",
    "RRRRRRRRRR",
    ".RRRRRRRR.",
    "..RRRRRR..",
    "...RRRR...",
    "....RR....",
    "..........",
)]


def colors(grid, bright=1.0):
    return [[tuple(int(v * bright) for v in COL.get(ch, (0, 0, 0))) if ch not in ". " else (0, 0, 0)
             for ch in row] for row in grid]


BASE = cat()
DRAW_ORDER = [(r, c) for r in range(N) for c in (range(N) if r % 2 == 0 else range(N - 1, -1, -1))
              if BASE[r][c] not in ". K"]
DRAW_T0, DRAW_T1 = 0.5, 6.5


def frame(t):
    """Grille 10 x 10 de couleurs RGB pour l'instant t (s)."""
    if t < DRAW_T0:
        return colors([["."] * N for _ in range(N)])
    if t < DRAW_T1:                                    # dessin pixel par pixel
        k = (t - DRAW_T0) / (DRAW_T1 - DRAW_T0) * len(DRAW_ORDER)
        g = colors(BASE)
        out = [[(0, 0, 0)] * N for _ in range(N)]
        for i, (r, c) in enumerate(DRAW_ORDER):
            if i < int(k):
                age = k - i
                out[r][c] = (255, 255, 255) if age < 0.6 else g[r][c]   # éclair blanc à la pose
        return out
    blinks = [(7.5, 7.65), (7.9, 8.05), (24.6, 24.75), (25.3, 25.45)]
    blink = any(a <= t < b for a, b in blinks)
    if t < 8.5:
        return colors(cat("closed" if blink else "open"))
    if t < 9.5:
        return colors(cat(look=-1))
    if t < 10.5:
        return colors(cat(look=1))
    if t < 11.0:
        return colors(cat())
    if t < 13.0:
        return colors(cat(mouth="smile"))
    if t < 13.6:
        return colors(cat("wink", mouth="smile"))
    if t < 14.5:
        return colors(cat(mouth="smile"))
    if t < 16.0:                                       # miaou
        whisk = int((t - 14.5) / 0.15) % 2
        ear = 14.6 <= t < 14.8 or 15.2 <= t < 15.4
        return colors(cat(mouth="open", whisk=whisk, ear=ear))
    if t < 17.0:
        return colors(cat())
    if t < 18.0:
        return colors(cat("half"))
    if t < 21.0:                                       # dodo : respiration lente
        b = 0.55 + 0.3 * math.cos((t - 18.0) / 1.5 * 2 * math.pi)
        return colors(cat("closed"), b)
    if t < 21.5:                                       # réveil
        return colors(cat(ear=t < 21.2))
    if t < 23.5:                                       # coeur qui bat
        p = (t - 21.5) % 1.0
        b = 1.0 if p < 0.15 or 0.3 <= p < 0.45 else 0.55
        return colors(HEART, b)
    if t < 26.0:
        return colors(cat("closed" if blink else "open", mouth="smile"))
    if t < 27.5:                                       # fondu de fin
        return colors(cat(mouth="smile"), max(0.0, 1 - (t - 26.0) / 1.5))
    return colors([["."] * N for _ in range(N)])


def cell_edges():
    """Bords en pixels des cellules : centrées sur les LEDs (calcul identique à l'application)."""
    xs = [round((MARGIN + i * PITCH) * SCALE) for i in range(N + 1)]            # 50 px par colonne
    centers = [(MARGIN + j * GAP) for j in range(N)]                            # y depuis le bas
    ys = [round(H - (c + GAP / 2) * SCALE) for c in reversed(centers)]          # haut de chaque ligne
    ys.append(round(H - (centers[0] - GAP / 2) * SCALE))
    return xs, ys


def render(grid, xs, ys):
    black = b"\x00\x00\x00"
    out = bytearray()
    out += black * W * ys[0]
    for r in range(N):
        row = bytearray(black * xs[0])
        for c in range(N):
            row += bytes(grid[r][c]) * (xs[c + 1] - xs[c])
        row += black * (W - xs[N])
        out += bytes(row) * (ys[r + 1] - ys[r])
    out += black * W * (H - ys[N])
    return bytes(out)


def main():
    dst = sys.argv[1]
    xs, ys = cell_edges()
    ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16",
                           "-preset", "slow", "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst],
                          stdin=subprocess.PIPE)
    expected = {}
    for f in range(int(DUR * FPS)):
        t = f / FPS
        g = frame(t)
        if f % 15 == 0:
            expected[f"{t:.2f}"] = g
        ff.stdin.write(render(g, xs, ys))
    ff.stdin.close()
    ff.wait()
    if len(sys.argv) > 2:
        json.dump(expected, open(sys.argv[2], "w"))
    print(f"{dst} : {W}x{H}, {DUR:.0f} s")


if __name__ == "__main__":
    main()
