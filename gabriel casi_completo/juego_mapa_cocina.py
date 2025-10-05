import pygame
import pytmx
import sys

pygame.init()

# -------------------------------
# Configuración ventana
# -------------------------------
ANCHO_MENU, ALTO_MENU = 1152, 758
ANCHO_MAPA, ALTO_MAPA = 1344, 768
ventana = pygame.display.set_mode((ANCHO_MENU, ALTO_MENU))
pygame.display.set_caption("Tembi'u Rush")

clock = pygame.time.Clock()

# -------------------------------
# Fondos
# -------------------------------
fondo_menu = pygame.image.load("menu.png").convert()
fondo_menu = pygame.transform.scale(fondo_menu, (ANCHO_MENU, ALTO_MENU))

fondo_instr = pygame.image.load("fondo_instrucciones.jpg").convert()
fondo_instr = pygame.transform.scale(fondo_instr, (ANCHO_MENU, ALTO_MENU))

fondo_fin = pygame.image.load("fondo_perdieron.jpg").convert()
fondo_fin = pygame.transform.scale(fondo_fin, (ANCHO_MAPA, ALTO_MAPA))

# -------------------------------
# Colores y fuentes
# -------------------------------
crema = (252, 242, 210)
verde_borde = (64, 128, 64)
verde_texto = (48, 96, 48)
negro = (0, 0, 0)
naranja_calido = (230, 126, 34)
blanco_roto = (250, 248, 232)

fuente_texto = pygame.font.SysFont("Arial", 22)
fuente_botones = pygame.font.SysFont("Arial", 42)
fuente_continuar = pygame.font.SysFont("Arial", 32)
fuente_timer = pygame.font.SysFont("Arial", 36)
fuente_moneda = pygame.font.SysFont("Arial", 36)

