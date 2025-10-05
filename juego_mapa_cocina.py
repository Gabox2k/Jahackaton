import pygame
import pytmx

pygame.init()

# --- Configuración de la ventana ---
WIDTH, HEIGHT = 1344, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tembi'u Rush")

clock = pygame.time.Clock()

# --- Cargar mapa de Tiled ---
tmx_data = pytmx.util_pygame.load_pygame("cocina.tmx")

# ---------------------------
# Separar colisiones y objetos interactivos
# ---------------------------
collisions = []
interactivos = []

for obj in tmx_data.objects:
    tipo = getattr(obj, "type", None) or obj.properties.get("tipo", None)
    rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))

    if tipo:  # objeto interactivo (heladera, plato, etc.)
        interactivos.append((tipo, rect))
    else:     # objeto sólido para colisión
        collisions.append(rect)

print("Colisiones cargadas:", len(collisions))
print("Zonas interactivas:", [t for t, _ in interactivos])

# ---------------------------
# Clase Player
# ---------------------------
class Player:
    def __init__(self, x, y, speed, sprites):
        self.sprites = sprites
        self.direction = "down"
        self.speed = speed
        base_sprite = list(sprites.values())[0]
        sprite_w, sprite_h = base_sprite.get_size()
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.rect.midbottom = (x, y)
        self.platos = 0  # Inventario de platos

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

        # Mover en X
        self.rect.x += dx
        for rect in collisions:
            if self.rect.colliderect(rect):
                if dx > 0:
                    self.rect.right = rect.left
                elif dx < 0:
                    self.rect.left = rect.right

        # Mover en Y
        self.rect.y += dy
        for rect in collisions:
            if self.rect.colliderect(rect):
                if dy > 0:
                    self.rect.bottom = rect.top
                elif dy < 0:
                    self.rect.top = rect.bottom

    def draw(self, surface):
        sprite = self.sprites.get(self.direction)
        if sprite:
            draw_x = self.rect.centerx - sprite.get_width() // 2
            draw_y = self.rect.bottom - sprite.get_height()
            surface.blit(sprite, (draw_x, draw_y))
        else:
            pygame.draw.rect(surface, (0, 255, 0), self.rect)

# ---------------------------
# Funciones de ayuda
# ---------------------------
def load_and_scale(path, size=(128, 128)):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)

def draw_map():
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

# --- Mostrar ventana de heladera como panel ---
def mostrar_heladera():
    imagen = pygame.image.load("ventana_heladera.png").convert()
    imagen = pygame.transform.scale(imagen, (768, 512))
    abierta = True

    while abierta:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE or evento.key == pygame.K_1:
                    abierta = False

        # Redibujar mapa y jugadores detrás de la heladera
        screen.fill((0, 0, 0))
        draw_map()
        player1.draw(screen)
        player2.draw(screen)

        # Dibujar heladera centrada
        screen.blit(imagen, ((WIDTH - 768)//2, (HEIGHT - 512)//2))
        pygame.display.flip()
        clock.tick(60)

# ---------------------------
# Crear jugadores
# ---------------------------
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

player1 = Player(1050, 600, 8, player1_sprites)
player2 = Player(1050, 500, 8, player2_sprites)

controls1 = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "up": pygame.K_UP, "down": pygame.K_DOWN}
controls2 = {"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s}

# ---------------------------
# Bucle principal
# ---------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # -------------------
    # Abrir heladera jugador 2
    # -------------------
    heladera_abierta = False
    for tipo, rect in interactivos:
        if tipo.lower() == "heladera" and player2.rect.colliderect(rect) and keys[pygame.K_1]:
            print("Jugador 2 abrió la heladera")
            mostrar_heladera()
            heladera_abierta = True
            break

    # -------------------
    # Mover jugadores solo si no se abrió heladera
    # -------------------
    if not heladera_abierta:
        player1.handle_input(keys, controls1)
        player2.handle_input(keys, controls2)

    # -------------------
    # Interacción jugador 1 con platos
    # -------------------
    for tipo, rect in interactivos[:]:  # [:] para evitar modificar mientras iteramos
        if tipo.lower() == "plato" and player1.rect.colliderect(rect) and keys[pygame.K_e]:
            print("Jugador 1 agarró un plato")
            player1.platos += 1
            interactivos.remove((tipo, rect))
            break

    # --- Dibujar todo ---
    screen.fill((0, 0, 0))
    draw_map()
    player1.draw(screen)
    player2.draw(screen)

    # Mostrar inventario de jugador 1
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Platos: {player1.platos}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
