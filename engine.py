import os
import math

import pygame
from pygame import Surface

from camera import Camera


class Engine:
    def __init__(self, display: Surface, max_rotations: int = 90) -> None:
        self.display = display
        self.max_rotations = max_rotations

    @staticmethod
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

    def make_rotation_matrix(self, images: list[Surface], spread: int = 1) -> dict[int, Surface]:
        rotations: dict[int, Surface] = {}
        for rotation in range(0, self.max_rotations):
            rotation_surface = Surface((images[0].get_width() * 2, images[0].get_height() + len(images) * spread * 3), pygame.SRCALPHA)
            self.render_stack(rotation_surface, images, (rotation_surface.get_width() // 2, rotation_surface.get_height() // 2), int(rotation / self.max_rotations * 360))
            rotations[rotation] = rotation_surface

        return rotations

    def render_stack(self, surf: Surface, images: list[Surface], pos: tuple[int, int], rotation:int, spread: int =1) -> None:
        for i, img in enumerate(images):
            rotated_img = pygame.transform.rotate(img, rotation)
            surf.blit(rotated_img, (pos[0] - rotated_img.get_width() // 2, pos[1] - rotated_img.get_height() // 2 - i * spread))

    def get_rotation_index(self, degrees: int) -> int:
        return int(-degrees * self.max_rotations // 360) % self.max_rotations

    def render_from_matrix(self, surf: Surface, matrix: dict[int, Surface], pos: tuple[int | float, int | float], rotation: int, camera: Camera, height: int = 0) -> None:
        rotation_offset = self.get_rotation_index(camera.rotation)
        final_rotation = (rotation + rotation_offset) % self.max_rotations

        img = matrix[final_rotation]

        x, y = pos
        camera_rotation_radians = math.radians(camera.rotation)

        camera_center_x = camera.offset[0] + self.display.get_width() // 2
        camera_center_y = camera.offset[1] + self.display.get_height() // 2

        # Calculate the offset from the center of the camera
        offset_x = (x - camera_center_x) * math.cos(camera_rotation_radians) - (y - camera_center_y) * math.sin(camera_rotation_radians)
        offset_y = (x - camera_center_x) * math.sin(camera_rotation_radians) + (y - camera_center_y) * math.cos(camera_rotation_radians) - height

        # Calculate the final rendering position relative to the center of the screen
        render_x = int(self.display.get_width() // 2 + offset_x - img.get_width() // 2)
        render_y = int(self.display.get_height() // 2 + offset_y - img.get_height() // 2)

        surf.blit(img, (render_x, render_y))

    def make_asset_map(self, asset_path: str) -> dict[str, dict[int, Surface]]:
        assert asset_path.endswith('/'), "asset path must end with '/' to signify directory path."
        return {img.replace(".png", ''): self.make_rotation_matrix(self.split_stylesheet_into_chunks(asset_path + img)) for img in os.listdir(asset_path)}
