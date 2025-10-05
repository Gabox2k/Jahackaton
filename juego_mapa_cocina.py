import pygame
import pytmx

pygame.init()

WIDTH, HEIGHT = 1344, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mapa con colisiones desde Tiled")

tmx_data = pytmx.util_pygame.load_pygame("cocina.tmx")

# # Construir lista de colisiones de forma robusta
# collisions = []
# for obj in tmx_data.objects:
#     if getattr(obj, "width", 0) == 0 or getattr(obj, "height", 0) == 0:
#         continue

#     x = obj.x
#     y = obj.y
#     if getattr(obj, "gid", None):
#         y = y - obj.height

#     rect = pygame.Rect(int(x), int(y), int(obj.width), int(obj.height))
#     collisions.append(rect)
collisions = []
for obj in tmx_data.objects:
    if getattr(obj, "width", 0) == 0 or getattr(obj, "height", 0) == 0:
        continue

    x = obj.x
    y = obj.y

    # Ajuste para que siempre quede top-left como referencia
    if getattr(obj, "gid", None):  # si es tile
        x = int(x)
        y = int(y - obj.height)
    else:  # si es rect normal
        x = int(x)
        y = int(y)

    rect = pygame.Rect(x, y, int(obj.width), int(obj.height))
    collisions.append(rect)


print("Colisiones cargadas:", len(collisions))

clock = pygame.time.Clock()

# ---------------------------
# Clase Player con sprites
# ---------------------------
# class Player:
#     def __init__(self, x, y, speed, sprites):
#         self.rect = pygame.Rect(x, y, 32, 32)
#         self.speed = speed
#         self.sprites = sprites  # dict con direcciones -> imagen
#         self.direction = "down"  # dirección inicial
class Player:
    def __init__(self, x, y, speed, sprites):
        self.sprites = sprites
        self.direction = "down"
        self.speed = speed

        # Sprite base (tomamos uno cualquiera)
        base_sprite = list(sprites.values())[0]
        sprite_w, sprite_h = base_sprite.get_size()

        # Rect pequeño (caja de colisión en los pies, no del tamaño del sprite)
        rect_w, rect_h = 32, 32  # tamaño de colisión
        self.rect = pygame.Rect(0, 0, rect_w, rect_h)

        # Centrar el rect en la posición inicial, pero alineado abajo
        self.rect.midbottom = (x, y)

    def handle_input(self, keys, controls):
        dx, dy = 0, 0
        if keys[controls["left"]]:
            dx = -self.speed
            self.direction = "left"
        if keys[controls["right"]]:
            dx = self.speed
            self.direction = "right"
        if keys[controls["up"]]:
            dy = -self.speed
            self.direction = "up"
        if keys[controls["down"]]:
            dy = self.speed
            self.direction = "down"

        # mover en X
        self.rect.x += dx
        for rect in collisions:
            if self.rect.colliderect(rect):
                if dx > 0:
                    self.rect.right = rect.left
                elif dx < 0:
                    self.rect.left = rect.right

        # mover en Y
        self.rect.y += dy
        for rect in collisions:
            if self.rect.colliderect(rect):
                if dy > 0:
                    self.rect.bottom = rect.top
                elif dy < 0:
                    self.rect.top = rect.bottom

    def draw(self, surface):
        if self.sprites and self.direction in self.sprites:
            sprite = self.sprites[self.direction]
            sprite_w, sprite_h = sprite.get_size()

            # Alinear sprite a los pies (rect.midbottom)
            draw_x = self.rect.centerx - sprite_w // 2
            draw_y = self.rect.bottom - sprite_h
            sprite = self.sprites[self.direction]
            # Calcular offset: dibujar desde los pies (self.rect.bottom)
            offset_y = self.rect.height - sprite.get_height()
            #surface.blit(sprite, (self.rect.x, self.rect.y + offset_y))
            surface.blit(sprite, (draw_x, draw_y))
        else:
            # fallback debug: rectángulo
            pygame.draw.rect(surface, (0, 255, 0), self.rect)

    # def draw(self, surface):
    #     if self.sprites and self.direction in self.sprites:
    #         surface.blit(self.sprites[self.direction], self.rect)
    #     else:
    #         # fallback: rectángulo de color
    #         pygame.draw.rect(surface, (0, 255, 0), self.rect)


# ---------------------------
# Cargar sprites (ejemplo)
# ---------------------------
# NOTA: reemplazá estas rutas por tus imágenes reales
def load_and_scale(path, size=(128, 128)):
    img = pygame.image.load(path).convert_alpha()  # convert_alpha() para transparencias
    return pygame.transform.scale(img, size)

player1_sprites = {
    "up": load_and_scale("player1.png"),
    "down": load_and_scale("player1.png"),
    "left": load_and_scale("player1.png"),
    "right": load_and_scale("player1.png"),
}

player2_sprites = {
    "up": load_and_scale("player2.png"),
    "down": load_and_scale("player2.png"),
    "left": load_and_scale("player2.png"),
    "right": load_and_scale("player2.png"),
}

# ---------------------------
# Crear dos jugadores
# ---------------------------
player1 = Player(1050, 600, 8, player1_sprites)
player2 = Player(1050, 500, 8, player2_sprites)  # un poco más arriba

# Controles distintos para cada jugador
controls1 = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT,
             "up": pygame.K_UP, "down": pygame.K_DOWN}
controls2 = {"left": pygame.K_a, "right": pygame.K_d,
             "up": pygame.K_w, "down": pygame.K_s}

# ---------------------------
# Dibujar mapa
# ---------------------------
def draw_map():
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

# ---------------------------
# Bucle principal
# ---------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player1.handle_input(keys, controls1)
    player2.handle_input(keys, controls2)

    screen.fill((0, 0, 0))
    draw_map()
    player1.draw(screen)
    player2.draw(screen)

    # for rect in collisions:
    #     pygame.draw.rect(screen, (255, 0, 0), rect, 1)  # solo borde

    pygame.display.flip()
    clock.tick(60)


pygame.quit()
