import pygame
import math
from abc import ABC, abstractmethod
from util import EventHandler
from bullet import StraightBullet, ZigZagBullet

# Função auxiliar para carregar e recortar o 1º quadro do spritesheet da torre
def load_tower_sprite(path, width, height, num_frames=6):
    sheet = pygame.image.load(path).convert_alpha()
    frame_w = sheet.get_width() // num_frames
    frame_h = sheet.get_height()
    first_frame = sheet.subsurface((0, 0, frame_w, frame_h))
    return pygame.transform.scale(first_frame, (width, height))

# Carregamento das imagens de cada variante de torre
TOWER_NORMAL_IMG = load_tower_sprite("images/tower_normal.png", 72, 96)
TOWER_RAPID_IMG = load_tower_sprite("images/tower_rapid.png", 72, 96)
TOWER_WAVE_IMG = load_tower_sprite("images/tower_wave.png", 72, 96)

# Classe do jogador/torre
class Player:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 24  # Raio de colisão com inimigos
        self.state = NormalTowerState(self)

    def update(self, dt):
        self.state.update(dt)

    def draw(self, screen):
        self.state.draw_aim(screen)  # Desenha a linha de mira da arma atual
        self.state.draw(screen)      # Desenha a torre do jogador por cima

    def shoot(self):
        self.state.shoot()

    def set_state(self, new_state_cls):
        self.state = new_state_cls(self)

# Classe base abstrata para as variantes de arma/estado da torre
class PlayerState(ABC):
    def __init__(self, player):
        self.player = player

    def draw(self, screen):
        rect = self.sprite.get_rect(center=(self.player.pos.x, self.player.pos.y))
        screen.blit(self.sprite, rect)
        
    def update(self, dt):
        pass

    def draw_aim(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.line(screen, (100, 100, 100), self.player.pos, mouse_pos, 1)

    # Calcula o ângulo em graus em direção à posição do mouse
    def get_aim_angle(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        direction = pygame.Vector2(mouse_x - self.player.pos.x, mouse_y - self.player.pos.y)
        if direction.length() == 0:
            return 0
        return pygame.Vector2(0, -1).angle_to(direction)

    @abstractmethod
    def shoot(self):
        pass

# --- 1. TORRE NORMAL / SNIPER: Tiro único, direto e muito rápido ---
class NormalTowerState(PlayerState):
    sprite = TOWER_NORMAL_IMG

    def draw_aim(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.line(screen, (0, 200, 255), self.player.pos, mouse_pos, 1)

    def shoot(self):
        angle = self.get_aim_angle()
        bullet = StraightBullet((self.player.pos.x, self.player.pos.y), angle=angle, speed=750, color=(0, 255, 255))
        EventHandler().notify("SpawnObj", bullet)

# --- 2. TORRE RÁPIDA / ESCOPETA: Dispara 3 projéteis em leque com alcance limitado ---
class RapidTowerState(PlayerState):
    sprite = TOWER_RAPID_IMG

    def draw_aim(self, screen):
        angle = self.get_aim_angle()
        # Linhas guia mostrando o leque do disparo
        for a in [angle - 18, angle, angle + 18]:
            rad = math.radians(a - 90)
            end_x = int(self.player.pos.x + math.cos(rad) * 100)
            end_y = int(self.player.pos.y + math.sin(rad) * 100)
            pygame.draw.line(screen, (255, 215, 0), self.player.pos, (end_x, end_y), 1)

    def shoot(self):
        angle = self.get_aim_angle()
        b1 = StraightBullet((self.player.pos.x, self.player.pos.y), angle=angle, speed=500, life_time=0.8, color=(255, 215, 0))
        b2 = StraightBullet((self.player.pos.x, self.player.pos.y), angle=angle - 18, speed=500, life_time=0.8, color=(255, 215, 0))
        b3 = StraightBullet((self.player.pos.x, self.player.pos.y), angle=angle + 18, speed=500, life_time=0.8, color=(255, 215, 0))
        
        EventHandler().notify("SpawnObj", b1)
        EventHandler().notify("SpawnObj", b2)
        EventHandler().notify("SpawnObj", b3)

# --- 3. TORRE ONDA: Projétil ondulado em zig-zag ---
class WaveTowerState(PlayerState):
    sprite = TOWER_WAVE_IMG

    def draw_aim(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.line(screen, (255, 0, 128), self.player.pos, mouse_pos, 1)

    def shoot(self):
        angle = self.get_aim_angle()
        bullet = ZigZagBullet((self.player.pos.x, self.player.pos.y), angle=angle, speed=450, color=(255, 0, 128))
        EventHandler().notify("SpawnObj", bullet)