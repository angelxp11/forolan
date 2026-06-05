# ◈ FORO LAN ◈

Sistema de foro local desarrollado en Python mediante arquitectura Cliente-Servidor sobre red LAN utilizando sockets TCP.

## Descripción

FORO LAN es una aplicación de comunicación local diseñada para funcionar dentro de una red de área local (LAN). Permite que múltiples usuarios se conecten simultáneamente a un servidor central para publicar mensajes, visualizar el historial de conversaciones y participar en discusiones en tiempo real.

El proyecto fue desarrollado como trabajo final de Telemática con el objetivo de aplicar conceptos fundamentales de redes y sistemas distribuidos.

---

## Características

* Comunicación Cliente-Servidor mediante TCP.
* Interfaz gráfica desarrollada con Tkinter.
* Historial persistente almacenado en formato JSON.
* Múltiples clientes conectados simultáneamente.
* Gestión de concurrencia mediante hilos (threading).
* Difusión automática de mensajes a todos los usuarios.
* Registro de eventos de conexión y desconexión.
* Visualización de usuarios conectados.
* Recuperación automática del historial al conectarse.

---

## Arquitectura

```text
                 ┌─────────────────┐
                 │    SERVIDOR     │
                 │ TCP Puerto 5555 │
                 └────────┬────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼

   Cliente 1        Cliente 2        Cliente N
      TCP              TCP              TCP
```

---

## Tecnologías utilizadas

* Python 3.11+
* Socket Programming
* TCP/IP
* JSON
* Threading
* Tkinter

---

## Protocolo de transporte

Se seleccionó TCP debido a que:

* Garantiza la entrega de los mensajes.
* Mantiene el orden de transmisión.
* Detecta errores durante la comunicación.
* Proporciona una conexión confiable entre clientes y servidor.

Estas características son ideales para una aplicación tipo foro donde ningún mensaje debe perderse.

---

## Persistencia de datos

Todos los mensajes son almacenados en:

```text
historial_foro.json
```

Cada mensaje contiene:

```json
{
  "nickname": "Usuario",
  "mensaje": "Contenido del mensaje",
  "timestamp": "2026-06-05 11:30:00"
}
```

---

## Ejecución

### 1. Iniciar el servidor

```bash
python server.py
```

Salida esperada:

```text
SERVIDOR DE FORO LAN
Host: 0.0.0.0
Puerto: 5555
Historial: historial_foro.json
```

---

### 2. Iniciar un cliente

```bash
python client.py
```

Posteriormente ingresar:

* Dirección IP del servidor.
* Nickname del usuario.

---

## Comunicación

Formato de intercambio:

```json
{
  "nickname": "Jose",
  "mensaje": "Hola a todos",
  "timestamp": "2026-06-05 11:30:00"
}
```

Mensajes especiales del sistema:

```json
{
  "tipo": "join",
  "nickname": "Jose"
}
```

```json
{
  "tipo": "sistema",
  "mensaje": "Jose se unió al foro."
}
```

---

## Manejo de concurrencia

El servidor crea un hilo independiente para cada cliente conectado.

Ventajas:

* Atención simultánea de múltiples usuarios.
* Respuesta en tiempo real.
* Escalabilidad para entornos LAN académicos.

---

## Estructura del proyecto

```text
ForoLAN/
│
├── server.py
├── client.py
├── historial_foro.json
└── README.md
```

---

## Pruebas realizadas

Se verificó:

* Conexión simultánea de múltiples clientes.
* Persistencia de mensajes.
* Recuperación de historial.
* Difusión de publicaciones en tiempo real.
* Comunicación mediante red LAN.

---

## Conceptos telemáticos aplicados

* Arquitectura Cliente-Servidor.
* Protocolo TCP.
* Direccionamiento IP.
* Puertos lógicos.
* Multiplexación de conexiones.
* Concurrencia mediante hilos.
* Persistencia de información.
* Comunicación distribuida.

---

## Autores

Trabajo Final de Telemática

Universidad de Investigacion y desarrollo - UDI

Integrantes:

* Jose Angel Bermúdez Choperena
* Karen Marcela Linares
* Daniel Fernando Martinez Arias
* Juan Sebastian Díaz Mantilla

Fecha: Junio 2026
