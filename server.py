import socket
import threading
import json
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5555

clientes = []
lock = threading.Lock()

ARCHIVO = "conversaciones.txt"


def guardar_mensaje(mensaje):
    with lock:
        with open(ARCHIVO, "a", encoding="utf-8") as archivo:
            archivo.write(mensaje + "\n")


def enviar_historial(cliente):
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as archivo:
            historial = archivo.read()

        if historial:
            cliente.send(("===== HISTORIAL =====\n" + historial +
                         "\n=====================\n").encode("utf-8"))
    except FileNotFoundError:
        pass


def broadcast(mensaje, cliente_origen=None):
    for cliente in clientes[:]:
        if cliente != cliente_origen:
            try:
                cliente.send(mensaje.encode("utf-8"))
            except:
                if cliente in clientes:
                    clientes.remove(cliente)


def manejar_cliente(cliente):
    enviar_historial(cliente)

    while True:
        try:
            datos = cliente.recv(4096)

            if not datos:
                break

            mensaje_json = json.loads(datos.decode("utf-8"))

            nickname = mensaje_json["nickname"]
            contenido = mensaje_json["mensaje"]
            timestamp = mensaje_json["timestamp"]

            mensaje_formateado = f"[{timestamp}] <{nickname}>: {contenido}"

            print(mensaje_formateado)

            guardar_mensaje(mensaje_formateado)

            broadcast(mensaje_formateado)

        except:
            break

    if cliente in clientes:
        clientes.remove(cliente)

    cliente.close()


def iniciar_servidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()

    print(f"Servidor iniciado en puerto {PORT}")
    print("Esperando conexiones...\n")

    while True:
        cliente, direccion = servidor.accept()

        print(f"Cliente conectado: {direccion}")

        clientes.append(cliente)

        hilo = threading.Thread(
            target=manejar_cliente,
            args=(cliente,)
        )
        hilo.start()


if __name__ == "__main__":
    iniciar_servidor()