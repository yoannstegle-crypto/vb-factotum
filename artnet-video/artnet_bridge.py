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
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from concurrent.futures import ThreadPoolExecutor
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


# ---------------------------------------------------------------------------
# Detection des boitiers WLED sur le reseau
# ---------------------------------------------------------------------------
IP_RE = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})")
# pas de proxy pour joindre les boitiers (les PC d'entreprise en ont souvent un)
_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def local_interfaces():
    """Adresses IPv4 de ce PC : [{'name', 'ip', 'prefix'}]."""
    found = {}
    if sys.platform.startswith("win"):
        try:
            out = subprocess.run(["ipconfig"], capture_output=True, timeout=5,
                                 creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
            text = out.decode("cp850", errors="replace")
            name, pending = "", None
            for line in text.splitlines():
                if line and not line[0].isspace() and line.rstrip().endswith(":"):
                    name, pending = line.strip().rstrip(":").strip(), None
                    for w in ("Carte Ethernet ", "Carte réseau sans fil ", "Ethernet adapter ",
                              "Wireless LAN adapter "):
                        name = name.replace(w, "")
                    continue
                m = IP_RE.findall(line)
                if "IPv4" in line and m:
                    pending = m[-1]
                elif pending and m:
                    mask = m[-1]
                    try:
                        prefix = ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
                    except ValueError:
                        prefix = 24
                    found[pending] = {"name": name, "ip": pending, "prefix": prefix}
                    pending = None
        except Exception:
            pass
    else:
        try:
            out = subprocess.run(["ip", "-4", "-o", "addr", "show"], capture_output=True,
                                 text=True, timeout=5).stdout
            for line in out.splitlines():
                m = re.search(r"^\d+:\s+(\S+)\s+inet\s+(\S+)/(\d+)", line)
                if m:
                    found[m.group(2)] = {"name": m.group(1), "ip": m.group(2), "prefix": int(m.group(3))}
        except Exception:
            pass
    try:  # complement / repli
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            found.setdefault(ip, {"name": "", "ip": ip, "prefix": 16 if ip.startswith("169.254.") else 24})
    except OSError:
        pass
    if not found:  # dernier recours : adresse de la route par defaut
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
            s.close()
            found[ip] = {"name": "", "ip": ip, "prefix": 24}
        except OSError:
            pass
    return [i for i in found.values() if not i["ip"].startswith("127.")]


def probe_wled(ip, timeout=0.8):
    """Interroge http://ip/json/info ; renvoie un resume si c'est un WLED."""
    try:
        with _opener.open(f"http://{ip}/json/info", timeout=timeout) as r:
            j = json.loads(r.read(200_000).decode("utf-8", errors="replace"))
    except Exception:
        return None
    if not isinstance(j, dict) or "leds" not in j:
        return None
    leds = j.get("leds") or {}
    return {"ip": ip, "name": str(j.get("name", "WLED"))[:64], "ver": str(j.get("ver", ""))[:20],
            "leds": leds.get("count") if isinstance(leds, dict) else None,
            "mac": str(j.get("mac", ""))[:20], "via": "http"}


def artpoll(ifaces, wait=2.0):
    """Envoie un ArtPoll en diffusion et collecte les ArtPollReply (ip -> nom court)."""
    replies = {}
    try:
        rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rx.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        rx.bind(("", ARTNET_PORT))
        rx.settimeout(0.2)
    except OSError:
        return replies
    poll = b"Art-Net\x00" + (0x2000).to_bytes(2, "little") + (14).to_bytes(2, "big") + b"\x00\x00"
    own = {i["ip"] for i in ifaces}
    for i in ifaces:
        try:
            net = ipaddress.IPv4Network(f"{i['ip']}/{i['prefix']}", strict=False)
            tx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tx.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            tx.bind((i["ip"], 0))
            for dst in {"255.255.255.255", str(net.broadcast_address)}:
                tx.sendto(poll, (dst, ARTNET_PORT))
            tx.close()
        except OSError:
            pass
    end = time.time() + wait
    while time.time() < end:
        try:
            d, _ = rx.recvfrom(1024)
        except socket.timeout:
            continue
        except OSError:
            break
        if d[:8] == b"Art-Net\x00" and int.from_bytes(d[8:10], "little") == 0x2100 and len(d) >= 44:
            ip = ".".join(str(b) for b in d[10:14])
            if ip not in own:
                replies[ip] = d[26:44].split(b"\x00")[0].decode("latin-1", errors="replace")
    rx.close()
    return replies


def discover(extra_ip=None):
    ifaces = local_interfaces()
    targets = []
    for i in ifaces:
        base = ipaddress.IPv4Network(f"{i['ip']}/24", strict=False)
        targets += [str(h) for h in base.hosts() if str(h) != i["ip"]]
    if extra_ip:
        targets.insert(0, extra_ip)
    targets = list(dict.fromkeys(targets))[:1100]

    poll_result = {}
    t = threading.Thread(target=lambda: poll_result.update(artpoll(ifaces)))
    t.start()
    with ThreadPoolExecutor(max_workers=200) as ex:
        devices = {d["ip"]: d for d in ex.map(probe_wled, targets) if d}
    t.join()
    for ip, short in poll_result.items():
        if ip not in devices:
            d = probe_wled(ip, timeout=1.5) or {"ip": ip, "name": short or "Noeud Art-Net",
                                                "ver": "", "leds": None, "mac": ""}
            devices[ip] = d
        devices[ip]["via"] = "artnet+" + devices[ip].get("via", "")

    suggestion = None
    for i in ifaces:
        if i["ip"].startswith("169.254."):
            a, b, c, d = i["ip"].split(".")
            suggestion = {"iface": i["name"], "pc_ip": i["ip"],
                          "wled_ip": f"169.254.{c}.{50 if d != '50' else 51}", "mask": "255.255.0.0"}
            break
    return {"interfaces": ifaces, "devices": sorted(devices.values(), key=lambda d: d["ip"]),
            "suggestion": suggestion}


def safe_lan_ip(value):
    """IP privee / locale uniquement (on ne sonde que le reseau local)."""
    ip = ipaddress.IPv4Address(value)
    if not (ip.is_private or ip.is_link_local):
        raise ValueError("adresse hors reseau local")
    return str(ip)


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
        elif path in ("/discover", "/probe"):
            q = parse_qs(urlparse(self.path).query)
            try:
                ip = safe_lan_ip(q["ip"][0]) if q.get("ip", [""])[0] else None
            except ValueError as e:
                self._reply(400, str(e).encode())
                return
            if path == "/probe":
                if not ip:
                    self._reply(400, b"ip manquante")
                    return
                res = probe_wled(ip, timeout=2.0)
            else:
                res = discover(ip)
            self._reply(200, json.dumps(res).encode(), "application/json")
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
