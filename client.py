#!/usr/bin/python
from __future__ import annotations

import threading

from dataclasses import dataclass

from settings import PORT
from settings import PacketType
from settings import PacketPayloadFormat
from settings import ResponseCodes
from settings import DisconnectCodes
from settings import Packet

from udpeasy import Client as cl

def decode(str: bytes) -> str:
    return str.decode().encode().decode()

@dataclass
class PlayerInfo:
    name: str
    id: int
    position: tuple[int, int] | None

class Client(cl):

    def __init__(self, host: str, port: int = PORT) -> None:
        super().__init__(host, port)
        self.accepted_connection = False
        self.name: str = "yo"
        self.connections: dict[int, PlayerInfo] = {}
        self.id = 0

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
        if not self.accepted_connection and self.id:
            pass
        disconnect_packet = Packet(
            PacketType.DISCONNECT,
            self.sequence_number,
            PacketPayloadFormat.DISCONNECT.pack(self.id, reason)
                                   )
        self.sock.sendto(disconnect_packet.serialize(), self.addr)

    def send_position(self, position: tuple[float, float]) -> None:
        if not self.accepted_connection:
            pass
        packet = Packet(
            PacketType.CURSOR_MOVE,
            self.sequence_number,
            PacketPayloadFormat.CURSOR_POSITION.pack(self.id, *position)
                                   )
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

            if packet.packet_type == PacketType.SEED_NEW_CONNECTION:
                id, name = PacketPayloadFormat.SEED_NEW_CONNECTION.unpack(packet.payload)
                name = decode(name)
                self.connections[id] = PlayerInfo(name, id, None)
                print(f'sourced existing person!\t{id}: {name}')

            if not self.accepted_connection:
                pass


            elif packet.packet_type == PacketType.NEW_PARTICIPANT:
                id, name = PacketPayloadFormat.NEW_PARTICIPANT.unpack(packet.payload)
                name = decode(name)
                self.connections[id] = PlayerInfo(name, id, None)
                print(f'new connection!\t{name} has joined!')

            elif packet.packet_type == PacketType.DISCONNECT:
                id, reason = PacketPayloadFormat.DISCONNECT.unpack(packet.payload)
                print(f'{id}: {self.connections[id].name} has disconnected!\treason: {reason}')
                self.connections.pop(id)

            elif packet.packet_type == PacketType.CURSOR_MOVE:
                id, x, y = PacketPayloadFormat.CURSOR_POSITION.unpack(packet.payload)
                if id != self.id and id in self.connections.keys():
                    self.connections[id].position = (x,y)

            if self.die:
                self.dead = True


    def start(self) -> None:
        thread = threading.Thread(target=self.run_loop, daemon=True)
        thread.start()

if __name__ == "__main__":
    server = Client('localhost')
    server.start()

