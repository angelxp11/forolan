import socket
import threading
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, font as tkfont
from datetime import datetime

# ═══════════════════════════════════════════════════════════
#  PALETA  —  tema cyberpunk oscuro
# ═══════════════════════════════════════════════════════════
C = {
    "bg":        "#0d0f14",   # fondo principal
    "panel":     "#131720",   # paneles secundarios
    "border":    "#1e2535",   # bordes
    "accent":    "#00e5ff",   # cian neón
    "accent2":   "#7b2fff",   # púrpura
    "green":     "#00ff9d",   # verde neón
    "yellow":    "#ffd60a",   # amarillo
    "red":       "#ff3d5e",   # rojo
    "text":      "#cdd6f4",   # texto normal
    "text_dim":  "#585b70",   # texto apagado
    "bubble_me": "#1a2540",   # burbuja propia
    "bubble_ot": "#1a1f2e",   # burbuja otros
    "input_bg":  "#0f1219",   # fondo input
    "scrollbar": "#1e2535",
}

NICK_COLORS = [
    "#00e5ff", "#00ff9d", "#ffd60a", "#ff7f50",
    "#c0a0ff", "#ff6eb4", "#7fffd4", "#ff9966",
]
_nick_map = {}
_nick_idx = [0]
DEFAULT_PORT = 5555

def nick_color(nick):
    if nick not in _nick_map:
        _nick_map[nick] = NICK_COLORS[_nick_idx[0] % len(NICK_COLORS)]
        _nick_idx[0] += 1
    return _nick_map[nick]


