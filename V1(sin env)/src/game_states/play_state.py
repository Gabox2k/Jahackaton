# src/game_states/play_state.py

import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_BACKGROUND_PATH, PLAYER1_SPAWN_POS, PLAYER2_SPAWN_POS, MAP_COLLISION_RECTS
from src.entities.player import Player
from src.utils.asset_loader import load_image

class PlayState:
    def __init__(self, game):
        self.game = game # Referencia al objeto Game principal
        self.background_image = load_image(MAP_BACKGROUND_PATH, alpha=False, scale=(SCREEN_WIDTH, SCREEN_HEIGHT))
        if not self.background_image:
            print("Error: No se pudo cargar el mapa de fondo. El juego no puede iniciar en PlayState.")
            # self.game.change_state("MENU") # O volver al menú si falla

        # Crear los jugadores
        self.player1 = Player(PLAYER1_SPAWN_POS[0], PLAYER1_SPAWN_POS[1], 1) # Jugador 1
        self.player2 = Player(PLAYER2_SPAWN_POS[0], PLAYER2_SPAWN_POS[1], 2) # Jugador 2

        # Grupo de sprites para dibujar fácilmente
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player1, self.player2)

        # Convertir los rectángulos de colisión a objetos Pygame.Rect
        self.obstacles = [pygame.Rect(r) for r in MAP_COLLISION_RECTS]

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            # Las acciones de los jugadores (ej. usar estación) irían aquí
            # for player in self.all_sprites:
            #    player.handle_input(events)

    def update(self):
        # Actualizar a todos los sprites, pasándoles la lista de obstáculos
        self.player1.update(self.obstacles)
        self.player2.update(self.obstacles)
        # self.all_sprites.update(self.obstacles) # Si Player tuviera un método update(obstacles)

    def draw(self, screen):
        # Dibujar el fondo del mapa
        if self.background_image:
            screen.blit(self.background_image, (0, 0))

        # Dibujar los jugadores
        self.all_sprites.draw(screen)

        # Opcional: Dibujar los rectángulos de colisión para depuración
        # for obstacle in self.obstacles:
        #    pygame.draw.rect(screen, (255, 0, 0, 100), obstacle, 1) # Rojo transparente