import pygame
import sys

pygame.init()

# Configuración de ventana
ancho, alto = 1152, 758
ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Tembi'u Rush - Menú Principal")

# Fondo
fondo = pygame.image.load("menu.png").convert()
fondo = pygame.transform.scale(fondo, (ancho, alto))

# Colores estilo pixel-art
crema = (252, 242, 210)
verde_borde = (64, 128, 64)
verde_texto = (48, 96, 48)

# Fuente pixel art
try:
    fuente_pixel = pygame.font.Font("PressStart2P-Regular.ttf", 40)
except:
    fuente_pixel = pygame.font.Font(None, 60)

# Rectángulos de botones (uno al lado del otro)
boton_juego = pygame.Rect(ancho // 2 - 400, 600, 300, 80)
boton_salir = pygame.Rect(ancho // 2 + 100, 600, 300, 80)

clock = pygame.time.Clock()

def dibujar_boton(superficie, rect, texto, fuente, color_texto, color_fondo, color_borde):
    pygame.draw.rect(superficie, color_fondo, rect, border_radius=10)
    pygame.draw.rect(superficie, color_borde, rect, width=6, border_radius=10)
    render_texto = fuente.render(texto, True, color_texto)
    superficie.blit(
        render_texto,
        (rect.centerx - render_texto.get_width() // 2,
         rect.centery - render_texto.get_height() // 2)
    )

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if boton_juego.collidepoint(evento.pos):
                print("Iniciando el juego")
            if boton_salir.collidepoint(evento.pos):
                pygame.quit()
                sys.exit()
    
    ventana.blit(fondo, (0, 0))

    # Dibujar botones estilo pixel-art
    dibujar_boton(ventana, boton_juego, "Jugar", fuente_pixel, verde_texto, crema, verde_borde)
    dibujar_boton(ventana, boton_salir, "Salir", fuente_pixel, verde_texto, crema, verde_borde)

    pygame.display.flip()
    clock.tick(30)