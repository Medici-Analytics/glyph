#!/usr/bin/python

from udpeasy import Server as srvr

from settings import PORT
from settings import Packet
from settings import PacketType
from settings import PacketPayloadFormat
from settings import ResponseCodes


class Server(srvr):
    def __init__(self, host: str, port: int = PORT) -> None:
        super().__init__(host, port)
        self._next_id = 1

    @property
    def next_id(self) -> int:
        n = self._next_id
        self._next_id += 1
        return n


    def sendto(self, packet: Packet, address) -> None:
        self.sock.sendto(packet.serialize(), address)


    def handle_request(self, data: bytes, client_address) -> None:
        packet = Packet.deserialize(data)
        if packet.packet_type == PacketType.JOIN_REQUEST:
            name, = PacketPayloadFormat.JOIN_REQUEST.unpack(packet.payload)
            name = name.decode()

            response = Packet(
                PacketType.JOIN_RESPONSE,
                packet.sequence_number,
                PacketPayloadFormat.JOIN_RESPONSE.pack(
                    ResponseCodes.ACCEPTED,
                    self.next_id
                )
            )
            self.sendto(response, client_address)
            print(name)


if __name__ == "__main__":
    server = Server('localhost')
    server.run()

