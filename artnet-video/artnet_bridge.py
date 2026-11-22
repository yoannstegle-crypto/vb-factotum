#!/usr/bin/env python3
"""
Relais Video -> Art-Net pour WLED.

- Sert la page index.html sur http://localhost:8080
- Recoit les images (pixels RGB) envoyees par la page (POST /frame)
- Les decoupe en univers Art-Net (170 LEDs RGB max par univers)
  et les envoie en UDP (port 6454) au boitier WLED.

Aucune dependance : uniquement la bibliotheque standard de Python 3.
Lancement : double-clic sur lancer.bat (Windows) ou `python artnet_bridge.py`.
"""

import ipaddress
import json
import os
import socket
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HTTP_PORT = 8080
ARTNET_PORT = 6454
LEDS_PER_UNIVERSE = 170          # 170 x 3 = 510 canaux sur 512
MAX_FRAME_BYTES = 3 * 170 * 64   # garde-fou : 64 univers max

HERE = os.path.dirname(os.path.abspath(__file__))

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sequence = 0
stats = {"frames": 0, "packets": 0, "last_error": None}


def artnet_dmx_packet(universe: int, data: bytes, seq: int) -> bytes:
    """Construit un paquet ArtDmx (OpCode 0x5000)."""
    if len(data) % 2:
        data += b"\x00"  # la longueur doit etre paire
    return (
        b"Art-Net\x00"
        + (0x5000).to_bytes(2, "little")   # OpCode ArtDmx
        + (14).to_bytes(2, "big")          # Version du protocole
        + bytes([seq, 0])                  # Sequence, Physical
        + bytes([universe & 0xFF, (universe >> 8) & 0x7F])  # SubUni, Net
        + len(data).to_bytes(2, "big")
        + data
    )


def send_frame(ip: str, start_universe: int, rgb: bytes) -> int:
    global sequence
    sequence = sequence % 255 + 1  # 1..255 (0 = sequence desactivee)
    chunk = LEDS_PER_UNIVERSE * 3
    count = 0
    for i in range(0, len(rgb), chunk):
        pkt = artnet_dmx_packet(start_universe + i // chunk, rgb[i:i + chunk], sequence)
        udp.sendto(pkt, (ip, ARTNET_PORT))
        count += 1
    return count


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # console silencieuse
        pass

    def _reply(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                self._reply(200, f.read(), "text/html; charset=utf-8")
        elif path == "/status":
            self._reply(200, json.dumps(stats).encode(), "application/json")
        else:
            self._reply(404, b"introuvable")

    def do_POST(self):
        url = urlparse(self.path)
        if url.path != "/frame":
            self._reply(404, b"introuvable")
            return
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > MAX_FRAME_BYTES:
            self.close_connection = True
            self._reply(413, b"taille d'image invalide")
            return
        data = self.rfile.read(length)
        q = parse_qs(url.query)
        try:
            ip = str(ipaddress.IPv4Address(q.get("ip", [""])[0]))
            uni = int(q.get("uni", ["1"])[0])
            if not 0 <= uni <= 32767:
                raise ValueError("univers hors limites")
        except ValueError as e:
            self._reply(400, f"parametre invalide : {e}".encode())
            return
        try:
            n = send_frame(ip, uni, data)
            stats["frames"] += 1
            stats["packets"] += n
            stats["last_error"] = None
            self._reply(204)
        except OSError as e:
            stats["last_error"] = str(e)
            self._reply(502, f"envoi UDP impossible : {e}".encode())


def main():
    try:
        server = ThreadingHTTPServer(("127.0.0.1", HTTP_PORT), Handler)
    except OSError as e:
        print(f"Impossible d'ouvrir le port {HTTP_PORT} : {e}")
        print("Le relais tourne peut-etre deja dans une autre fenetre.")
        input("Entree pour quitter...")
        sys.exit(1)
    url = f"http://localhost:{HTTP_PORT}/"
    print("=" * 56)
    print(" Relais Video -> Art-Net actif")
    print(f" Ouvre : {url}")
    print(" Laisse cette fenetre ouverte. Ctrl+C pour arreter.")
    print("=" * 56)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArret.")


if __name__ == "__main__":
    main()
