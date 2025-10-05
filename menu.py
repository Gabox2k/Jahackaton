import pygame
import sys

pygame.init()

#configuracion de la ventana
ancho, alto = 1152, 758
ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Tembi'u Rush - Menú Principal")

#fondo
fondo = pygame.image.load("menu.png").convert()
fondo = pygame.transform.scale(fondo, (ancho, alto))

fondo_inst = pygame.image.load("fondo_instrucciones.jpg").convert()
fondo_inst = pygame.transform.scale(fondo_inst,(ancho, alto))


#Colores de estilo
crema = (252, 242, 210)
verde_borde = (64, 128, 64)
verde_texto = (48, 96, 48)

#Las fuentes de pixel-art
try:
    fuente_pixel = pygame.font.Font("PressStart2P-Regular.ttf", 40)
except:
    fuente_pixel = pygame.font.Font(None, 60)

#Rectangulos de los botones
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

pantalla_juego = False

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if evento.type == pygame.MOUSEBUTTONDOWN:
            if not pantalla_juego:
                if boton_juego.collidepoint(evento.pos):
                    pantalla_juego = True
                    print("Iniciando el juego")
                if boton_salir.collidepoint(evento.pos):
                    pygame.quit()
                    sys.exit()
        
    if pantalla_juego:
        ventana.blit(fondo_inst, (0, 0))
    else:
        ventana.blit(fondo, (0, 0))   
        #Dibujar botones estilo pixel-art
        dibujar_boton(ventana, boton_juego, "Jugar", fuente_pixel, verde_texto, crema, verde_borde)
        dibujar_boton(ventana, boton_salir, "Salir", fuente_pixel, verde_texto, crema, verde_borde)

    pygame.display.flip()
    clock.tick(30)