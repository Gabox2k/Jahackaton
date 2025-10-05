import pygame
import pytmx
import sys
import os

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
# Rutas de assets
# -------------------------------
ASSETS_DIR = "assets"
ING_DIR = os.path.join(ASSETS_DIR, "ingredientes")
FRIDGE_DIR = os.path.join(ASSETS_DIR, "heladera")

# Crea las carpetas si no existen (no falla si ya están)
os.makedirs(ING_DIR, exist_ok=True)
os.makedirs(FRIDGE_DIR, exist_ok=True)

# -------------------------------
# Fondos (con fallbacks)
# -------------------------------
def safe_load_image(path, size):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, size)
    except Exception:
        s = pygame.Surface(size); s.fill((30, 30, 30))
        return s

fondo_menu = safe_load_image("menu.png", (ANCHO_MENU, ALTO_MENU))
fondo_instr = safe_load_image("fondo_instrucciones.jpg", (ANCHO_MENU, ALTO_MENU))
fondo_fin = safe_load_image("fondo_perdieron.jpg", (ANCHO_MAPA, ALTO_MAPA))

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
    ("Cada pedido entregado suma 100$, los que eches a perder te restarán 50$.", blanco_roto),
    ("Controles:", naranja_calido),
    ("Jugador 1 → WASD (solo moverse)", blanco_roto),
    ("Jugador 2 → Flechas + 1 heladera + 2 recoger + 3 entregar", blanco_roto),
    ("Acciones:", naranja_calido),
    ("Tomá ingredientes", blanco_roto),
    ("Cortá y cociná", blanco_roto),
    ("Emplatá", blanco_roto),
]

