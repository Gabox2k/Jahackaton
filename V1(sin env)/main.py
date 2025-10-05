# main.py

import pygame
from src.config import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE, FPS
# Importar el PlayState directamente, no necesitamos el MenuState por ahora para probar
from src.game_states.play_state import PlayState

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        # Directamente al PlayState para probar el mapa y los personajes
        self.current_state = PlayState(self) 

    def run(self):
        while self.running:
            # Pasar los eventos al estado actual
            self.current_state.handle_input(pygame.event.get())
            # Actualizar el estado actual
            self.current_state.update()
            # Dibujar el estado actual en la pantalla
            self.current_state.draw(self.screen)

            pygame.display.flip() # Actualiza toda la pantalla
            self.clock.tick(FPS) # Limita los FPS

        pygame.quit() # Cierra Pygame al salir del bucle

    def change_state(self, new_state_name):
        # Esta función será útil más tarde para cambiar entre MenuState, PlayState, etc.
        # Por ahora, solo tenemos PlayState
        if new_state_name == "PLAY":
            self.current_state = PlayState(self)
        # elif new_state_name == "MENU":
        #    self.current_state = MenuState(self) # Descomentar cuando implementemos el menú

if __name__ == "__main__":
    game = Game()
    game.run()