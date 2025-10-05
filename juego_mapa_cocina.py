import pygame
import pytmx
import random
from collections import Counter

pygame.init()

WIDTH, HEIGHT = 1344, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mapa con colisiones + Recetas/Pedidos")

# === MAPA / TILED ============================================================
tmx_data = pytmx.util_pygame.load_pygame("cocina.tmx")

collisions = []
for obj in tmx_data.objects:
    if getattr(obj, "width", 0) == 0 or getattr(obj, "height", 0) == 0:
        continue
    x = obj.x
    y = obj.y
    if getattr(obj, "gid", None):  # tile
        x = int(x)
        y = int(y - obj.height)
    else:
        x = int(x)
        y = int(y)
    rect = pygame.Rect(x, y, int(obj.width), int(obj.height))
    collisions.append(rect)

clock = pygame.time.Clock()

# === JUGADORES ===============================================================
def load_and_scale(path, size=(128, 128)):
    img = pygame.image.load(path).convert_alpha()
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

class Player:
    def __init__(self, x, y, speed, sprites):
        self.sprites = sprites
        self.direction = "down"
        self.speed = speed
        rect_w, rect_h = 32, 32
        self.rect = pygame.Rect(0, 0, rect_w, rect_h)
        self.rect.midbottom = (x, y)

        # Estado del jugador
        self.bowl = []
        self.last_cooked = None

    def handle_move(self, keys, controls):
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

        self.rect.x += dx
        for r in collisions:
            if self.rect.colliderect(r):
                if dx > 0: self.rect.right = r.left
                elif dx < 0: self.rect.left = r.right

        self.rect.y += dy
        for r in collisions:
            if self.rect.colliderect(r):
                if dy > 0: self.rect.bottom = r.top
                elif dy < 0: self.rect.top = r.bottom

    def draw(self, surface):
        sprite = self.sprites[self.direction]
        sprite_w, sprite_h = sprite.get_size()
        draw_x = self.rect.centerx - sprite_w // 2
        draw_y = self.rect.bottom - sprite_h
        surface.blit(sprite, (draw_x, draw_y))

player1 = Player(1050, 600, 8, player1_sprites)
player2 = Player(1050, 500, 8, player2_sprites)

