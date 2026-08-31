# Inicialização
import pygame 
import random
pygame.init()
pygame.font.init()



font = font = pygame.font.Font(None, 50)
Nome = "Mariana"
rect =  (260, 100, 175, 35)

random.seed(Nome)
x, y =  random.randint(0, 500), random.randint(0, 400)

print(y)

# Renderiza o texto para capturar a largura e altura exatas da fonte
text_surface = font.render(Nome, True, (0, 0, 0))
text_width, text_height = text_surface.get_size()

# Ajusta o retângulo para ter o tamanho do texto e ficar na mesma posição (x, y)
rect = (x, y, text_width, text_height)

# Cria a janela
WIDTH   =  800; HEIGHT =  600
screen = pygame.display.set_mode((WIDTH, HEIGHT))  

#loop
while True: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        # Desenha
        screen.fill((30, 30, 30))
        pygame.draw.rect(screen, (255,255,255), rect)
        screen.blit(font.render(Nome, True, (0,0,0)), (x, y))
        pygame.display.flip()
