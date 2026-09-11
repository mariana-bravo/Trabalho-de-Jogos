import pygame
from abc import ABC, abstractmethod
from util import EventHandler

# Classe principal do inimigo
class Enemy:
    frames = []  # Lista estática para armazenar os quadros de animação

    @classmethod
    def load_frames(cls):
        # Carrega os quadros da folha de sprites (spritesheet) apenas uma vez
        if not cls.frames:
            sheet = pygame.image.load("images/enemy.png").convert_alpha()
            w = sheet.get_width() // 6
            h = sheet.get_height()
            cls.frames = [
                pygame.transform.scale(sheet.subsurface((i * w, 0, w, h)), (48, 48))
                for i in range(6)
            ]

    def __init__(self, pos):
        Enemy.load_frames()

        self.pos = pygame.Vector2(pos)
        self.speed = 90
        self.radius = 20  # Raio usado para detecção de colisões
        
        self.current_frame = 0
        self.anim_timer = 0
        self.image = Enemy.frames[0]
        self.state = ApproachingState(self)  # Estado inicial

    def update(self, dt):
        self.state.update(dt)

    def draw(self, screen):
        self.state.draw(screen)

    def hit(self):
        self.state.on_hit()

    def destroy(self):
        # Notifica o jogo para remover este inimigo da lista de objetos
        EventHandler().notify("DestroyObj", self)

# Classe base abstrata para os estados do inimigo (Pattern State)
class EnemyState(ABC):
    def __init__(self, enemy):
        self.enemy = enemy

    @abstractmethod
    def update(self, dt):
        pass

    def draw(self, screen):
        # Desenha o sprite centralizado na posição do inimigo
        screen.blit(self.enemy.image, (self.enemy.pos.x - 24, self.enemy.pos.y - 24))

    def on_hit(self):
        pass

# --- ESTADO 1: APROXIMANDO-SE ---
class ApproachingState(EnemyState):
    def update(self, dt):
        # Movimentação descendente baseada no delta time (dt)
        self.enemy.pos.y += self.enemy.speed * dt

        # Atualiza a animação de caminhada
        self.enemy.anim_timer += dt
        if self.enemy.anim_timer >= 0.12:
            self.enemy.anim_timer = 0
            self.enemy.current_frame = (self.enemy.current_frame + 1) % len(Enemy.frames)
            self.enemy.image = Enemy.frames[self.enemy.current_frame]

        # Se ultrapassar a parte inferior da tela, é destruído
        if self.enemy.pos.y > 600:
            self.enemy.destroy()

    def on_hit(self):
        # Transiciona para o estado atordoado ao sofrer dano
        self.enemy.state = StunnedState(self.enemy)

# --- ESTADO 2: ATORDOADO (STUNNED) ---
class StunnedState(EnemyState):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.stun_timer = 0.25  # Duração do atordoamento em segundos

    def update(self, dt):
        self.stun_timer -= dt
        # Leve recuo para trás devido ao impacto do tiro
        self.enemy.pos.y -= 25 * dt 
        self.enemy.image = Enemy.frames[0]  # Trava no primeiro quadro

        if self.stun_timer <= 0:
            self.enemy.destroy()