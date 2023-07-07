#!/usr/bin/python
from __future__ import annotations

import threading

from settings import PORT
from settings import PacketType
from settings import PacketPayloadFormat
from settings import ResponseCodes
from settings import DisconnectCodes
from settings import Packet

from udpeasy import Client as cl

def decode(str: bytes) -> str:
    return str.decode().encode().decode()


class Client(cl):

    def __init__(self, host: str, port: int = PORT) -> None:
        super().__init__(host, port)
        self.accepted_connection = False
        self.name: str = "yo"
        self.connections = {}

    def request_join(self) -> None:
        request_packet = Packet(
            PacketType.JOIN_REQUEST,
            self.sequence_number,
            PacketPayloadFormat.JOIN_REQUEST.pack(self.name.encode())
        )
        self.send(request_packet)


    def send(self, packet: Packet) -> None:
        self.sock.sendto(packet.serialize(), self.addr)


    def send_disconnect(self, reason: DisconnectCodes = DisconnectCodes.GRACEFUL) -> None:
        disconnect_packet = Packet(
            PacketType.DISCONNECT,
            self.sequence_number,
            PacketPayloadFormat.DISCONNECT.pack(self.id, reason)
                                   )
        self.sock.sendto(disconnect_packet.serialize(), self.addr)


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


            if not self.accepted_connection:
                pass

            if packet.packet_type == PacketType.SEED_NEW_CONNECTION:
                id, name = PacketPayloadFormat.SEED_NEW_CONNECTION.unpack(packet.payload)
                name = decode(name)
                self.connections[id] = name

            if packet.packet_type == PacketType.NEW_PARTICIPANT:
                id, name = PacketPayloadFormat.NEW_PARTICIPANT.unpack(packet.payload)
                name = decode(name)
                self.connections[id] = name
                print(f'new connection!\t{name} has joined!')

            if packet.packet_type == PacketType.DISCONNECT:
                id, reason = PacketPayloadFormat.DISCONNECT.unpack(packet.payload)
                print(f'{id}: {self.connections[id]} has disconnected!\treason: {reason}')
                self.connections.pop(id)

            if self.die:
                self.dead = True


    def start(self) -> None:
        thread = threading.Thread(target=self.run_loop, daemon=True)
        thread.start()

if __name__ == "__main__":
    server = Client('localhost')
    server.start()

