import pygame
import sys

pygame.init()

#Configuracion de pantalla
ancho, alto = 1152, 758
ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Tembi'u Rush - Menú Principal")

#Fondos
fondo = pygame.image.load("menu.png").convert()
fondo = pygame.transform.scale(fondo, (ancho, alto))

fondo_bosque = pygame.image.load("fondo_instrucciones.jpg").convert()
fondo_bosque = pygame.transform.scale(fondo_bosque, (ancho, alto))

#Colores
crema = (252, 242, 210)
verde_borde = (64, 128, 64)
verde_texto = (48, 96, 48)

#Colores del texto
beige_claro = (247, 228, 178)      # #F7E4B2
blanco_roto = (250, 248, 232)      # #FAF8E8
naranja_calido = (230, 126, 34)    # #E67E22
rojo_terroso = (183, 65, 14)       # #B7410E
amarillo_mostaza = (241, 196, 15)  # #F1C40F
negro = (0, 0, 0)

#Fuentes usando SysFont
fuente_texto = pygame.font.SysFont("Arial", 22)   # texto con instrucciones
fuente_botones = pygame.font.SysFont("Arial", 42) # botones

#Botones
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

#Texto con instrucciones
lineas_texto = [
    ("Objetivo:", naranja_calido),
    ("Prepará y entregá los pedidos a tiempo para ganar.", blanco_roto),
    ("Cada pedido entregado suma 100$, los que eches a perder te restaran 50$.", blanco_roto),
    ("Controles:", naranja_calido),
    ("Jugador 1 → WASD + E", blanco_roto),
    ("Jugador 2 → Flechas + Enter", blanco_roto),
    ("Acciones:", naranja_calido),
    ("Tomá ingredientes", blanco_roto),
    ("Cortá y cociná", blanco_roto),
    ("Emplatá", blanco_roto),
]

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
        ventana.blit(fondo_bosque, (0, 0))

        #Texto centrado con sombra
        espacio = 30  #separacion entre lineas
        alturas_lineas = [fuente_texto.render(linea, True, color).get_height() for linea, color in lineas_texto]
        alto_total = sum(alturas_lineas) + espacio * (len(lineas_texto) - 1)
        y_inicio = (alto - alto_total) // 2 - 100  

        y = y_inicio
        for linea, color in lineas_texto:
            render_texto = fuente_texto.render(linea, True, color)
            x = (ancho - render_texto.get_width()) // 2
            #Sombra negras
            ventana.blit(fuente_texto.render(linea, True, negro), (x + 2, y + 2))
            #Texto principal
            ventana.blit(render_texto, (x, y))
            y += render_texto.get_height() + espacio

    else:
        ventana.blit(fondo, (0, 0))
        #Botones con fuentes
        dibujar_boton(ventana, boton_juego, "Jugar", fuente_botones, verde_texto, crema, verde_borde)
        dibujar_boton(ventana, boton_salir, "Salir", fuente_botones, verde_texto, crema, verde_borde)

    pygame.display.flip()
    clock.tick(30)
