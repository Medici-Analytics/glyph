#!/usr/bin/python

import socket
import threading

from settings import Data, Instructions, PORT

def make_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return sock

def handle_connection(sock: socket.socket):
    print("handling...")
    while True:
        data = sock.recv(1024)
        data = Data.deserialize(data)
        print(data)

def run(sock: socket.socket) -> None:
    sock.connect(("localhost", PORT))
    thread = threading.Thread(target = handle_connection, args=[sock], daemon=True)
    thread.start()

if __name__ == "__main__":
    data = Data(Instructions.GREET, b"Hello, world")
    sock = make_socket()

    sock.send(data.serialize())
    while True:
        data = Data(Instructions.CHAT, input().encode())
        sock.send(data.serialize())
