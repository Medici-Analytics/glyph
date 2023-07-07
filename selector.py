import pygame
from pygame import Surface
from pygame import Vector2

from engine import Engine

from camera import Camera

class Selector:
    MOVE_DELAY = 100
    MOVE_INTERVAL = 120
    HEIGHT = 24

    def __init__(self, asset: dict[int, Surface], position: Vector2, engine: Engine, step_size: int = 24) -> None:
        self.asset = asset
        self.position = position
        self.movement_vector = Vector2()
        self.move_timer = 0
        self.step_size = step_size
        self.engine = engine

    def handle_event(self, keys, camera: Camera | None = None) -> None:
        if keys[pygame.K_LEFT]:
            self.movement_vector.x = -self.step_size

        elif keys[pygame.K_RIGHT]:
            self.movement_vector.x = self.step_size

        else:
            self.movement_vector.x = 0

        if keys[pygame.K_UP]:
            self.movement_vector.y = -self.step_size

        elif keys[pygame.K_DOWN]:
            self.movement_vector.y = self.step_size

        else:
            self.movement_vector.y = 0


        if camera != None:
            self.movement_vector = camera.move_relative(self.movement_vector)

    def update(self) -> None:
        current_time = pygame.time.get_ticks()

        if self.movement_vector.length() > 0 and current_time - self.move_timer > Selector.MOVE_INTERVAL:
            self.position += self.movement_vector
            self.move_timer = current_time


    def render(self, dest: Surface, camera: Camera) -> None:
        self.engine.render_from_matrix(dest, self.asset, (self.position.x, self.position.y), 0, camera, Selector.HEIGHT)
