import pygame
import sys
import os

pygame.init()

# Mostrar información útil para depuración
print("Working directory (cwd):", os.getcwd())
script_dir = os.path.dirname(os.path.abspath(__file__))
print("Script directory (__file__):", script_dir)
print("Archivos en script_dir:", os.listdir(script_dir))

# Configuración de ventana
ANCHO, ALTO = 1152, 758
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tembi'u Rush - Game Over")

# Colores estilo pixel-art
CREMA = (252, 242, 210)
VERDE_BORDE = (64, 128, 64)
VERDE_TEXTO = (48, 96, 48)
FALLBACK_BG = (20, 20, 30)  # color si no hay imagen

# Función para buscar imagen en varias rutas
def encontrar_imagen(nombre_base):
    # listas de extensiones y subcarpetas a probar
    ext = [".jpg", ".jpeg", ".png", ".bmp"]
    subdirs = ["", "images", "img", "assets", "assets/images", "src"]
    for sd in subdirs:
        for e in ext:
            ruta = os.path.join(script_dir, sd, nombre_base + e)
            if os.path.exists(ruta):
                return ruta
    # probar nombre exacto en cwd también
    for e in ext:
        ruta_cwd = os.path.join(os.getcwd(), nombre_base + e)
        if os.path.exists(ruta_cwd):
            return ruta_cwd
    return None

# Intentar cargar fondo
ruta_fondo = encontrar_imagen("fondo_final")
fondo = None
if ruta_fondo:
    try:
        print("Cargando imagen desde:", ruta_fondo)
        fondo = pygame.image.load(ruta_fondo).convert()
        fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))
    except Exception as e:
        print("Error al cargar la imagen encontrada:", e)
        fondo = None
else:
    print("No se encontró 'fondo_final' en script_dir ni en subcarpetas ni en cwd.")

# Cargar fuentes de forma segura (buscar en script_dir también)
def encontrar_fuente(nombre):
    posibles = [nombre, os.path.join(script_dir, nombre)]
    for p in posibles:
        if os.path.exists(p):
            return p
    return None

ruta_fuente = encontrar_fuente("pixel_font.ttf")
try:
    if ruta_fuente:
        print("Cargando fuente desde:", ruta_fuente)
        fuente_titulo = pygame.font.Font(ruta_fuente, 80)
        fuente_texto = pygame.font.Font(ruta_fuente, 36)
        fuente_boton = pygame.font.Font(ruta_fuente, 40)
    else:
        raise FileNotFoundError("pixel_font.ttf no encontrado")
except Exception as e:
    print("No se pudo cargar la fuente personalizada:", e)
    fuente_titulo = pygame.font.Font(None, 80)
    fuente_texto = pygame.font.Font(None, 36)
    fuente_boton = pygame.font.Font(None, 40)

clock = pygame.time.Clock()

# Botones
boton_volver = pygame.Rect(ANCHO // 2 - 400, 600, 300, 80)
boton_salir = pygame.Rect(ANCHO // 2 + 100, 600, 300, 80)

def dibujar_boton(superficie, rect, texto, fuente, color_texto, color_fondo, color_borde):
    pygame.draw.rect(superficie, color_fondo, rect, border_radius=10)
    pygame.draw.rect(superficie, color_borde, rect, width=6, border_radius=10)
    render_texto = fuente.render(texto, True, color_texto)
    superficie.blit(
        render_texto,
        (rect.centerx - render_texto.get_width() // 2,
         rect.centery - render_texto.get_height() // 2)
    )

# Función segura para "volver al menú"
def volver_al_menu():
    pygame.quit()
    # Intentar ejecutar menu.py en la misma carpeta del script
    menu_path = os.path.join(script_dir, "menu.py")
    if os.path.exists(menu_path):
        print("Lanzando menu.py ...")
        # Ejecutar menu con el mismo intérprete (no usar subprocess en VSCode si causa problemas)
        os.execv(sys.executable, [sys.executable, menu_path])
    else:
        print("menu.py no encontrado en:", script_dir)
        sys.exit()

# Loop principal
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN:
            if boton_volver.collidepoint(evento.pos):
                volver_al_menu()

            if boton_salir.collidepoint(evento.pos):
                pygame.quit()
                sys.exit()

    # Dibujar fondo (imagen o fallback)
    if fondo:
        ventana.blit(fondo, (0, 0))
    else:
        ventana.fill(FALLBACK_BG)

    # Texto principal
    texto_perdiste = fuente_titulo.render("¡PERDISTE!", True, VERDE_TEXTO)
    texto_mensaje = fuente_texto.render("Se acabó el tiempo y no pudiste terminar el pedido", True, VERDE_TEXTO)

    ventana.blit(texto_perdiste, (ANCHO // 2 - texto_perdiste.get_width() // 2, 250))
    ventana.blit(texto_mensaje, (ANCHO // 2 - texto_mensaje.get_width() // 2, 350))

    # Dibujar botones
    dibujar_boton(ventana, boton_volver, "Volver", fuente_boton, VERDE_TEXTO, CREMA, VERDE_BORDE)
    dibujar_boton(ventana, boton_salir, "Salir", fuente_boton, VERDE_TEXTO, CREMA, VERDE_BORDE)

    pygame.display.flip()
    clock.tick(30)
