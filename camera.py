class Camera:
    ROTATION_SPEED: int = 2

    def __init__(self, offset: list[int], rotation: int) -> None:
        self.offset = offset
        self.rotation = rotation
