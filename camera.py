import pygame

class Camera:
    ROTATION_SPEED: int = 2

    def __init__(self, offset: list[int], rotation: int) -> None:
        self.offset = offset
        self.rotation = rotation
        self.movement_speed = 10

    def handle_event(self, keys) -> None:
        movement_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_q]:
            self.rotation -= self.ROTATION_SPEED

        if keys[pygame.K_e]:
            self.rotation += self.ROTATION_SPEED

        if keys[pygame.K_a]:
            movement_vector.x -= self.movement_speed

        if keys[pygame.K_d]:
            movement_vector.x += self.movement_speed

        if keys[pygame.K_w]:
            movement_vector.y -= self.movement_speed

        if keys[pygame.K_s]:
            movement_vector.y += self.movement_speed

        rotated_movement_vector = movement_vector.rotate(-self.rotation)
        self.offset[0] += int(rotated_movement_vector.x)
        self.offset[1] += int(rotated_movement_vector.y)
