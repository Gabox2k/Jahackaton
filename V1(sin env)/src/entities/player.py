# src/entities/player.py

import pygame
from src.config import TILE_SIZE, PLAYER1_KEYS, PLAYER2_KEYS, PLAYER_CHICA_SPRITESHEET_PATH, PLAYER_CHICO_SPRITESHEET_PATH
from src.utils.asset_loader import load_image

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, player_id):
        super().__init__()
        self.player_id = player_id
        self.speed = 4 # Velocidad de movimiento del jugador

        # Cargar el spritesheet o la imagen temporal
        if self.player_id == 1:
            self.spritesheet = load_image(PLAYER_CHICA_SPRITESHEET_PATH, scale=(TILE_SIZE, TILE_SIZE)) # Temporal: escalar a un tile
            self.keys = PLAYER1_KEYS
        else:
            self.spritesheet = load_image(PLAYER_CHICO_SPRITESHEET_PATH, scale=(TILE_SIZE, TILE_SIZE)) # Temporal: escalar a un tile
            self.keys = PLAYER2_KEYS

        # Usar la imagen temporal directamente. Más tarde, aquí irá la lógica de animación.
        self.image = self.spritesheet

        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0

    def handle_input(self, events):
        # Esta función podría manejar eventos de pulsación de teclas para acciones específicas
        # Pero para el movimiento, Pygame.key.get_pressed() es mejor en update.
        pass

    def update(self, obstacles):
        """
        Actualiza la posición del jugador y maneja las colisiones.
        Args:
            obstacles (list of pygame.Rect): Rectángulos de los obstáculos del mapa.
        """
        # Reiniciar velocidad
        self.vel_x = 0
        self.vel_y = 0

        # Obtener el estado de todas las teclas presionadas
        keys_pressed = pygame.key.get_pressed()

        # Calcular velocidad basada en las teclas asignadas a este jugador
        if keys_pressed[self.keys['left']]:
            self.vel_x = -self.speed
        if keys_pressed[self.keys['right']]:
            self.vel_x = self.speed
        if keys_pressed[self.keys['up']]:
            self.vel_y = -self.speed
        if keys_pressed[self.keys['down']]:
            self.vel_y = self.speed

        # Normalizar velocidad si se mueve en diagonal para que no vaya más rápido
        if self.vel_x != 0 and self.vel_y != 0:
            self.vel_x /= 1.414 # Aproximadamente sqrt(2)

        # Guardar la posición anterior para revertir colisiones
        old_rect = self.rect.copy()

        # Intentar mover en X
        self.rect.x += self.vel_x
        self._handle_collisions(old_rect.x, obstacles, 'x')

        # Intentar mover en Y
        self.rect.y += self.vel_y
        self._handle_collisions(old_rect.y, obstacles, 'y')

        # Lógica para que los jugadores no crucen sus zonas (definidas en config.py)
        # Esto es un ejemplo, deberás ajustar las constantes
        from src.config import PLAYER1_ZONE_LIMIT_TOP, PLAYER2_ZONE_LIMIT_BOTTOM

        if self.player_id == 1: # Cocinero (zona inferior)
            if self.rect.top < PLAYER1_ZONE_LIMIT_TOP:
                self.rect.top = PLAYER1_ZONE_LIMIT_TOP
        elif self.player_id == 2: # Cortador/Entregador (zona superior)
            if self.rect.bottom > PLAYER2_ZONE_LIMIT_BOTTOM:
                self.rect.bottom = PLAYER2_ZONE_LIMIT_BOTTOM


    def _handle_collisions(self, old_coord, obstacles, axis):
        """
        Maneja colisiones con obstáculos.
        Args:
            old_coord (int): La coordenada (x o y) antes del movimiento.
            obstacles (list of pygame.Rect): Rectángulos de los obstáculos.
            axis (str): 'x' o 'y' para indicar el eje de colisión.
        """
        for obstacle_rect in obstacles:
            if self.rect.colliderect(obstacle_rect):
                if axis == 'x':
                    if self.vel_x > 0: # Moviéndose a la derecha
                        self.rect.right = obstacle_rect.left
                    elif self.vel_x < 0: # Moviéndose a la izquierda
                        self.rect.left = obstacle_rect.right
                elif axis == 'y':
                    if self.vel_y > 0: # Moviéndose hacia abajo
                        self.rect.bottom = obstacle_rect.top
                    elif self.vel_y < 0: # Moviéndose hacia arriba
                        self.rect.top = obstacle_rect.bottom