# -------------------------------
# Utilidades UI
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
# Escena del mapa
# -------------------------------
def jugar_mapa():
    import traceback

    screen = pygame.display.set_mode((ANCHO_MAPA, ALTO_MAPA))
    pygame.display.set_caption("Tembi'u Rush - Cocina")

    clock_mapa = pygame.time.Clock()

    # -------- Carga TMX segura --------
    tmx_data = None
    load_error = None
    try:
        tmx_data = pytmx.util_pygame.load_pygame("cocina.tmx")
    except Exception as e:
        load_error = f"No se pudo cargar 'cocina.tmx': {e}"

    collisions, interactivos = [], []

    def draw_map_safe():
        if not tmx_data:
            screen.fill((60, 40, 30))
            return
        for layer in tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

    if tmx_data:
        for obj in tmx_data.objects:
            tipo = getattr(obj, "type", None)
            try:
                props = obj.properties or {}
            except Exception:
                props = {}
            if not tipo:
                tipo = props.get("tipo", None)
            rect = pygame.Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))
            if tipo:
                interactivos.append((tipo, rect))
            else:
                collisions.append(rect)

    # -------- Zonas clave (aprox) --------
    pickup_rect   = pygame.Rect(1060, 560, 100, 100)  # PICK-UP
    heladera_rect = pygame.Rect(165, 480, 120, 190)   # Heladera (izquierda)

    # -------- Sprites / assets --------
    def load_and_scale(path, size=(128, 128)):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        except Exception:
            s = pygame.Surface(size, pygame.SRCALPHA)
            s.fill((255, 255, 255, 180))
            return s

    try:
        plato_img = pygame.image.load("plato.png").convert_alpha()
    except Exception:
        plato_img = pygame.Surface((32, 32), pygame.SRCALPHA)
        plato_img.fill((255, 255, 255))
    plato_img = pygame.transform.scale(plato_img, (32, 32))

    # 3 platos sobre mesa
    mesa_x, mesa_y, num_platos = 400, 300, 3
    for i in range(num_platos):
        interactivos.append(("plato", pygame.Rect(mesa_x + i * 60, mesa_y, 32, 32)))

    # ======= HELADERA =======
    def load_fridge_image():
        candidates = [
            os.path.join(FRIDGE_DIR, "fondo_heladera.png"),
            os.path.join(FRIDGE_DIR, "c2bfd9eb-8f72-49ac-a280-fd5ecf0d7641.png"),
            "c2bfd9eb-8f72-49ac-a280-fd5ecf0d7641.png",
            "Diseño sin título.png",
            "ventana_heladera.png",
        ]
        for fn in candidates:
            try:
                img = pygame.image.load(fn).convert()
                return pygame.transform.scale(img, (ANCHO_MAPA, ALTO_MAPA))
            except Exception:
                continue
        # último fallback: gris (no azul)
        s = pygame.Surface((ANCHO_MAPA, ALTO_MAPA))
        s.fill((40, 40, 40))
        return s

    def load_ingredient_icons():
        """
        Carga íconos desde assets/ingredientes primero, y si no, desde el mismo folder del .py.
        Si no existe el PNG, pone un placeholder con el nombre.
        (ARROZ eliminado del catálogo)
        """
        catalog = {
            "manteca": ["manteca.png"],
            "harina":  ["harina.png"],
            "almidon": ["almidon.png", "almidón.png"],
            "mandioca":["mandioca.png", "yuca.png"],
            "queso":   ["queso.png"],
            "carne":   ["carne.png", "carne_picada.png"],
        }
        icons = {}
        for name, files in catalog.items():
            surf = None
            # busca primero en assets/ingredientes, luego junto al .py
            for base in (ING_DIR, ""):
                for fn in files:
                    path = os.path.join(base, fn) if base else fn
                    try:
                        surf = pygame.image.load(path).convert_alpha()
                        break
                    except Exception:
                        continue
                if surf is not None:
                    break
            if surf is None:
                # Placeholder: tarjeta con el nombre del ingrediente
                w, h = 128, 128
                surf = pygame.Surface((w, h), pygame.SRCALPHA)
                surf.fill((230, 230, 230, 255))
                pygame.draw.rect(surf, (40, 40, 40), surf.get_rect(), 2, border_radius=10)
                txt = fuente_texto.render(name, True, (20, 20, 20))
                surf.blit(txt, (w//2 - txt.get_width()//2, h//2 - txt.get_height()//2))
            icons[name] = surf
        return icons

    ING_ICONS = load_ingredient_icons()

    def draw_icon_in_rect(surface, icon, rect, pad=8):
        """Dibuja el icono centrado y escalado dentro del rect (mantiene aspecto)."""
        if icon is None:
            return
        iw, ih = icon.get_width(), icon.get_height()
        maxw, maxh = max(1, rect.w - pad*2), max(1, rect.h - pad*2)
        scale = min(maxw / iw, maxh / ih)
        new_size = (max(1, int(iw * scale)), max(1, int(ih * scale)))
        icon_scaled = pygame.transform.smoothscale(icon, new_size)
        x = rect.x + (rect.w - new_size[0]) // 2
        y = rect.y + (rect.h - new_size[1]) // 2
        surface.blit(icon_scaled, (x, y))

    def abrir_heladera(jugador):
        heladera_bg = load_fridge_image()
        BASE_W, BASE_H = heladera_bg.get_width(), heladera_bg.get_height()
        sx, sy = ANCHO_MAPA / BASE_W, ALTO_MAPA / BASE_H
        def S(x, y, w, h):
            return pygame.Rect(int(x * sx), int(y * sy), int(w * sx), int(h * sy))

        # Áreas clickeables de ingredientes (ARROZ eliminado)
        items = {
            "manteca": S(140, 320, 150, 120),
            "harina":  S(420, 300, 120, 140),
            # "arroz":   S(560, 300, 120, 140),  # <- eliminado
            "almidon": S(720, 300, 135, 140),
            "mandioca":S(220, 480, 220, 110),
            "queso":   S(490, 500, 140, 110),
            "carne":   S(680, 495, 210, 120),
        }

        overlay_clock = pygame.time.Clock()
        running_overlay = True
        while running_overlay:
            mx, my = pygame.mouse.get_pos()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN and (ev.key == pygame.K_ESCAPE or ev.key == pygame.K_l):
                    running_overlay = False
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    for nombre, r in items.items():
                        if r.collidepoint(mx, my):
                            jugador.bowl.append(nombre)

            # Dibujo overlay: fondo + íconos en sus cuadros
            screen.blit(heladera_bg, (0, 0))

            for nombre, r in items.items():
                # panel sutil detrás
                panel = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                panel.fill((255, 255, 255, 40))
                screen.blit(panel, (r.x, r.y))
                # ícono centrado
                draw_icon_in_rect(screen, ING_ICONS.get(nombre), r, pad=10)

            # Hover suave (sin bordes)
            for nombre, r in items.items():
                if r.collidepoint(mx, my):
                    hover = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                    hover.fill((255, 255, 255, 50))
                    screen.blit(hover, (r.x, r.y))

            # Instrucciones + selección
            screen.blit(fuente_texto.render("CLICK = agregar | L/ESC = cerrar", True, (255,255,255)), (18, 18))
            sel = "Seleccionados: " + (", ".join(jugador.bowl[-8:]) if jugador.bowl else "-")
            screen.blit(fuente_texto.render(sel, True, (255,255,255)), (18, ALTO_MAPA - 40))

            pygame.display.flip()
            overlay_clock.tick(60)
    # ===========================================

    # -------- Jugadores --------
    player1_sprites = {d: load_and_scale("player1.png") for d in ["up", "down", "left", "right"]}
    player2_sprites = {d: load_and_scale("player2.png") for d in ["up", "down", "left", "right"]}

    class Player:
        def __init__(self, x, y, speed, sprites):
            self.sprites = sprites
            self.direction = "down"
            self.speed = speed
            self.rect = pygame.Rect(x, y, 32, 32)
            self.platos_recogidos = 0
            self.bowl = []  # ingredientes desde heladera

        def handle_input(self, keys, controls):
            dx, dy = 0, 0
            if keys[controls["left"]]:  dx = -self.speed; self.direction = "left"
            if keys[controls["right"]]: dx =  self.speed; self.direction = "right"
            if keys[controls["up"]]:    dy = -self.speed; self.direction = "up"
            if keys[controls["down"]]:  dy =  self.speed; self.direction = "down"

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

    player1 = Player(1050, 600, 8, player1_sprites)  # solo moverse
    player2 = Player(1050, 500, 8, player2_sprites)  # recoge/entrega + heladera

    controls1 = {"left": pygame.K_a, "right": pygame.K_d, "up": pygame.K_w, "down": pygame.K_s}
    controls2 = {"left": pygame.K_LEFT, "right": pygame.K_RIGHT, "up": pygame.K_UP, "down": pygame.K_DOWN,
                 "recoger": pygame.K_2, "entregar": pygame.K_3, "heladera": pygame.K_1}

    # -------- HUD --------
    def draw_hint(texto, x, y):
        t = fuente_texto.render(texto, True, (0, 0, 0))
        pad = 6
        box = pygame.Rect(x, y, t.get_width() + 2*pad, t.get_height() + 2*pad)
        pygame.draw.rect(screen, (255, 255, 255), box, border_radius=6)
        pygame.draw.rect(screen, (0, 0, 0), box, 2, border_radius=6)
        screen.blit(t, (x + pad, y + pad))

    INTERACT_PADDING = 10
    tiempo_inicial = pygame.time.get_ticks()
    monedas = 0

    # -------- Loop principal del mapa --------
    running_mapa = True
    while running_mapa:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                # Abrir heladera (J2 cerca + tecla 1)
                if event.type == pygame.KEYDOWN and event.key == controls2["heladera"]:
                    if player2.rect.colliderect(heladera_rect.inflate(12, 12)):
                        abrir_heladera(player2)

            keys = pygame.key.get_pressed()
            player1.handle_input(keys, controls1)
            player2.handle_input(keys, controls2)

            # Interacción con platos (solo J2)
            for tipo, rect in interactivos[:]:
                interact_rect = rect.inflate(INTERACT_PADDING, INTERACT_PADDING)
                if tipo.lower() == "plato":
                    if player2.rect.colliderect(interact_rect) and keys[controls2["recoger"]]:
                        player2.platos_recogidos += 1
                        interactivos.remove((tipo, rect))

            # Entrega (J2 tecla 3)
            if player2.rect.colliderect(pickup_rect) and keys[controls2["entregar"]] and player2.platos_recogidos > 0:
                monedas += 50 * player2.platos_recogidos
                player2.platos_recogidos = 0

            # ----- Dibujo -----
            screen.fill((0, 0, 0))
            draw_map_safe()
            player1.draw(screen)
            player2.draw(screen)

            for tipo, rect in interactivos:
                if tipo.lower() == "plato":
                    screen.blit(plato_img, rect.topleft)

            if player2.platos_recogidos > 0:
                screen.blit(plato_img, (player2.rect.x, player2.rect.y - 20))

            # Hints (sin bordes debug)
            if player2.rect.colliderect(heladera_rect.inflate(16, 16)):
                draw_hint("1 = Abrir heladera", 190, 460)
            if player2.rect.colliderect(pickup_rect.inflate(16, 16)):
                draw_hint("3 = Entregar", pickup_rect.x - 10, pickup_rect.y - 40)

            # HUD
            screen.blit(fuente_moneda.render(f"Moneda: {monedas}", True, (255,255,255)), (10, 10))
            bowl_txt = ", ".join(player2.bowl[-8:]) if player2.bowl else "-"
            screen.blit(fuente_texto.render(f"P2 bowl: {bowl_txt}", True, (255,255,255)), (10, 40))

            # Timer 2 minutos
            tiempo_actual = pygame.time.get_ticks()
            tiempo_restante = max(0, 120000 - (tiempo_actual - tiempo_inicial))
            minutos = tiempo_restante // 60000
            segundos = (tiempo_restante % 60000) // 1000
            timer_text = fuente_timer.render(f"{minutos:02d}:{segundos:02d}", True, (255,255,255))
            screen.blit(timer_text, (ANCHO_MAPA - 150, 10))

            if tiempo_restante <= 0:
                screen.blit(fondo_fin, (0, 0))
                pygame.display.flip()
                pygame.time.delay(3000)
                return

            if load_error:
                draw_hint(load_error, 20, ALTO_MAPA - 60)

            pygame.display.flip()
            clock_mapa.tick(60)

        except Exception as e:
            # Overlay de error para no “cerrar” la ventana sin mensaje
            msg = str(e)
            overlay = pygame.Surface((ANCHO_MAPA, ALTO_MAPA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            y = 200
            for line in ["Se produjo un error:", msg, "Revisá la consola. ESC para salir."]:
                txt = fuente_texto.render(line, True, (255, 120, 120))
                screen.blit(txt, (40, y)); y += 28
            pygame.display.flip()
            # permitir salir
            waiting = True
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                        return

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
        ventana.blit(fondo_instr, (0, 0))

        espacio = 30
        alturas = [fuente_texto.render(l, True, c).get_height() for l, c in lineas_texto]
        alto_total = sum(alturas) + espacio * (len(lineas_texto) - 1)
        y_inicio = (ALTO_MENU - alto_total) // 2 - 100
        y = y_inicio
        for linea, color in lineas_texto:
            render = fuente_texto.render(linea, True, color)
            x = (ANCHO_MENU - render.get_width()) // 2
            ventana.blit(fuente_texto.render(linea, True, negro), (x + 2, y + 2))
            ventana.blit(render, (x, y))
            y += render.get_height() + espacio

        dibujar_boton(ventana, boton_continuar, "Continuar", fuente_continuar, verde_texto, crema, verde_borde)
    else:
        ventana.blit(fondo_menu, (0, 0))
        dibujar_boton(ventana, boton_jugar, "Jugar", fuente_botones, verde_texto, crema, verde_borde)
        dibujar_boton(ventana, boton_salir, "Salir", fuente_botones, verde_texto, crema, verde_borde)

    pygame.display.flip()
    clock.tick(30)
