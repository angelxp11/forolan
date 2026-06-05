import socket
import threading
import json
from datetime import datetime

SERVER_IP = input("IP del servidor: ")
PORT = 5555

nickname = input("Ingrese su nickname: ")

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((SERVER_IP, PORT))


def recibir():
    while True:
        try:
            mensaje = cliente.recv(4096).decode("utf-8")

            if mensaje:
                print("\n" + mensaje)
        except:
            break


def enviar():
    while True:
        texto = input()

        mensaje = {
            "nickname": nickname,
            "mensaje": texto,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        cliente.send(json.dumps(mensaje).encode("utf-8"))


hilo_recibir = threading.Thread(target=recibir)
hilo_recibir.daemon = True
hilo_recibir.start()

print("\nConectado al foro.")
print("Escriba mensajes y presione ENTER.\n")

enviar()