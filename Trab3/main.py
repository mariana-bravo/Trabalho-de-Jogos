import pygame
import random

# 1. Inicialização do Pygame e criação da tela
pygame.init()
WIDTH = 600; HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Defenda a Torre - Trabalho 3")
clock = pygame.time.Clock()

# 2. Importações das classes e utilitários
from player import Player, NormalTowerState, RapidTowerState, WaveTowerState
from enemy import Enemy
from bullet import Bullet
from util import EventHandler, circle_collistiion

# Carregamento do cenário
FENCE_IMG = pygame.transform.scale(pygame.image.load("images/fence.png"), (32, 32))
GRASS_IMG = pygame.transform.scale(pygame.image.load("images/grass_tile.png"), (64, 64))

# Instanciação inicial do jogador e da lista de objetos
player = Player((WIDTH // 2, HEIGHT - 80))
objects = [player]

# Configuração de fontes
font = pygame.font.SysFont("arial", 16, bold=True)
font_big = pygame.font.SysFont("arial", 32, bold=True)

# Variáveis globais do estado de jogo
game_over = False
start_time = pygame.time.get_ticks()
survival_time = 0
spawn_timer = 0.0

# --- GERENCIAMENTO DE OBJETOS VIA OBSERVER PATTERN ---
def add_obj(obj):
    objects.append(obj)

def remove_obj(obj):
    if obj in objects:
        objects.remove(obj)

EventHandler().subscribe("SpawnObj", add_obj)
EventHandler().subscribe("DestroyObj", remove_obj)

# Reinicia a partida redefinindo o estado inicial do jogo
def reset_game():
    global objects, player, game_over, start_time, survival_time, spawn_timer
    player = Player((WIDTH // 2, HEIGHT - 80))
    objects = [player]
    game_over = False
    start_time = pygame.time.get_ticks()
    survival_time = 0
    spawn_timer = 0.0

# Processa entradas do teclado e mouse
def handle_input():
    global game_over
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not game_over:  # Botão esquerdo do mouse atira
                player.shoot()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:  # Reinicia o jogo a qualquer momento
                reset_game()

            if not game_over:
                if event.key == pygame.K_SPACE:
                    player.shoot()
                elif event.key == pygame.K_a:
                    player.set_state(NormalTowerState)
                elif event.key == pygame.K_s:
                    player.set_state(RapidTowerState)
                elif event.key == pygame.K_d:
                    player.set_state(WaveTowerState)

# Desenha o piso gramado repetido
def draw_background(screen, screen_width, screen_height):
    for x in range(0, screen_width, 64):
        for y in range(0, screen_height, 64):
            screen.blit(GRASS_IMG, (x, y))

# Desenha as cercas divisórias na altura da torre
def draw_boundaries(screen, player_pos, screen_width):
    fence_w = FENCE_IMG.get_width()
    y_pos = player_pos.y - 16

    for x in range(0, int(player_pos.x - 40), fence_w):
        screen.blit(FENCE_IMG, (x, y_pos))

    for x in range(int(player_pos.x + 40), screen_width, fence_w):
        screen.blit(FENCE_IMG, (x, y_pos))

# --- LOOP PRINCIPAL DO JOGO ---
running = True
while running:
    # Calcula delta time (dt) em segundos (~0.016s a 60 FPS)
    dt = clock.tick(60) / 1000.0
    handle_input()

    if not game_over:
        survival_time = (pygame.time.get_ticks() - start_time) // 1000

        # Temporizador para criar um novo inimigo a cada 1.2 segundos
        spawn_timer += dt
        if spawn_timer >= 1.2:
            enemy_x = random.randint(50, WIDTH - 50)
            objects.append(Enemy((enemy_x, 0)))
            spawn_timer = 0.0

        # Atualiza a lógica de cada objeto ativo
        for obj in list(objects):
            obj.update(dt)

        # Processamento de colisões: Projéteis x Inimigos
        bullets = [o for o in objects if isinstance(o, Bullet)]
        enemies = [o for o in objects if isinstance(o, Enemy)]

        for bullet in bullets:
            for enemy in enemies:
                if circle_collistiion(bullet.pos, bullet.radius, enemy.pos, enemy.radius):
                    bullet.destroy()
                    enemy.hit()

        # Checa condição de derrota (Inimigo atinge o jogador ou ultrapassa a linha da torre)
        for enemy in enemies:
            if circle_collistiion(player.pos, player.radius, enemy.pos, enemy.radius) or enemy.pos.y >= player.pos.y:
                game_over = True

    # --- DESENHO NA TELA ---
    draw_background(screen, WIDTH, HEIGHT)
    draw_boundaries(screen, player.pos, WIDTH)

    # Desenha todos os objetos do jogo (jogador, balas, inimigos)
    for obj in objects:
        obj.draw(screen)

    # Interface gráfica e telas de estado
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        go_text = font_big.render("GAME OVER!", True, (255, 80, 80))
        time_text = font.render(f"Você sobreviveu por: {survival_time} segundos", True, (255, 255, 255))
        restart_text = font.render("Aperte 'F' para jogar novamente", True, (0, 255, 150))

        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(time_text, (WIDTH // 2 - time_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
    else:
        status_text = font.render(f"Tempo: {survival_time}s | [A,S,D]: Armas | [Clique/Espaço]: Atirar | [F]: Reset", True, (220, 220, 220))
        screen.blit(status_text, (15, 15))

    pygame.display.flip()