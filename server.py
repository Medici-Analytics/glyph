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
        self.connections = {}


    @property
    def next_id(self) -> int:
        n = self._next_id
        self._next_id += 1
        return n


    def sendto(self, packet: Packet, address) -> None:
        self.sock.sendto(packet.serialize(), address)


    def broadcast(self, packet: Packet) -> None:
        for connection in self.connections.copy().keys():
            self.sendto(packet, connection)


    def valid_join_request(self, packet: Packet) -> bool:
        return True


    def send_other_connections_to_new_connection(self, client_address) -> None:
        for connection in self.connections.values():
            print(f'sending {connection} to {client_address}')
            packet = Packet(
                PacketType.SEED_NEW_CONNECTION,
                0,
                PacketPayloadFormat.SEED_NEW_CONNECTION.pack(connection['id'], connection['name'].encode())
            )
            self.sendto(packet, client_address)


    def handle_request(self, data: bytes, client_address) -> None:
        packet = Packet.deserialize(data)
        if packet.packet_type == PacketType.JOIN_REQUEST:
            if self.valid_join_request(packet):
                name, = PacketPayloadFormat.JOIN_REQUEST.unpack(packet.payload)
                id = self.next_id
                new_player_packet = Packet(
                    PacketType.NEW_PARTICIPANT,
                    packet.sequence_number,
                    PacketPayloadFormat.NEW_PARTICIPANT.pack(id, name))

                self.send_other_connections_to_new_connection(client_address)
                self.broadcast(new_player_packet)

                self.connections[client_address] = {'name': name.decode(), 'id':id}
                response = Packet(
                    PacketType.JOIN_RESPONSE,
                    packet.sequence_number,
                    PacketPayloadFormat.JOIN_RESPONSE.pack(
                        ResponseCodes.ACCEPTED,
                        id
                    )
                )
                self.sendto(response, client_address)

        if packet.packet_type == PacketType.DISCONNECT:
            id, reason = PacketPayloadFormat.DISCONNECT.unpack(packet.payload)
            print(f'disconnect signal recieved from:{client_address}')
            print(id, reason)
            self.connections.pop(client_address)
            self.broadcast(packet)

        if packet.packet_type == PacketType.CURSOR_MOVE:
            self.broadcast(packet)

if __name__ == "__main__":
    server = Server('localhost')
    server.run()

