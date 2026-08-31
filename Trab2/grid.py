import pygame
import random

class Cell:
    # Representa uma célula individual dentro da matriz do tabuleiro
    def __init__(self, x, y, size, sprites):
        self.x = x  # Posição X na grade
        self.y = y  # Posição Y na grade
        self.size = size  # Tamanho em pixels
        self.sprites = sprites  # Dicionário com os gráficos
        
        # Estados fundamentais da célula
        self.is_mine = False       # Define se a célula esconde uma bomba
        self.is_revealed = False   # Define se o jogador já clicou/abriu a célula
        self.is_flagged = False    # Define se o jogador marcou com bandeira
        self.neighbor_mines = 0    # Contador de bombas nos 8 blocos vizinhos

    def draw(self, screen, offset_y=0):
        # Desenha a célula na tela de acordo com o seu estado atual
        # Escolhe qual sprite exibir baseado nas flags de estado
        if not self.is_revealed:
            if self.is_flagged:
                img = self.sprites['flag']
            else:
                img = self.sprites['closed']
        else:
            if self.is_mine:
                img = self.sprites['mine']
            elif self.neighbor_mines > 0:
                img = self.sprites[self.neighbor_mines]
            else:
                img = self.sprites['empty']
                
        # Renderiza a imagem respeitando o deslocamento vertical do cabeçalho
        screen.blit(img, (self.x * self.size, (self.y * self.size) + offset_y))


class Grid:
    """Gerencia a matriz de células, distribuição de minas e regras do jogo."""
    def __init__(self, rows, cols, cell_size, num_mines, sprites):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.sprites = sprites
        
        # Criação da matriz 2D (lista de listas) contendo as instâncias de Cell
        self.cells = [[Cell(col, row, cell_size, sprites) for col in range(cols)] for row in range(rows)]
        
        # Posiciona as bombas aleatoriamente e calcula os números vizinhos
        self.place_mines(num_mines)
        self.calculate_neighbors()

    def place_mines(self, num_mines):
        """Distribui as minas aleatoriamente pelo tabuleiro."""
        mines_placed = 0
        while mines_placed < num_mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if not self.cells[r][c].is_mine:
                self.cells[r][c].is_mine = True
                mines_placed += 1

    def calculate_neighbors(self):
        """Calcula quantas minas existem ao redor de cada célula (os 8 vizinhos)."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.cells[r][c].is_mine:
                    continue
                
                count = 0
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        if 0 <= r + i < self.rows and 0 <= c + j < self.cols:
                            if self.cells[r + i][c + j].is_mine:
                                count += 1
                self.cells[r][c].neighbor_mines = count

    def reveal_cell(self, r, c):
        """Revela uma célula e executa a expansão em cascata (Flood Fill) se for vazia."""
        cell = self.cells[r][c]
        if cell.is_revealed or cell.is_flagged:
            return "continue"
            
        cell.is_revealed = True
        
        # Condição de derrota se clicar em uma mina
        if cell.is_mine:
            return "game_over"
            
        # Expansão automática recursiva para blocos com 0 minas vizinhas
        if cell.neighbor_mines == 0:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 <= r + i < self.rows and 0 <= c + j < self.cols:
                        self.reveal_cell(r + i, c + j)
                        
        return "continue"

    def reveal_all_mines(self):
        """Revela todas as minas do tabuleiro ao fim de jogo."""
        for row in self.cells:
            for cell in row:
                if cell.is_mine:
                    cell.is_revealed = True

    def check_win(self):
        """Verifica se todas as células seguras foram abertas (Condição de Vitória)."""
        for row in self.cells:
            for cell in row:
                if not cell.is_mine and not cell.is_revealed:
                    return False
        return True

    def draw(self, screen, offset_y=0):
        """Itera pela matriz e manda cada célula se desenhar na tela."""
        for row in self.cells:
            for cell in row:
                cell.draw(screen, offset_y)