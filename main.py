#!/usr/bin/python
import sys
import os

import pygame
from pygame import Surface

pygame.init()


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

def render_stack(surf: Surface, images: list[Surface], pos: tuple[int, int], rotation:int, spread: int =1):
    for i, img in enumerate(images):
        rotated_img = pygame.transform.rotate(img, rotation)
        surf.blit(rotated_img, (pos[0] - rotated_img.get_width() // 2, pos[1] - rotated_img.get_height() // 2 - i * spread))

images = split_stylesheet_into_chunks("./assets/chr_knight.png")
frame = 0

while True:
    display.fill((0,0,0))
    frame += 1
    render_stack(display, images, (display.get_width() // 2,display.get_height() // 2), frame)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
    screen.blit(pygame.transform.scale(display, screen.get_size()), (0,0))
    pygame.display.update()
    clock.tick(60)

