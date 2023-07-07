#!/usr/bin/python
import sys
import math

import pygame
import pygame.font
from pygame import Vector2

from client import Client

from camera import Camera

from engine import Engine

from selector import Selector

pygame.init()
pygame.font.init()

MAX_ROTATIONS = 90
DEBUG_FONT_SIZE = 14
DEBUG_MARGIN = 2
DEBUG_ROTATION_SPEED = 10
ASSET_PATH = 'assets/'


class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((1080, 720), 0, 32)
        self.display = pygame.Surface((600,720))

        self.font_renderer = pygame.font.SysFont("Arial", DEBUG_FONT_SIZE)

        self.clock = pygame.time.Clock()
        self.engine = Engine(self.display, MAX_ROTATIONS)
        self.camera = Camera([-100,-300], 45)
        self.asset_map = self.engine.make_asset_map(ASSET_PATH)

        self.size = 24
        self.map = []
        for y in range(8):
            for x in range(8):
                self.map.append((x, y))

        self.client = Client("localhost")
        self.selector = Selector(self.asset_map['selector'], Vector2(), self.engine)
        self.cube = self.asset_map['cute_cube']
        self.knight = self.asset_map['chr_knight']


    def _run(self) -> None:
        self.client.start()

        while True:
            self.display.fill((0,0,0))

            for x, y in sorted(self.map, key=self.camera.by_furthest_away):
                self.engine.render_from_matrix(self.display, self.cube, (x * self.size, y * self.size), 0, self.camera)

            for x, y in sorted(self.map, key=self.camera.by_furthest_away):
                self.engine.render_from_matrix(self.display, self.knight, (x * self.size, y * self.size), 0, self.camera, self.size)


            rotation_debug = self.font_renderer.render(f'rotation: {self.engine.get_rotation_index(self.camera.rotation)}', False, (255,255,255))
            asset_debug = self.font_renderer.render(f'assets loaded: {len(self.asset_map)}', False, (255,255,255))
            camera_debug = self.font_renderer.render(f'camera rotation: {self.camera.rotation}. camera sin/cos: {math.sin(math.radians(self.camera.rotation)):.2f}/{math.cos(math.radians(self.camera.rotation)):.2f}', False, (255,255,255))
            self.display.blit(rotation_debug, (0,0))
            self.display.blit(asset_debug, (0, DEBUG_FONT_SIZE + DEBUG_MARGIN))
            self.display.blit(camera_debug, (0, DEBUG_FONT_SIZE*2 + DEBUG_MARGIN))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                pygame.quit()

            for id, player in self.client.connections.items():
                if type(player.position) == tuple:
                    self.engine.render_from_matrix(
                        self.display,
                        self.asset_map['selector'],
                        player.position,
                        0,
                        self.camera,
                        self.size
                    )

            self.selector.handle_event(keys, self.camera)
            pos = self.selector.position.x, self.selector.position.y
            self.client.send_position(pos)
            self.selector.update()
            self.selector.render(self.display, self.camera)

            self.camera.handle_event(keys)

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

    def run(self) -> None:
        try:
            self._run()
        except BaseException as e:
            self.client.send_disconnect()
            self.client.stop()
            raise e


if __name__ == "__main__":
    game = Game()
    game.run()
