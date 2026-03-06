"""
entities/enemy.py
Inimigos normais do jogo.
Bosses ficam separados em entities/boss.py.
"""

import pygame

from game import style

TIPO_NORMAL = "NORMAL"
TIPO_AGIL = "AGIL"
TIPO_LACAIO = "LACAIO"

_COR_MAP = {
    TIPO_NORMAL: style.ENEMY_NORMAL,
    TIPO_AGIL: style.ENEMY_AGIL,
    TIPO_LACAIO: style.ENEMY_LACAIO,
}


class Enemy:
    def __init__(self, x, y, velocidade, vida, raio=18, tipo=TIPO_NORMAL):
        self.pos = pygame.Vector2(x, y)
        self.vel_base = velocidade
        self.raio = raio
        self.vida = vida
        self.max_vida = vida
        self.tipo = tipo
        self._ultimo_spawn = pygame.time.get_ticks()

    def update(self, target_pos: pygame.Vector2) -> list:
        direcao = target_pos - self.pos
        if direcao.length() > 0:
            direcao = direcao.normalize()
        self.pos += direcao * self.vel_base
        return []

    def draw(self, surface: pygame.Surface, fonte_pequena):
        cor = _COR_MAP.get(self.tipo, style.ENEMY_NORMAL)

        pygame.draw.circle(surface, cor, (int(self.pos.x), int(self.pos.y)), self.raio)

        if self.raio > 20:
            pygame.draw.circle(surface, (0, 0, 0), (int(self.pos.x), int(self.pos.y)), self.raio, 2)

        if self.max_vida > 1:
            bar_w = self.raio * 2
            bar_h = 4
            bx = int(self.pos.x) - self.raio
            by = int(self.pos.y) - self.raio - 8
            pygame.draw.rect(surface, (60, 20, 20), (bx, by, bar_w, bar_h))
            fill = int(bar_w * (self.vida / self.max_vida))
            if fill > 0:
                pygame.draw.rect(surface, (220, 50, 50), (bx, by, fill, bar_h))

    def compensate_pause(self, pause_ms: int):
        self._ultimo_spawn += pause_ms