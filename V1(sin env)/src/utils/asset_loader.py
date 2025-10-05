# src/utils/asset_loader.py

import pygame
from src.config import IMAGES_DIR # Importa la ruta base de imágenes

def load_image(path, alpha=True, scale=None):
    """
    Carga una imagen, la convierte para Pygame, y opcionalmente la escala.
    Args:
        path (str): Ruta relativa de la imagen dentro de IMAGES_DIR.
        alpha (bool): Si la imagen tiene canal alfa (transparencia).
        scale (tuple): Tupla (width, height) para escalar la imagen, o None para no escalar.
    Returns:
        pygame.Surface: La imagen cargada y convertida, o None si hay un error.
    """
    full_path = IMAGES_DIR + path
    try:
        image = pygame.image.load(full_path)
        if scale:
            image = pygame.transform.scale(image, scale)
        if alpha:
            return image.convert_alpha()
        else:
            return image.convert()
    except pygame.error as e:
        print(f"Error al cargar imagen {full_path}: {e}")
        return None

# Puedes añadir más funciones para cargar sonidos, fuentes, etc. aquí
# def load_sound(path): ...
# def load_font(path, size): ...