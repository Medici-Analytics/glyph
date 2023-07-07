from __future__ import annotations

import struct

from enum import IntEnum, auto

PORT = 2313

class UNPACKERS:
    CURSOR_POSITION = struct.Struct("iff")
    GREET = struct.Struct("is")

class END(IntEnum):
    WHITE_MATE = auto()
    BLACK_MATE = auto()
    TIE = auto()
    DRAW = auto()
    INSUFFICIENT_MATERIAL = auto()

class Instructions(IntEnum):
    GREET = auto()
    CHAT = auto()
    DISCONNECT = auto()
    BOARD = auto()
    MOVE = auto()
    MATE = auto()
    INVALID_MOVE = auto()
    CURSOR_MOVE = auto()

class Data:
    def __init__(self, instruction: Instructions, data: bytes) -> None:
        self.instructions = instruction
        self.data = data

    def serialize(self) -> bytes:
        return self.instructions.to_bytes() + self.data

    @staticmethod
    def deserialize(data: bytes) -> Data:
        instruction = Instructions((data[0]))
        data = data[1:]
        return Data(instruction, data)
