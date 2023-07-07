from __future__ import annotations

import struct

from enum import IntEnum, auto

from udpeasy import Packet as pckt

PORT = 2313

class PacketPayloadFormat:
    CURSOR_POSITION = struct.Struct("iff")
    GREET = struct.Struct("32s")
    JOIN_RESPONSE = struct.Struct('ii')
    JOIN_REQUEST = struct.Struct('32s')

class ResponseCodes(IntEnum):
    ACCEPTED = auto()
    DENIED = auto()

class END(IntEnum):
    WHITE_MATE = auto()
    BLACK_MATE = auto()
    TIE = auto()
    DRAW = auto()
    INSUFFICIENT_MATERIAL = auto()

class PacketType(IntEnum):
    JOIN_REQUEST = auto()
    JOIN_RESPONSE = auto()
    GREET = auto()
    CHAT = auto()
    DISCONNECT = auto()
    BOARD = auto()
    MOVE = auto()
    MATE = auto()
    INVALID_MOVE = auto()
    CURSOR_MOVE = auto()

class Packet(pckt):
    MAGIC_NUMBER = 0x22AF432E
    def __init__(self, packet_type, sequence_number, payload) -> None:
        super().__init__(packet_type, sequence_number, payload)

    @classmethod
    def deserialize(cls, serialized_data) -> Packet:
        if len(serialized_data) < Packet.HEADER_SIZE:
            raise ValueError("Invalid packet - packet is too short")

        magic_number, time, packet_type, sequence_number, payload_length = struct.unpack('IIIII', serialized_data[:Packet.HEADER_SIZE])

        if magic_number != Packet.MAGIC_NUMBER:
            print(magic_number, Packet.MAGIC_NUMBER)
            raise ValueError("Invalid packet - magic number mis-match of packets. \npacket will be disqualified")
        payload = serialized_data[Packet.HEADER_SIZE: Packet.HEADER_SIZE+ payload_length]

        packet = Packet(packet_type, sequence_number, payload)
        packet.time = time
        return packet
