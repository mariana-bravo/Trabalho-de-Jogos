import pygame
from abc import ABC, abstractmethod
from util import colored_sprite, EventHandler
import math

def rotate(pos, angle, axis=(0, 0)):
    angle = math.radians(angle)
    x, y = pos
    ax, ay = axis

    # Translate so axis is the origin
    x -= ax
    y -= ay

    # Rotate
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    rx = x * cos_a - y * sin_a
    ry = x * sin_a + y * cos_a

    # Translate back
    return rx + ax, ry + ay

class Bullet(ABC):
    # Velocidade em pixels/segundo (ex: 600) e tempo de vida em segundos (ex: 3.0)
    def __init__(self, pos, angle=0, radius=8, speed=600, life_time=3.0, color=(255, 255, 0)):
        self.pos = pygame.Vector2(pos)
        self.origin = pygame.Vector2(pos)
        self.life_time = life_time
        self.angle = angle
        self.elapsed = 0
        self.radius = radius
        self.speed = speed
        self.sprite = colored_sprite(color, (self.radius * 2, self.radius * 2))

    def update(self, dt):
        self.elapsed += dt
        if self.life_time and self.elapsed >= self.life_time:
            self.destroy()
            return
        
        rel_pos = self.move()
        self.pos = pygame.Vector2(rotate(rel_pos, self.angle)) + self.origin

    def draw(self, screen):
        # Centraliza o sprite do tiro na posição x, y
        screen.blit(self.sprite, (self.pos.x - self.radius, self.pos.y - self.radius))

    @abstractmethod
    def move(self):
        pass

    def destroy(self):
        EventHandler().notify("DestroyObj", self)

class StraightBullet(Bullet):
    def move(self):
        return pygame.Vector2(0, -self.elapsed * self.speed)

class ZigZagBullet(Bullet):
    def move(self):
        return pygame.Vector2(math.sin(self.elapsed * 12) * 35, -self.elapsed * self.speed)