# ═══════════════════════════════════════════════════════════
#  VENTANA DE LOGIN
# ═══════════════════════════════════════════════════════════
class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("FORO LAN — Conexión")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)
        self.result = None
        self._build()
        # Centrar
        self.root.update_idletasks()
        w, h = 440, 500
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.root.mainloop()

    def _build(self):
        # Canvas decorativo de fondo (cuadrícula)
        cv = tk.Canvas(self.root, width=440, height=500,
                       bg=C["bg"], highlightthickness=0)
        cv.place(x=0, y=0)
        for x in range(0, 440, 30):
            cv.create_line(x, 0, x, 500, fill="#0e1117", width=1)
        for y in range(0, 500, 30):
            cv.create_line(0, y, 440, y, fill="#0e1117", width=1)

        frame = tk.Frame(self.root, bg=C["bg"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / título
        tk.Label(frame, text="◈ FORO LAN ◈",
                 font=("Courier", 26, "bold"),
                 fg=C["accent"], bg=C["bg"]).pack(pady=(0, 4))
        tk.Label(frame, text="Sistema de Mensajería en Red Local",
                 font=("Courier", 10),
                 fg=C["text_dim"], bg=C["bg"]).pack(pady=(0, 30))

        # Línea decorativa
        tk.Frame(frame, height=1, width=340, bg=C["accent"]).pack(pady=(0, 24))

        def field(parent, label, default="", show=None, readonly=False):
            tk.Label(parent, text=label,
                     font=("Courier", 9, "bold"),
                     fg=C["text_dim"], bg=C["bg"],
                     anchor="w").pack(fill="x", pady=(0, 4))
            var = tk.StringVar(value=default)
            e = tk.Entry(parent, textvariable=var,
                         font=("Courier", 13),
                         bg=C["input_bg"], fg=C["text"],
                         insertbackground=C["accent"],
                         relief="flat", bd=0,
                         highlightthickness=1,
                         highlightcolor=C["accent"],
                         highlightbackground=C["border"],
                         show=show or "",
                         state="readonly" if readonly else "normal")
            if readonly:
                e.configure(readonlybackground=C["input_bg"])
            e.pack(fill="x", ipady=8, pady=(0, 16))
            return var

        self.ip_var   = field(frame, "▸ IP DEL SERVIDOR", "127.0.0.1")
        self.port_var = field(frame, "▸ PUERTO (fijo)", str(DEFAULT_PORT), readonly=True)
        self.nick_var = field(frame, "▸ TU NICKNAME")

        # Botón conectar
        btn = tk.Button(frame,
                        text="CONECTAR  →",
                        font=("Courier", 12, "bold"),
                        bg=C["accent"], fg=C["bg"],
                        activebackground=C["green"],
                        activeforeground=C["bg"],
                        relief="flat", bd=0,
                        cursor="hand2",
                        command=self._conectar)
        btn.pack(fill="x", ipady=10, pady=(8, 0))
        self.root.bind("<Return>", lambda e: self._conectar())

        self.status = tk.Label(frame, text="",
                               font=("Courier", 9),
                               fg=C["red"], bg=C["bg"])
        self.status.pack(pady=(8, 0))

    def _conectar(self):
        ip   = self.ip_var.get().strip()
        nick = self.nick_var.get().strip()
        port = DEFAULT_PORT
        if not ip:
            self.status.config(text="✗  Ingresa la IP del servidor")
            return
        if not nick:
            self.status.config(text="✗  Ingresa un nickname")
            return

        self.status.config(text="Conectando...", fg=C["yellow"])
        self.root.update()

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((ip, port))
            s.settimeout(None)
            self.result = (s, ip, port, nick)
            self.root.destroy()
        except Exception as e:
            self.status.config(text=f"✗  {e}", fg=C["red"])


# ═══════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL DEL FORO
# ═══════════════════════════════════════════════════════════
class ForoWindow:
    def __init__(self, sock, server_ip, server_port, nick):
        self.sock        = sock
        self.server_ip   = server_ip
        self.server_port = server_port
        self.nick        = nick
        self.running     = True
        self.usuarios    = set()

        self.root = tk.Tk()
        self.root.title(f"FORO LAN  —  {nick}  @  {server_ip}:{server_port}")
        self.root.configure(bg=C["bg"])
        self.root.protocol("WM_DELETE_WINDOW", self._salir)

        # Tamaño y centrado
        w, h = 980, 680
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self.root.minsize(700, 500)

        self._build()
        self._hilo_rx()
        self._enviar_join()
        self.root.mainloop()

    # ── Layout ───────────────────────────────────────────
    def _build(self):
        # ── Topbar ──────────────────────────────────────
        topbar = tk.Frame(self.root, bg=C["panel"], height=48)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="◈ FORO LAN",
                 font=("Courier", 14, "bold"),
                 fg=C["accent"], bg=C["panel"]).pack(side="left", padx=18)

        self.lbl_status = tk.Label(topbar,
                                   text=f"● conectado  {self.server_ip}:{self.server_port}",
                                   font=("Courier", 9),
                                   fg=C["green"], bg=C["panel"])
        self.lbl_status.pack(side="left", padx=12)

        tk.Label(topbar,
                 text=f"usuario: {self.nick}",
                 font=("Courier", 9, "bold"),
                 fg=C["yellow"], bg=C["panel"]).pack(side="right", padx=18)

        # Separador top
        tk.Frame(self.root, height=1, bg=C["accent"]).pack(fill="x")

        # ── Cuerpo ──────────────────────────────────────
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # ── Sidebar ─────────────────────────────────────
        sidebar = tk.Frame(body, bg=C["panel"], width=180)
        sidebar.pack(side="right", fill="y")
        sidebar.pack_propagate(False)

        tk.Frame(sidebar, height=1, bg=C["border"]).pack(fill="x")
        tk.Label(sidebar, text="CONECTADOS",
                 font=("Courier", 8, "bold"),
                 fg=C["text_dim"], bg=C["panel"]).pack(pady=(14, 6))
        tk.Frame(sidebar, height=1, bg=C["border"]).pack(fill="x", padx=10)

        self.users_frame = tk.Frame(sidebar, bg=C["panel"])
        self.users_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Separador vertical
        tk.Frame(body, width=1, bg=C["border"]).pack(side="right", fill="y")

        # ── Panel de chat ────────────────────────────────
        chat_panel = tk.Frame(body, bg=C["bg"])
        chat_panel.pack(side="left", fill="both", expand=True)

        # Área de mensajes
        self.chat_area = tk.Text(
            chat_panel,
            bg=C["bg"], fg=C["text"],
            font=("Courier", 11),
            relief="flat", bd=0,
            wrap="word",
            state="disabled",
            cursor="arrow",
            selectbackground=C["border"],
            padx=14, pady=10,
        )
        self.chat_area.pack(fill="both", expand=True, side="top")

        # Scrollbar custom
        sb = tk.Scrollbar(self.chat_area, orient="vertical",
                          command=self.chat_area.yview,
                          bg=C["scrollbar"], troughcolor=C["bg"],
                          relief="flat", width=6)
        sb.pack(side="right", fill="y")
        self.chat_area.configure(yscrollcommand=sb.set)

        # Definir tags de texto
        self._setup_tags()

        # ── Input bar ────────────────────────────────────
        tk.Frame(chat_panel, height=1, bg=C["border"]).pack(fill="x")
        input_bar = tk.Frame(chat_panel, bg=C["input_bg"], height=56)
        input_bar.pack(fill="x", side="bottom")
        input_bar.pack_propagate(False)

        tk.Label(input_bar, text="▸",
                 font=("Courier", 14, "bold"),
                 fg=C["accent"], bg=C["input_bg"]).pack(side="left", padx=(14, 4))

        self.msg_var = tk.StringVar()
        self.entry = tk.Entry(
            input_bar,
            textvariable=self.msg_var,
            font=("Courier", 12),
            bg=C["input_bg"], fg=C["text"],
            insertbackground=C["accent"],
            relief="flat", bd=0,
        )
        self.entry.pack(side="left", fill="both", expand=True, ipady=6)
        self.entry.bind("<Return>", lambda e: self._enviar())
        self.entry.focus()

        btn_send = tk.Button(
            input_bar,
            text="ENVIAR",
            font=("Courier", 10, "bold"),
            bg=C["accent"], fg=C["bg"],
            activebackground=C["green"],
            activeforeground=C["bg"],
            relief="flat", bd=0,
            cursor="hand2",
            padx=18,
            command=self._enviar,
        )
        btn_send.pack(side="right", padx=10, pady=8)

    def _setup_tags(self):
        a = self.chat_area
        a.tag_config("hora",     foreground=C["text_dim"], font=("Courier", 9))
        a.tag_config("sistema",  foreground=C["yellow"],   font=("Courier", 10, "italic"))
        a.tag_config("hist_hdr", foreground=C["accent"],   font=("Courier", 9, "bold"))
        a.tag_config("yo",       foreground=C["green"],    font=("Courier", 11, "bold"))
        a.tag_config("msg_yo",   foreground="#a0d4ff",     font=("Courier", 11))
        a.tag_config("msg_ot",   foreground=C["text"],     font=("Courier", 11))
        a.tag_config("sep",      foreground=C["border"],   font=("Courier", 7))
        # tags de colores por nick (se crean dinámicamente)

    def _nick_tag(self, nick):
        tag = f"nick_{nick}"
        try:
            self.chat_area.tag_cget(tag, "foreground")
        except:
            self.chat_area.tag_config(tag, foreground=nick_color(nick),
                                      font=("Courier", 11, "bold"))
        return tag

    # ── Escritura en el área ──────────────────────────
    def _write(self, *parts):
        """parts = lista de (texto, tag)"""
        self.chat_area.configure(state="normal")
        for text, tag in parts:
            if tag:
                self.chat_area.insert("end", text, tag)
            else:
                self.chat_area.insert("end", text)
        self.chat_area.configure(state="disabled")
        self.chat_area.see("end")

    def _append_mensaje(self, datos: dict):
        nick = datos.get("nickname", "???")
        texto = datos.get("mensaje", "")
        ts = datos.get("timestamp", "")
        hora = ts[11:16] if len(ts) >= 16 else ts

        es_mio = nick == self.nick
        msg_tag = "msg_yo" if es_mio else "msg_ot"
        nick_tag = "yo" if es_mio else self._nick_tag(nick)
        sufijo = " (tú)" if es_mio else ""

        self._write(
            (f"  {hora}  ", "hora"),
            (f"{nick}{sufijo}", nick_tag),
            ("  »  ", "hora"),
            (f"{texto}\n", msg_tag),
            (f"  {'─' * 60}\n", "sep"),
        )

    def _append_sistema(self, msg: str):
        self._write(
            (f"\n  ◈  {msg}\n\n", "sistema"),
        )

    def _append_hist_header(self):
        self._write(
            (f"\n  {'━'*20} HISTORIAL {'━'*20}\n\n", "hist_hdr"),
        )

    def _append_hist_footer(self):
        self._write(
            (f"\n  {'━'*50}\n\n", "hist_hdr"),
        )

    # ── Sidebar de usuarios ───────────────────────────
    def _refresh_users(self):
        for w in self.users_frame.winfo_children():
            w.destroy()
        for u in sorted(self.usuarios):
            c = C["green"] if u == self.nick else nick_color(u)
            dot = "● " if u == self.nick else "○ "
            tk.Label(self.users_frame,
                     text=f"{dot}{u}",
                     font=("Courier", 10),
                     fg=c, bg=C["panel"],
                     anchor="w").pack(fill="x", pady=2)

    # ── Red: recibir ─────────────────────────────────
    def _hilo_rx(self):
        t = threading.Thread(target=self._recibir, daemon=True)
        t.start()

    def _recibir(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096).decode("utf-8")
                if not data:
                    break
                buffer += data
                while True:
                    try:
                        datos = json.loads(buffer.strip())
                        buffer = ""
                        self.root.after(0, self._procesar, datos)
                        break
                    except json.JSONDecodeError:
                        if "\n" in buffer:
                            linea, buffer = buffer.split("\n", 1)
                            try:
                                d = json.loads(linea.strip())
                                self.root.after(0, self._procesar, d)
                            except:
                                pass
                        else:
                            break
            except:
                break
        self.root.after(0, self._desconectado)

    def _procesar(self, datos: dict):
        tipo = datos.get("tipo", "mensaje")
        if tipo == "sistema":
            msg = datos.get("mensaje", "")
            self._append_sistema(msg)
            # Actualizar lista de usuarios
            if "se unió" in msg:
                nick = msg.split(" se unió")[0].strip()
                self.usuarios.add(nick)
                self._refresh_users()
            elif "abandonó" in msg:
                nick = msg.split(" abandonó")[0].strip()
                self.usuarios.discard(nick)
                self._refresh_users()
        elif tipo == "historial_inicio":
            self._append_hist_header()
        elif tipo == "historial_fin":
            self._append_hist_footer()
        else:
            nick = datos.get("nickname", "")
            if nick:
                self.usuarios.add(nick)
                self._refresh_users()
            self._append_mensaje(datos)

    def _desconectado(self):
        self.lbl_status.config(text="● desconectado", fg=C["red"])
        self._append_sistema("Conexión cerrada por el servidor.")

    # ── Red: enviar ──────────────────────────────────
    def _enviar_join(self):
        try:
            d = {"tipo": "join", "nickname": self.nick,
                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            self.sock.send((json.dumps(d) + "\n").encode("utf-8"))
            self.usuarios.add(self.nick)
            self._refresh_users()
        except:
            pass

    def _enviar(self):
        texto = self.msg_var.get().strip()
        if not texto:
            return
        self.msg_var.set("")
        datos = {
            "nickname": self.nick,
            "mensaje": texto,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        try:
            self.sock.send((json.dumps(datos) + "\n").encode("utf-8"))
        except:
            self._append_sistema("No se pudo enviar el mensaje.")

    def _salir(self):
        self.running = False
        try:
            self.sock.close()
        except:
            pass
        self.root.destroy()


# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
def main():
    login = LoginWindow()
    if login.result is None:
        return  # usuario cerró la ventana sin conectar
    sock, ip, port, nick = login.result
    ForoWindow(sock, ip, port, nick)

if __name__ == "__main__":
    main()