#!/usr/bin/python
from __future__ import annotations

import socket
import threading
from settings import Data, Instructions, PORT

client_lock = threading.Lock()
clients_connected: list[socket.socket] = []

def handle_client(client_socket: socket.socket, client_address: ...) -> None:
    with client_lock:
        clients_connected.append(client_socket)

    while True:
        data = client_socket.recv(1024)
        if not data:
            break

        packet = Data.deserialize(data)
        print(packet.data)
        if packet.instructions == Instructions.CHAT:
            [ client.send(packet.serialize()) for client in clients_connected]
            print('sending')

    with client_lock:
        clients_connected.remove(client_socket)
        print(f'client with ip: {client_address} has been disconnected')

    client_socket.close()

def make_socket_run(port: int = PORT) -> None:
    print('starting...')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", port))
    server_socket.listen(10)
    while True:
        client_connection, client_address = server_socket.accept()
        thread = threading.Thread(target = handle_client, args=[client_connection, client_address])
        thread.start()


if __name__ == "__main__":
    make_socket_run()