# -------------------------------
# Botones
# -------------------------------
boton_jugar = pygame.Rect(ANCHO_MENU // 2 - 400, 600, 300, 80)
boton_salir = pygame.Rect(ANCHO_MENU // 2 + 100, 600, 300, 80)
boton_continuar = pygame.Rect(ANCHO_MENU // 2 - 150, ALTO_MENU - 120, 300, 70)

# -------------------------------
# Texto instrucciones
# -------------------------------
lineas_texto = [
    ("Objetivo:", naranja_calido),
    ("Prepará y entregá los pedidos a tiempo para ganar.", blanco_roto),
    ("Cada pedido entregado suma 100$, los que eches a perder te restaran 50$.", blanco_roto),
    ("Controles:", naranja_calido),
    ("Jugador 1 → WASD (solo moverse)", blanco_roto),
    ("Jugador 2 → Flechas + 2 para recoger + 3 para entregar", blanco_roto),
    ("Acciones:", naranja_calido),
    ("Tomá ingredientes", blanco_roto),
    ("Cortá y cociná", blanco_roto),
    ("Emplatá", blanco_roto),
]

# -------------------------------
# Función para dibujar botones
# -------------------------------
def dibujar_boton(superficie, rect, texto, fuente, color_texto, color_fondo, color_borde):
    pygame.draw.rect(superficie, color_fondo, rect, border_radius=10)
    pygame.draw.rect(superficie, color_borde, rect, width=6, border_radius=10)
    render_texto = fuente.render(texto, True, color_texto)
    superficie.blit(
        render_texto,
        (rect.centerx - render_texto.get_width() // 2,
         rect.centery - render_texto.get_height() // 2)
    )

# -------------------------------
# Función del mapa
# -------------------------------
def jugar_mapa():
    screen = pygame.display.set_mode((ANCHO_MAPA, ALTO_MAPA))
    pygame.display.set_caption("Tembi'u Rush - Cocina")

    clock_mapa = pygame.time.Clock()

    # Cargar mapa de Tiled
    tmx_data = pytmx.util_pygame.load_pygame("cocina.tmx")

    collisions = []
    interactivos = []

    for obj in tmx_data.objects:
        tipo = getattr(obj, "type", None) or obj.properties.get("tipo", None)
        rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
        if tipo:
            interactivos.append((tipo, rect))
        else:
            collisions.append(rect)

    # -------------------
    # Cargar imagen del plato y colocar 3 platos sobre la mesa
    # -------------------
    plato_img = pygame.image.load("plato.png").convert_alpha()
    plato_img = pygame.transform.scale(plato_img, (32,32))

    mesa_x = 460
    mesa_y = 350
    num_platos = 3
    for i in range(num_platos):
        x = mesa_x + i * 60
        y = mesa_y
        interactivos.append(("plato", pygame.Rect(x, y, 32, 32)))

    # -------------------
    # Zona entrega (solo posición, sin rect visible)
    # -------------------
    entrega_x, entrega_y = 1060, 560  # solo referencia para entregar

    # -------------------
    # Clase Player
    # -------------------
    class Player:
        def __init__(self, x, y, speed, sprites):
            self.sprites = sprites
            self.direction = "down"
            self.speed = speed
            self.rect = pygame.Rect(x, y, 32, 32)
            self.platos_recogidos = 0

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

            self.rect.x += dx
            for rect in collisions:
                if self.rect.colliderect(rect):
                    if dx > 0: self.rect.right = rect.left
                    elif dx < 0: self.rect.left = rect.right

            self.rect.y += dy
            for rect in collisions:
                if self.rect.colliderect(rect):
                    if dy > 0: self.rect.bottom = rect.top
                    elif dy < 0: self.rect.top = rect.bottom

        def draw(self, surface):
            sprite = self.sprites.get(self.direction)
            if sprite:
                draw_x = self.rect.centerx - sprite.get_width() // 2
                draw_y = self.rect.bottom - sprite.get_height()
                surface.blit(sprite, (draw_x, draw_y))
            else:
                pygame.draw.rect(surface, (0, 255, 0), self.rect)

    # -------------------
    # Funciones ayuda
    # -------------------
    def load_and_scale(path, size=(128,128)):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)

    def draw_map():
        for layer in tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x*tmx_data.tilewidth, y*tmx_data.tileheight))

    # -------------------
    # Crear jugadores
    # -------------------
    player1_sprites = {d: load_and_scale("player1.png") for d in ["up","down","left","right"]}
    player2_sprites = {d: load_and_scale("player2.png") for d in ["up","down","left","right"]}

    player1 = Player(1050,600,8,player1_sprites)  # Player 1 solo se mueve
    player2 = Player(1050,500,8,player2_sprites)  # Player 2 recoge y entrega

    controls1 = {"left": pygame.K_a,"right": pygame.K_d,"up": pygame.K_w,"down": pygame.K_s}
    controls2 = {"left": pygame.K_LEFT,"right": pygame.K_RIGHT,"up": pygame.K_UP,"down": pygame.K_DOWN,"recoger": pygame.K_2,"entregar": pygame.K_3}

    INTERACT_PADDING = 10
    tiempo_inicial = pygame.time.get_ticks()
    monedas = 0

    running_mapa = True
    while running_mapa:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        player1.handle_input(keys, controls1)
        player2.handle_input(keys, controls2)

        # -------------------
        # Interacción con platos (solo Player 2)
        # -------------------
        for tipo, rect in interactivos[:]:
            interact_rect = rect.inflate(INTERACT_PADDING, INTERACT_PADDING)
            # Player2 recoge solo si está cerca en X y casi mismo nivel en Y
            if tipo.lower() == "plato" and keys[controls2["recoger"]]:
                if abs(player2.rect.bottom - rect.bottom) < 15 and abs(player2.rect.centerx - rect.centerx) < 35:
                    player2.platos_recogidos += 1
                    interactivos.remove((tipo, rect))
                    break  # solo uno a la vez

        # -------------------
        # Player 2 entrega platos en zona fija con tecla 3
        # -------------------
        if keys[controls2["entregar"]]:
            if abs(player2.rect.centerx - entrega_x) < 50 and abs(player2.rect.centery - entrega_y) < 50:
                monedas += 50 * player2.platos_recogidos
                player2.platos_recogidos = 0

        # -------------------
        # Dibujar todo
        # -------------------
        screen.fill((0,0,0))
        draw_map()
        player1.draw(screen)
        player2.draw(screen)

        # Dibujar platos
        for tipo, rect in interactivos:
            if tipo.lower() == "plato":
                screen.blit(plato_img, rect.topleft)

        # Dibujar plato que lleva Player 2
        if player2.platos_recogidos > 0:
            screen.blit(plato_img, (player2.rect.x, player2.rect.y - 20))

        # Mostrar monedas
        screen.blit(fuente_moneda.render(f"Moneda: {monedas}", True, (255,255,255)), (10,10))

        # Timer 2 minutos
        tiempo_actual = pygame.time.get_ticks()
        tiempo_restante = max(0, 120000 - (tiempo_actual - tiempo_inicial))
        minutos = tiempo_restante // 60000
        segundos = (tiempo_restante % 60000) // 1000
        timer_text = fuente_timer.render(f"{minutos:02d}:{segundos:02d}", True, (255,255,255))
        screen.blit(timer_text, (ANCHO_MAPA - 150, 10))

        # Fin cuando se acaba el tiempo
        if tiempo_restante <= 0:
            screen.blit(fondo_fin,(0,0))
            pygame.display.flip()
            pygame.time.delay(3000)
            return

        pygame.display.flip()
        clock_mapa.tick(60)

# -------------------------------
# Bucle principal menú
# -------------------------------
pantalla_juego = False
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if not pantalla_juego:
                if boton_jugar.collidepoint(evento.pos):
                    pantalla_juego = True
                if boton_salir.collidepoint(evento.pos):
                    pygame.quit()
                    sys.exit()
            else:
                if boton_continuar.collidepoint(evento.pos):
                    jugar_mapa()

    # Dibujar menú o instrucciones
    if pantalla_juego:
        ventana.blit(fondo_instr, (0,0))

        # Texto
        espacio = 30
        alturas_lineas = [fuente_texto.render(l, True, c).get_height() for l,c in lineas_texto]
        alto_total = sum(alturas_lineas) + espacio*(len(lineas_texto)-1)
        y_inicio = (ALTO_MENU - alto_total)//2 - 100
        y = y_inicio
        for linea, color in lineas_texto:
            render_texto = fuente_texto.render(linea, True, color)
            x = (ANCHO_MENU - render_texto.get_width())//2
            ventana.blit(fuente_texto.render(linea, True, negro), (x+2,y+2))
            ventana.blit(render_texto, (x,y))
            y += render_texto.get_height() + espacio

        dibujar_boton(ventana, boton_continuar, "Continuar", fuente_continuar, verde_texto, crema, verde_borde)
    else:
        ventana.blit(fondo_menu, (0,0))
        dibujar_boton(ventana, boton_jugar, "Jugar", fuente_botones, verde_texto, crema, verde_borde)
        dibujar_boton(ventana, boton_salir, "Salir", fuente_botones, verde_texto, crema, verde_borde)

    pygame.display.flip()
    clock.tick(30)
