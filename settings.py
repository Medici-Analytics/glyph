from __future__ import annotations

from enum import IntEnum, auto

PORT = 2313

class Instructions(IntEnum):
    GREET = auto()
    CHAT = auto()
    DISCONNECT = auto()
    BOARD = auto()

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
