#!/usr/bin/python
from __future__ import annotations

import threading

from settings import PORT
from settings import PacketType
from settings import PacketPayloadFormat
from settings import ResponseCodes
from settings import Packet

from udpeasy import Client as cl

class Client(cl):

    def __init__(self, host: str, port: int = PORT) -> None:
        super().__init__(host, port)
        self.accepted_connection = False
        self.name: str = "yo"

    def request_join(self) -> None:
        request_packet = Packet(
            PacketType.JOIN_REQUEST,
            self.sequence_number,
            PacketPayloadFormat.JOIN_REQUEST.pack(self.name.encode())
        )
        self.send(request_packet)


    def send(self, packet: Packet) -> None:
        self.sock.sendto(packet.serialize(), self.addr)


    def run_loop(self) -> None:
        self.request_join()
        while not self.dead:
            data, addr = self.sock.recvfrom(1024)
            packet = Packet.deserialize(data)

            if packet.packet_type == PacketType.JOIN_RESPONSE:
                response, id = PacketPayloadFormat.JOIN_RESPONSE.unpack(packet.payload)

                if response == ResponseCodes.ACCEPTED:
                    self.id = id
                    self.accepted_connection = True
                    print(f'connected accepted!\nlogged in with id {id}')

                elif response == ResponseCodes.DENIED:
                    print("connected denied, sadge")
                    self.stop()


            if self.die:
                self.dead = True


    def start(self):
        thread = threading.Thread(target=self.run_loop)
        thread.start()

if __name__ == "__main__":
    server = Client('localhost')
    server.start()

