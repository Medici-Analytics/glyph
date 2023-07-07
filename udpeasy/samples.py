import struct

class SamplePacketType:
    MESSAGE = 1
    SCORE = 2
    COORDINATES = 3

class SamplePayloadFormat:
    MESSAGE = struct.Struct("32s")    # char[32]
    SCORE = struct.Struct("I")        # int
    COORDINATES = struct.Struct("II") # int, int
