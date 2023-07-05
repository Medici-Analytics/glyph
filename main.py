#!/usr/bin/python
import sys
import os

import pygame
from pygame import Surface

pygame.init()

MAX_ROTATIONS = 16

screen = pygame.display.set_mode((500, 500), 0, 32)
display = pygame.Surface((100,100))

clock = pygame.time.Clock()

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
        rotation_surface = Surface((images[0].get_width(), images[0].get_height() + len(images)* spread))
        render_stack(rotation_surface, images, (rotation_surface.get_width() // 2, rotation_surface.get_height() // 2), int(rotation / MAX_ROTATIONS * 360))
        rotations[rotation] = rotation_surface

    return rotations

def render_stack(surf: Surface, images: list[Surface], pos: tuple[int, int], rotation:int, spread: int =1) -> None:
    for i, img in enumerate(images):
        rotated_img = pygame.transform.rotate(img, rotation)
        surf.blit(rotated_img, (pos[0] - rotated_img.get_width() // 2, pos[1] - rotated_img.get_height() // 2 - i * spread))

def render_from_matrix(surf: Surface, matrix: dict[int, Surface], pos:tuple[int, int], rotation: int) -> None:
    img = matrix[rotation]
    surf.blit(img, (pos[0] - img.get_width() // 2, pos[1] - img.get_height() // 2))

images = split_stylesheet_into_chunks("./assets/chr_knight.png")
frame = 0

image_matrix = make_rotation_matrix(images)

while True:
    display.fill((0,0,0))
    frame += 1
    render_from_matrix(display, image_matrix, (display.get_width() // 2, display.get_height() // 2), frame // 10 % MAX_ROTATIONS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.blit(pygame.transform.scale(display, screen.get_size()), (0,0))
    pygame.display.update()
    clock.tick(60)

