from abc import ABC, abstractmethod
import socket
import threading


class Client(ABC):
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.sequence_number = 0
        self.die = False
        self.dead = False

    @abstractmethod
    def start(self):
        thread = threading.Thread(target=self.run_loop())
        thread.start()

    def stop(self):
        self.die = True


    @abstractmethod
    def run_loop(self):
        ...

