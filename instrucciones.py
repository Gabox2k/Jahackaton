import pygame
import os
import sys

pygame.init()

# Ventana
ANCHO, ALTO = 1152, 758
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Globitos mensajes")

# Colores
NEGRO = (0, 0, 0)

# Directorio actual
script_dir = os.path.dirname(os.path.abspath(__file__))
ruta_globo_chef = os.path.join(script_dir, "globito_chef.png")     # flechita izquierda
ruta_globo_cliente = os.path.join(script_dir, "globito_cliente.png")  # flechita derecha

# Cargar globitos
globito_chef = pygame.image.load(ruta_globo_chef).convert_alpha()
globito_cliente = pygame.image.load(ruta_globo_cliente).convert_alpha()

# Escalar tamaño
globito_chef = pygame.transform.scale(globito_chef, (500, 150))
globito_cliente = pygame.transform.scale(globito_cliente, (500, 150))

# Posiciones en pantalla
rect_chef = pygame.Rect(100, 100, globito_chef.get_width(), globito_chef.get_height())
rect_cliente = pygame.Rect(600, 100, globito_cliente.get_width(), globito_cliente.get_height())

# Mensajes (texto + tipo de globito)
mensajes = [
    ("Llegó un pedido de mbejú", "cliente"),
    ("Llegó un pedido de pastel mandi’o", "cliente"),
    ("¡La comida se está quemando!", "chef"),
    ("¡Más rápido, se acaba el tiempo!", "chef"),
]
indice = 0
tiempo_cambio = 3000  # 3 segundos
ultimo_cambio = pygame.time.get_ticks()

clock = pygame.time.Clock()

def render_texto_ajustado(texto, fuente_base, color, max_width):
    palabras = texto.split(" ")
    lineas = []
    linea_actual = ""

    for palabra in palabras:
        test_linea = linea_actual + palabra + " "
        if fuente_base.size(test_linea)[0] <= max_width:
            linea_actual = test_linea
        else:
            lineas.append(linea_actual)
            linea_actual = palabra + " "
    lineas.append(linea_actual)

    superficies = [fuente_base.render(linea.strip(), True, color) for linea in lineas]
    return superficies

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Cambio automático de mensaje
    ahora = pygame.time.get_ticks()
    if ahora - ultimo_cambio > tiempo_cambio:
        indice = (indice + 1) % len(mensajes)
        ultimo_cambio = ahora

    ventana.fill((30, 30, 30))  # fondo

    texto, tipo = mensajes[indice]
    fuente = pygame.font.Font(None, 36)

    if tipo == "chef":
        ventana.blit(globito_chef, rect_chef.topleft)
        superficies_lineas = render_texto_ajustado(texto, fuente, NEGRO, rect_chef.width - 20)
        total_alto = sum(s.get_height() for s in superficies_lineas)
        y_offset = rect_chef.y + (rect_chef.height - total_alto) // 2
        for s in superficies_lineas:
            ventana.blit(s, (rect_chef.x + (rect_chef.width - s.get_width()) // 2, y_offset))
            y_offset += s.get_height()

    elif tipo == "cliente":
        ventana.blit(globito_cliente, rect_cliente.topleft)
        superficies_lineas = render_texto_ajustado(texto, fuente, NEGRO, rect_cliente.width - 20)
        total_alto = sum(s.get_height() for s in superficies_lineas)
        y_offset = rect_cliente.y + (rect_cliente.height - total_alto) // 2
        for s in superficies_lineas:
            ventana.blit(s, (rect_cliente.x + (rect_cliente.width - s.get_width()) // 2, y_offset))
            y_offset += s.get_height()

    pygame.display.flip()
    clock.tick(30)
