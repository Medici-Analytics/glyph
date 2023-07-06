#!/usr/bin/python
import sys
import os
import math

import pygame
import pygame.font
from pygame import Surface

import client
from settings import Instructions
from settings import Data

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

class Camera:
    ROTATION_SPEED: int = 2

    def __init__(self, offset: list[int], rotation: int) -> None:
        self.offset = offset
        self.rotation = rotation

def split_stylesheet_into_chunks(stylesheet_path: str) -> list[Surface]:
    stylesheet = pygame.image.load(stylesheet_path)
    stylesheet_width, stylesheet_height = stylesheet.get_size()
    chunk_size = stylesheet_width

    num_chunks_rows = stylesheet_height // stylesheet_width

    surfaces = []

    for chunk_row in range(num_chunks_rows):
        start_x = 0
        end_x = start_x + chunk_size
        start_y = chunk_row * chunk_size
        end_y = start_y + chunk_size

        chunk_surface = pygame.Surface((chunk_size, chunk_size), pygame.SRCALPHA) # needs to have alphachannel or transparency overrides when blit

        chunk_surface.blit(stylesheet, (0, 0), (start_x, start_y, end_x, end_y))

        surfaces.append(chunk_surface)

    surfaces.reverse()
    return surfaces

def make_rotation_matrix(images: list[Surface], spread: int = 1) -> dict[int, Surface]:
    rotations: dict[int, Surface] = {}
    for rotation in range(0, MAX_ROTATIONS):
        rotation_surface = Surface((images[0].get_width() * 2, images[0].get_height() + len(images) * spread * 3), pygame.SRCALPHA)
        render_stack(rotation_surface, images, (rotation_surface.get_width() // 2, rotation_surface.get_height() // 2), int(rotation / MAX_ROTATIONS * 360))
        rotations[rotation] = rotation_surface

    return rotations

def render_stack(surf: Surface, images: list[Surface], pos: tuple[int, int], rotation:int, spread: int =1) -> None:
    for i, img in enumerate(images):
        rotated_img = pygame.transform.rotate(img, rotation)
        surf.blit(rotated_img, (pos[0] - rotated_img.get_width() // 2, pos[1] - rotated_img.get_height() // 2 - i * spread))

def get_rotation_index(degrees: int) -> int:
    return int(-degrees * MAX_ROTATIONS // 360) % MAX_ROTATIONS

def render_from_matrix(surf: Surface, matrix: dict[int, Surface], pos: tuple[int, int], rotation: int, camera: Camera, height: int = 0) -> None:
    rotation_offset = get_rotation_index(camera.rotation)
    final_rotation = (rotation + rotation_offset) % MAX_ROTATIONS

    img = matrix[final_rotation]

    x, y = pos
    camera_rotation_radians = math.radians(camera.rotation)

    camera_center_x = camera.offset[0] + display.get_width() // 2
    camera_center_y = camera.offset[1] + display.get_height() // 2

    # Calculate the offset from the center of the camera
    offset_x = (x - camera_center_x) * math.cos(camera_rotation_radians) - (y - camera_center_y) * math.sin(camera_rotation_radians)
    offset_y = (x - camera_center_x) * math.sin(camera_rotation_radians) + (y - camera_center_y) * math.cos(camera_rotation_radians) - height

    # Calculate the final rendering position relative to the center of the screen
    render_x = int(display.get_width() // 2 + offset_x - img.get_width() // 2)
    render_y = int(display.get_height() // 2 + offset_y - img.get_height() // 2)

    surf.blit(img, (render_x, render_y))

def make_asset_map(asset_path: str = ASSET_PATH) -> dict[str, dict[int, Surface]]:
    assert asset_path.endswith('/'), "asset path must end with '/' to signify directory path."
    return {img.replace(".png", ''): make_rotation_matrix(split_stylesheet_into_chunks(asset_path + img)) for img in os.listdir(asset_path)}


asset_map = make_asset_map()
cube = asset_map['cute_cube']
knight = asset_map['chr_knight']
frame = 0

camera = Camera([0,0], MAX_ROTATIONS//2)

def distance_from_camera(pos: tuple[int, int]) -> int:
    rot = math.radians(camera.rotation)
    sin = math.sin(rot)
    cos = math.cos(rot)
    if cos < 0 and sin < 0:
        return -pos[1] + -pos[0]
    elif cos < 0:
        return -pos[1]
    elif sin < 0:
        return -pos[0]
    return pos[1]

size = 24
map = []
for y in range(8):
    for x in range(8):
        map.append((x, y))

sock = client.make_socket()
client.run(sock)

while True:
    current_rotation = frame // DEBUG_ROTATION_SPEED % MAX_ROTATIONS
    display.fill((0,0,0))
    frame += 1

    for x, y in sorted(map, key=distance_from_camera):
        render_from_matrix(display, cube, (x * size, y * size), 0, camera)

    for x, y in sorted(map, key=distance_from_camera):
        render_from_matrix(display, knight, (x * size, y * size), 0, camera, size)

    rotation_debug = font_renderer.render(f'rotation: {get_rotation_index(camera.rotation)}', False, (255,255,255))
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

    if keys[pygame.K_q]:
        camera.rotation -= camera.ROTATION_SPEED

    if keys[pygame.K_e]:
        camera.rotation += camera.ROTATION_SPEED

    movement_speed = 10
    movement_vector = pygame.Vector2(0, 0)

    if keys[pygame.K_a]:
        movement_vector.x -= movement_speed

    if keys[pygame.K_d]:
        movement_vector.x += movement_speed

    if keys[pygame.K_w]:
        movement_vector.y -= movement_speed

    if keys[pygame.K_s]:
        movement_vector.y += movement_speed

    if keys[pygame.K_BACKSPACE]:
        data = Data(Instructions.CHAT, b'yo, testing')
        sock.sendall(data.serialize())

    camera.offset[0] += int(rotated_movement_vector.x)
    camera.offset[1] += int(rotated_movement_vector.y)

    screen.blit(pygame.transform.scale(display, screen.get_size()), (0,0))
    pygame.display.update()
    clock.tick(60)

