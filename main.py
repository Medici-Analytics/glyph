#!/usr/bin/python
import sys
import math

import pygame
import pygame.font
from pygame import Vector2

import client
from settings import Instructions
from settings import Data

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

screen = pygame.display.set_mode((1080, 720), 0, 32)
display = pygame.Surface((600,720))

font_renderer = pygame.font.SysFont("Arial", DEBUG_FONT_SIZE)

clock = pygame.time.Clock()
engine = Engine(display, MAX_ROTATIONS)
camera = Camera([0,0], 45)
asset_map = engine.make_asset_map(ASSET_PATH)

size = 24
map = []
for y in range(8):
    for x in range(8):
        map.append((x, y))

sock = client.make_socket()
client.run(sock)
selector = Selector(asset_map['green_cube'], Vector2(), engine)
cube = asset_map['cute_cube']
knight = asset_map['chr_knight']

while True:
    display.fill((0,0,0))

    for x, y in sorted(map, key=camera.by_furthest_away):
        engine.render_from_matrix(display, cube, (x * size, y * size), 0, camera)

    for x, y in sorted(map, key=camera.by_furthest_away):
        engine.render_from_matrix(display, knight, (x * size, y * size), 0, camera, size)


    rotation_debug = font_renderer.render(f'rotation: {engine.get_rotation_index(camera.rotation)}', False, (255,255,255))
    asset_debug = font_renderer.render(f'assets loaded: {len(asset_map)}', False, (255,255,255))
    camera_debug = font_renderer.render(f'camera rotation: {camera.rotation}. camera sin/cos: {math.sin(math.radians(camera.rotation)):.2f}/{math.cos(math.radians(camera.rotation)):.2f}', False, (255,255,255))
    display.blit(rotation_debug, (0,0))
    display.blit(asset_debug, (0, DEBUG_FONT_SIZE + DEBUG_MARGIN))
    display.blit(camera_debug, (0, DEBUG_FONT_SIZE*2 + DEBUG_MARGIN))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        pygame.quit()

    if keys[pygame.K_BACKSPACE]:
        data = Data(Instructions.CHAT, b'yo, testing')
        sock.sendall(data.serialize())

    selector.handle_event(keys)
    selector.update()
    selector.render(display, camera)

    camera.handle_event(keys)

    screen.blit(pygame.transform.scale(display, screen.get_size()), (0,0))
    pygame.display.update()
    clock.tick(60)

