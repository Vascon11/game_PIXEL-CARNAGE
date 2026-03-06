"""
entities/projectile.py
Projétil padrão, com suporte a ricochete e modo boomerang (do Pixel Carnage).
"""

import pygame
from game.config import LARGURA, ALTURA, ALTURA_HUD
from game import style


class Projectile:
    def __init__(
        self,
        x: float,
        y: float,
        vel_x: float,
        vel_y: float,
        bounces: int = 0,
        boomerang: bool = False,
        shot_color: tuple = style.SHOT,
        dano: int = 1,
    ):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vel_x, vel_y)
        self.raio = 6
        self.bounces_restantes = bounces
        self.boomerang = boomerang
        self.nascimento = pygame.time.get_ticks()
        self.shot_color = shot_color
        self.dano = dano

    def update(self, player_pos: pygame.Vector2 | None = None):
        agora = pygame.time.get_ticks()

        # Lógica do boomerang: depois de 400ms volta para o jogador
        if self.boomerang and player_pos and agora - self.nascimento > 400:
            direcao = player_pos - self.pos
            if direcao.length() > 0:
                self.vel += direcao.normalize() * 0.8
            if self.vel.length() > 15:
                self.vel = self.vel.normalize() * 15

        self.pos += self.vel

        # Ricochete (só para projéteis não-boomerang)
        if self.bounces_restantes > 0 and not self.boomerang:
            if self.pos.x <= 0 or self.pos.x >= LARGURA:
                self.vel.x *= -1
                self.bounces_restantes -= 1
            if self.pos.y <= ALTURA_HUD or self.pos.y >= ALTURA:
                self.vel.y *= -1
                self.bounces_restantes -= 1

    def draw(self, surface: pygame.Surface):
        cor = style.SHOT_BOOM if self.boomerang else self.shot_color
        pygame.draw.circle(surface, cor, (int(self.pos.x), int(self.pos.y)), self.raio)
        if self.boomerang:
            pygame.draw.circle(surface, (255, 255, 200), (int(self.pos.x), int(self.pos.y)), self.raio, 2)

    def is_outside(self) -> bool:
        return not (0 <= self.pos.x <= LARGURA and ALTURA_HUD <= self.pos.y <= ALTURA)