controls1 = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "up": pygame.K_UP, "down": pygame.K_DOWN}
controls2 = {"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s}

def draw_map():
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

# === SISTEMA DE RECETAS ======================================================
FONT = pygame.font.SysFont(None, 22)
BIG  = pygame.font.SysFont(None, 40)

# Ingredientes sin "sal"
INGREDIENT_KEYS = [
    ("almidon",  "1 / KP1"),
    ("queso",    "2 / KP2"),
    ("manteca",  "3 / KP3"),
    ("leche",    "4 / KP4"),
    ("mandioca", "5 / KP5"),
    ("harina",   "6 / KP6"),
    ("carne",    "7 / KP7"),
]

RECIPES = {
    "MBEJU": {"almidon", "queso", "manteca"},
    "PASTEL MANDI'O": {"mandioca", "harina", "carne"},
}

# 🔀 Randomiza entre 1 a 3 pedidos
possible_recipes = list(RECIPES.keys())
orders = [random.choice(possible_recipes) for _ in range(random.randint(1, 3))]
delivered = []

# === FUNCIONES DE COCINA =====================================================
def try_cook(player):
    bowl_set = set(player.bowl)
    for name, req in RECIPES.items():
        if req.issubset(bowl_set):
            player.last_cooked = name
            player.bowl.clear()
            return True
    return False

def deliver(player):
    global delivered
    if player.last_cooked is None:
        return False
    want = Counter(orders)
    have = Counter(delivered)
    if have[player.last_cooked] < want[player.last_cooked]:
        delivered.append(player.last_cooked)
        player.last_cooked = None
        return True
    return False

def lists_match():
    return Counter(delivered) == Counter(orders)

# === TIMER Y ESTADO FINAL ====================================================
TOTAL_TIME_MS = 120_000  # 2 minutos
start_ticks = pygame.time.get_ticks()
game_over = False
game_result = None  # "win" o "lose"

# === INTERFAZ ================================================================
def draw_panel():
    panel = pygame.Rect(WIDTH - 360, 0, 360, HEIGHT)
    pygame.draw.rect(screen, (245, 245, 245), panel)
    pygame.draw.line(screen, (200, 200, 200), (panel.left, 0), (panel.left, HEIGHT), 2)

    now = pygame.time.get_ticks()
    remaining = max(0, TOTAL_TIME_MS - (now - start_ticks))
    secs = remaining // 1000
    time_text = BIG.render(f"Tiempo: {secs:>3}s", True, (50, 50, 50))
    screen.blit(time_text, (panel.left + 10, 10))

    y = 52
    screen.blit(BIG.render("Ingredientes", True, (20, 20, 20)), (panel.left+10, y)); y += 36
    for name, hint in INGREDIENT_KEYS:
        screen.blit(FONT.render(f"- {name} [{hint}]", True, (30, 30, 30)), (panel.left+14, y)); y += 22

    y += 10
    screen.blit(BIG.render("Pedidos", True, (20, 20, 20)), (panel.left+10, y)); y += 36
    cnt = Counter(orders)
    for k in cnt:
        screen.blit(FONT.render(f"- {k} x{cnt[k]}", True, (30,30,30)), (panel.left+14, y)); y+=22

    y += 10
    screen.blit(BIG.render("Entregados", True, (20, 20, 20)), (panel.left+10, y)); y += 36
    if not delivered:
        screen.blit(FONT.render("(vacío)", True, (60,60,60)), (panel.left+14, y)); y+=22
    else:
        cnt = Counter(delivered)
        for k in cnt:
            screen.blit(FONT.render(f"- {k} x{cnt[k]}", True, (30,30,30)), (panel.left+14, y)); y+=22

    y += 16
    screen.blit(BIG.render("Controles", True, (20, 20, 20)), (panel.left+10, y)); y+=36
    for line in [
        "P1: 1..7 agrega | ENTER cocina | D entrega | BKSP limpia",
        "P2: KP1..KP7 | KP_ENTER cocina | RCTRL entrega | DEL limpia",
        "V = Validar pedidos",
    ]:
        screen.blit(FONT.render(line, True, (40,40,40)), (panel.left+14, y)); y+=22

def draw_overlay(result):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    if result == "win":
        msg = BIG.render("¡GANASTE! 🎉 (ESC para salir)", True, (255,255,255))
    else:
        msg = BIG.render("PERDISTE 😢 (ESC para salir)", True, (255,255,255))
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 20))

# === MAPEO DE INGREDIENTES ====================================================
KEY_TO_ING1 = {
    pygame.K_1: "almidon",
    pygame.K_2: "queso",
    pygame.K_3: "manteca",
    pygame.K_4: "leche",
    pygame.K_5: "mandioca",
    pygame.K_6: "harina",
    pygame.K_7: "carne",
}
KEY_TO_ING2 = {
    pygame.K_KP1: "almidon",
    pygame.K_KP2: "queso",
    pygame.K_KP3: "manteca",
    pygame.K_KP4: "leche",
    pygame.K_KP5: "mandioca",
    pygame.K_KP6: "harina",
    pygame.K_KP7: "carne",
}

# === LOOP PRINCIPAL ==========================================================
running = True
while running:
    now = pygame.time.get_ticks()
    remaining = max(0, TOTAL_TIME_MS - (now - start_ticks))
    if not game_over and remaining == 0:
        game_over = True
        game_result = "lose"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_ESCAPE:
                running = False
            if not game_over:
                # P1
                if event.key in KEY_TO_ING1: player1.bowl.append(KEY_TO_ING1[event.key])
                if event.key == pygame.K_RETURN: try_cook(player1)
                if event.key == pygame.K_d: deliver(player1)
                if event.key == pygame.K_BACKSPACE: player1.bowl.clear()

                # P2
                if event.key in KEY_TO_ING2: player2.bowl.append(KEY_TO_ING2[event.key])
                if event.key == pygame.K_KP_ENTER: try_cook(player2)
                if event.key == pygame.K_RCTRL: deliver(player2)
                if event.key == pygame.K_DELETE: player2.bowl.clear()

                # Validar
                if event.key == pygame.K_v:
                    if lists_match():
                        game_over = True
                        game_result = "win"
                    else:
                        game_over = True
                        game_result = "lose"

    keys = pygame.key.get_pressed()
    if not game_over:
        player1.handle_move(keys, controls1)
        player2.handle_move(keys, controls2)

    screen.fill((0, 0, 0))
    draw_map()
    player1.draw(screen)
    player2.draw(screen)
    draw_panel()

    if game_over:
        draw_overlay(game_result)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
