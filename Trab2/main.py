import pygame
import os
from grid import Grid

# Inicialização da biblioteca Pygame
pygame.init()
FPS = 60
CELL_SIZE = 32
ROWS, COLS = 10, 10
NUM_MINES = 10
HEADER_HEIGHT = 45  # Altura reservada no topo para a exibição de textos informativos

WIDTH = COLS * CELL_SIZE
HEIGHT = (ROWS * CELL_SIZE) + HEADER_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Campo Minado - Trabalho 2")
clock = pygame.time.Clock()

# Configuração de fonte para renderização de textos na interface
font = pygame.font.SysFont(None, 24)

# Carregamento e fatiamento da Sprite Sheet de gráficos
image_path = os.path.join("images", "minesweeper.png")
sprite_sheet = pygame.image.load(image_path).convert_alpha()
orig_w = sprite_sheet.get_width() // 4
orig_h = sprite_sheet.get_height() // 4

def get_sprite(col, row):
    # Recorta o sprite e redimensiona para o tamanho da célula
    rect = pygame.Rect(col * orig_w, row * orig_h, orig_w, orig_h)
    image = sprite_sheet.subsurface(rect)
    return pygame.transform.scale(image, (CELL_SIZE, CELL_SIZE))

# Dicionário de mapeamento de assets visuais
sprites = {
    'mine': get_sprite(0, 0),
    'flag': get_sprite(2, 0),
    1: get_sprite(0, 1),
    2: get_sprite(1, 1),
    3: get_sprite(2, 1),
    4: get_sprite(3, 1),
    5: get_sprite(0, 2),
    6: get_sprite(1, 2),
    7: get_sprite(2, 2),
    8: get_sprite(3, 2),
    'empty': get_sprite(2, 3),
    'closed': get_sprite(3, 3)
}

def reset_game():
    # Reinicia o estado da partida criando uma nova grade
    return Grid(ROWS, COLS, CELL_SIZE, NUM_MINES, sprites), False, False

game_grid, game_over, won = reset_game()

# --- LOOP PRINCIPAL DO JOGO ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # Entrada via teclado (R para reiniciar, ESC para sair do programa)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                game_grid, game_over, won = reset_game()
            elif event.key == pygame.K_ESCAPE:
                running = False
            
        # Entrada via mouse (Cliques no tabuleiro)
        if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not won:
            x, y = pygame.mouse.get_pos()
            
            # Valida se o clique ocorreu dentro da área do tabuleiro (abaixo do cabeçalho de texto)
            if y >= HEADER_HEIGHT:
                col = x // CELL_SIZE
                row = (y - HEADER_HEIGHT) // CELL_SIZE
                
                if 0 <= row < ROWS and 0 <= col < COLS:
                    # Botão esquerdo do mouse (Revelar célula)
                    if event.button == 1: 
                        result = game_grid.reveal_cell(row, col)
                        if result == "game_over":
                            game_over = True
                            game_grid.reveal_all_mines()
                    # Botão direito do mouse (Alternar bandeira)
                    elif event.button == 3: 
                        if not game_grid.cells[row][col].is_revealed:
                            game_grid.cells[row][col].is_flagged = not game_grid.cells[row][col].is_flagged
                    
                    # Verifica condição de vitória a cada clique
                    if not game_over and game_grid.check_win():
                        won = True

    # Renderização visual dos elementos na tela
    screen.fill((30, 30, 30))
    
    # Exibe mensagens textuais informativas no painel superior
    if won:
        status_text = font.render("Vitoria! Aperte 'R'", True, (0, 255, 120))
    elif game_over:
        status_text = font.render("Game Over! Aperte 'R'", True, (255, 90, 90))
    else:
        status_text = font.render("Jogando | Mouse / R: Reiniciar", True, (220, 220, 220))
        
    screen.blit(status_text, (15, 12))
    
    # Desenha o tabuleiro abaixo do cabeçalho de texto
    game_grid.draw(screen, HEADER_HEIGHT)
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()