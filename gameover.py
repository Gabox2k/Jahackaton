import pygame
import sys
import os

pygame.init()

# Configuración de ventana
ANCHO, ALTO = 1152, 758
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Tembi'u Rush - Game Over")

# Colores estilo pixel-art
CREMA = (252, 242, 210)
VERDE_BORDE = (255, 128, 0)
VERDE_TEXTO = (48, 96, 48)
FALLBACK_BG = (20, 20, 30)  # color si no hay imagen

# Directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Buscar imagen de fondo
ruta_fondo = os.path.join(script_dir, "fondo_perdieron.jpg")
fondo = None
if os.path.exists(ruta_fondo):
    try:
        fondo = pygame.image.load(ruta_fondo).convert()
        fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))
    except:
        fondo = None

# Fuentes (default de pygame)
fuente_boton = pygame.font.Font(None, 30)  # fuente más chica

clock = pygame.time.Clock()

# Botones más chicos
boton_volver = pygame.Rect(ANCHO // 2 - 250, 600, 200, 60)
boton_salir = pygame.Rect(ANCHO // 2 + 50, 600, 200, 60)

def dibujar_boton(superficie, rect, texto, fuente, color_texto, color_fondo, color_borde):
    pygame.draw.rect(superficie, color_fondo, rect, border_radius=8)
    pygame.draw.rect(superficie, color_borde, rect, width=4, border_radius=8)
    render_texto = fuente.render(texto, True, color_texto)
    superficie.blit(
        render_texto,
        (rect.centerx - render_texto.get_width() // 2,
         rect.centery - render_texto.get_height() // 2)
    )

# Función para volver al menú
def volver_al_menu():
    pygame.quit()
    menu_path = os.path.join(script_dir, "menu.py")
    if os.path.exists(menu_path):
        os.execv(sys.executable, [sys.executable, menu_path])
    else:
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

    # Fondo
    if fondo:
        ventana.blit(fondo, (0, 0))
    else:
        ventana.fill(FALLBACK_BG)

    # Botones
    dibujar_boton(ventana, boton_volver, "Volver", fuente_boton, VERDE_TEXTO, CREMA, VERDE_BORDE)
    dibujar_boton(ventana, boton_salir, "Salir", fuente_boton, VERDE_TEXTO, CREMA, VERDE_BORDE)

    pygame.display.flip()
    clock.tick(30)
