import socket
import threading
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
HOST      = "0.0.0.0"   # Escuchar en todas las interfaces IPv4 disponibles
PORT      = 5555         # Puerto TCP fijo para conexiones de clientes
HISTORIAL = "historial_foro.json"

# ─────────────────────────────────────────────
#  PALETA ANSI (solo para logs del servidor)
# ─────────────────────────────────────────────
R      = "\033[0m"
B      = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
GRAY   = "\033[90m"
WHITE  = "\033[97m"

def log(nivel, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    colores = {"INFO": GREEN, "WARN": YELLOW, "ERROR": RED, "CONN": CYAN}
    c = colores.get(nivel, WHITE)
    print(f"  {GRAY}{ts}{R}  {c}{B}[{nivel}]{R}  {msg}")

# ─────────────────────────────────────────────
#  ESTADO GLOBAL
# ─────────────────────────────────────────────
clientes = {}   # sock -> nickname
lock     = threading.Lock()

# ─────────────────────────────────────────────
#  HISTORIAL
# ─────────────────────────────────────────────
def cargar_historial():
    if os.path.exists(HISTORIAL):
        try:
            with open(HISTORIAL, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def guardar_mensaje(datos: dict):
    hist = cargar_historial()
    hist.append(datos)
    with open(HISTORIAL, "w", encoding="utf-8") as f:
        json.dump(hist, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────
#  BROADCAST
# ─────────────────────────────────────────────
def broadcast(datos: dict, excluir=None):
    # Envío de datos a todos los clientes conectados, excepto el opcionalmente excluido.
    # Usamos JSON con separador de línea para que el cliente pueda parsear mensajes
    # concatenados en el stream TCP.
    raw = (json.dumps(datos, ensure_ascii=False) + "\n").encode("utf-8")
    with lock:
        muertos = []
        for sock in clientes:
            if sock is excluir:
                continue
            try:
                sock.send(raw)
            except:
                muertos.append(sock)
        for s in muertos:
            _desconectar_silencioso(s)

def _desconectar_silencioso(sock):
    clientes.pop(sock, None)
    try:
        sock.close()
    except:
        pass

def enviar_a(sock, datos: dict):
    try:
        sock.send((json.dumps(datos, ensure_ascii=False) + "\n").encode("utf-8"))
    except:
        pass

# ─────────────────────────────────────────────
#  MANEJO DE CLIENTE
# ─────────────────────────────────────────────
def manejar_cliente(sock, addr):
    nick = None
    try:
        # ── Historial inicial ──────────────────
        # Cuando un cliente se conecta, el servidor envía el historial de chat
        # para que el usuario vea los últimos mensajes antes de continuar.
        hist = cargar_historial()
        if hist:
            enviar_a(sock, {"tipo": "historial_inicio", "mensaje": ""})
            for m in hist[-50:]:   # últimos 50 mensajes
                enviar_a(sock, m)
            enviar_a(sock, {"tipo": "historial_fin", "mensaje": ""})

        # ── Loop de recepción ──────────────────
        # El servidor lee del socket en un loop infinito hasta que el cliente
        # cierra la conexión o ocurre un error.
        buffer = ""
        while True:
            data = sock.recv(4096).decode("utf-8")
            if not data:
                break
            buffer += data

            while "\n" in buffer or buffer:
                # Intentar parsear lo que hay
                try:
                    datos = json.loads(buffer.strip())
                    buffer = ""
                except json.JSONDecodeError:
                    # Si no hay \n todavía, esperar más datos
                    if "\n" not in buffer:
                        break
                    linea, buffer = buffer.split("\n", 1)
                    try:
                        datos = json.loads(linea.strip())
                    except:
                        continue

                # ── Procesar mensaje ───────────
                tipo = datos.get("tipo", "mensaje")

                if tipo == "join":
                    nick = datos.get("nickname", f"user_{addr[1]}")
                    with lock:
                        clientes[sock] = nick
                    log("CONN", f"{GREEN}{nick}{R} se conectó desde {addr[0]}:{addr[1]}")
                    aviso = {
                        "tipo": "sistema",
                        "mensaje": f"{nick} se unió al foro.",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    broadcast(aviso)

                else:
                    # Mensaje normal de chat
                    if nick is None:
                        nick = datos.get("nickname", f"user_{addr[1]}")
                        with lock:
                            clientes[sock] = nick

                    guardar_mensaje(datos)
                    log("INFO", f"{CYAN}{nick}{R}: {datos.get('mensaje','')[:60]}")
                    broadcast(datos, excluir=None)   # el servidor retransmite a todos incluido emisor

                if not buffer:
                    break

    except Exception as e:
        log("ERROR", f"{addr} — {e}")
    finally:
        with lock:
            nombre = clientes.pop(sock, nick or str(addr))
        try:
            sock.close()
        except:
            pass
        if nombre:
            log("CONN", f"{YELLOW}{nombre}{R} se desconectó.")
            broadcast({
                "tipo": "sistema",
                "mensaje": f"{nombre} abandonó el foro.",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

# ─────────────────────────────────────────────
#  BANNER SERVIDOR
# ─────────────────────────────────────────────
def banner():
    import os
    w = 60
    print()
    print(f"  {CYAN}{'═'*w}{R}")
    print(f"  {CYAN}║{R}{B}{'  SERVIDOR DE FORO LAN':^{w-2}}{R}{CYAN}║{R}")
    print(f"  {CYAN}╠{'═'*w}╣{R}")
    print(f"  {CYAN}║{R}  {'Host:':<12}{WHITE}{HOST}{R:<{w-16}}{CYAN}  ║{R}")
    print(f"  {CYAN}║{R}  {'Puerto:':<12}{WHITE}{PORT}{R:<{w-16}}{CYAN}  ║{R}")
    print(f"  {CYAN}║{R}  {'Historial:':<12}{WHITE}{HISTORIAL}{R:<{w-16}}{CYAN}  ║{R}")
    print(f"  {CYAN}{'═'*w}{R}")
    print()

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    os.system("cls" if os.name == "nt" else "clear")
    banner()

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen(20)
    log("INFO", f"Escuchando en {WHITE}{HOST}:{PORT}{R}  —  esperando clientes...\n")

    try:
        # El servidor acepta conexiones TCP entrantes y crea un hilo por cliente.
        while True:
            conn, addr = servidor.accept()
            t = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        log("WARN", "Servidor detenido por el usuario.")
    finally:
        servidor.close()

if __name__ == "__main__":
    main()