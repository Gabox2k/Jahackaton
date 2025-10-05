# src/config.py

import pygame

# --- Configuración de la Ventana ---
SCREEN_WIDTH = 1024 # Ajusta al ancho de tu imagen de mapa (ej. 1024px)
SCREEN_HEIGHT = 768 # Ajusta al alto de tu imagen de mapa (ej. 768px)
TITLE = "Tembi'u Rush"
FPS = 60

# --- Colores Básicos (para debug, luego se usan sprites) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# --- Rutas de Assets ---
ASSETS_DIR = "assets/"
IMAGES_DIR = ASSETS_DIR + "images/"
FONTS_DIR = ASSETS_DIR + "fonts/"
SOUNDS_DIR = ASSETS_DIR + "sounds/"

# Rutas específicas para este prototipo
MAP_BACKGROUND_PATH = "maps/san_juan_map_final.png"
PLAYER_CHICA_SPRITESHEET_PATH = "characters/player_chica_spritesheet.png"
PLAYER_CHICO_SPRITESHEET_PATH = "characters/player_chico_spritesheet.png"

# --- Configuración del Juego y Mapa ---
TILE_SIZE = 32 # Tamaño en píxeles de un "tile" o celda de movimiento para los personajes

# Posiciones de inicio de los jugadores (ajusta estas coordenadas X, Y)
# Basado en tu mapa de la sala libre, estos son ejemplos que deberás ajustar visualmente.
# Player 1 (Cocinero) - Zona inferior
PLAYER1_SPAWN_POS = (SCREEN_WIDTH // 2 - TILE_SIZE, SCREEN_HEIGHT - TILE_SIZE * 2) 
# Player 2 (Cortador/Entregador) - Zona superior
PLAYER2_SPAWN_POS = (SCREEN_WIDTH // 2 - TILE_SIZE, TILE_SIZE * 2)

# --- Controles de Jugadores ---
PLAYER1_KEYS = {
    'up': pygame.K_w, 'down': pygame.K_s, 'left': pygame.K_a, 'right': pygame.K_d,
    'action_1': pygame.K_1, 'action_2': pygame.K_2, 'action_3': pygame.K_3, 'action_4': pygame.K_4
}
PLAYER2_KEYS = {
    'up': pygame.K_UP, 'down': pygame.K_DOWN, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
    'action_q': pygame.K_q, 'action_e': pygame.K_e, 'action_r': pygame.K_r, 'action_f': pygame.K_f, 'action_g': pygame.K_g
}

# --- Rectángulos de Colisión para el Mapa ---
# ¡IMPORTANTE! Ajusta estos Rect()s para que coincidan con las paredes y mesas de tu mapa.
# La última imagen que me pasaste tiene paredes alrededor y una gran área central libre.
# Necesitarás definir los rectángulos de las paredes exteriores y las bases de las estaciones.
MAP_COLLISION_RECTS = [
    # Pared exterior izquierda (ajusta width y height según el grosor de tu pared)
    pygame.Rect(0, 0, 100, SCREEN_HEIGHT), # Ejemplo: 100px de ancho para la pared izquierda
    # Pared exterior derecha
    pygame.Rect(SCREEN_WIDTH - 100, 0, 100, SCREEN_HEIGHT), # Ejemplo: 100px de ancho para la pared derecha
    # Pared exterior superior
    pygame.Rect(0, 0, SCREEN_WIDTH, 100), # Ejemplo: 100px de alto para la pared superior
    # Pared exterior inferior
    pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100), # Ejemplo: 100px de alto para la pared inferior

    # Colisiones para las estaciones (usa tu imagen como referencia)
    # Estas son solo EJEMPLOS. Reemplázalas por las coordenadas reales de tus estaciones.
    pygame.Rect(100, 150, 150, 80),  # Mesa de corte (ejemplo)
    pygame.Rect(300, 150, 200, 80),  # Otra mesa larga (ejemplo)
    pygame.Rect(700, 150, 150, 80),  # Zona de entrega (ejemplo)
    pygame.Rect(100, 500, 150, 100), # Horno/Tatakua (ejemplo)
    pygame.Rect(300, 550, 100, 50),  # Olla 1 (ejemplo)
    pygame.Rect(450, 550, 100, 50),  # Olla 2 (ejemplo)
    pygame.Rect(600, 550, 100, 50),  # Sartén (ejemplo)
    pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 200, 100, 150) # Barril de ingredientes (ejemplo)
    # Agrega más Rects para la heladera, barriles, platos, etc.
] # <--- ¡ESTE CORCHETE DE CIERRE ES EL QUE FALTABA!

# --- Límites de Zona para los Jugadores (Para evitar que crucen entre sí) ---
# Aquí asumimos que la división es horizontal en el centro de la pantalla
# El cocinero (P1) no puede subir más allá de este punto.
PLAYER1_ZONE_LIMIT_TOP = (SCREEN_HEIGHT // 2) - (TILE_SIZE // 2) 
# El cortador/entregador (P2) no puede bajar más allá de este punto.
PLAYER2_ZONE_LIMIT_BOTTOM = (SCREEN_HEIGHT // 2) + (TILE_SIZE // 2)