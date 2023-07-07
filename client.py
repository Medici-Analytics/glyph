#!/usr/bin/python
from __future__ import annotations

import socket
import threading

from settings import Data
from settings import PORT
from settings import Instructions


class Client:

    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def handle_connection(self):
        while True:
            data = self.sock.recv(1024)
            data = Data.deserialize(data)
            print(data)

    def send(self, data: Data) -> None:
        self.sock.sendall(data.serialize())

    def run(self) -> Client:
        self.sock.connect(("localhost", PORT))
        thread = threading.Thread(target = self.handle_connection, daemon=True)
        thread.start()
        return self

