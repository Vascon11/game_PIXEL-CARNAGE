"""
entities/boss.py
Bosses separados dos inimigos normais.

Fluxo:
- TITAN      -> ao morrer vira 2 SENTINELAS
- SENTINELA  -> ao morrer vira 2 FRAGMENTOS
- FRAGMENTO  -> forma final

Também concentra:
- nomes de anúncio
- comportamento especial
- spawn de lacaios do boss principal
"""

import math
import random
import pygame

from game import style
from game.config import BOSS_LACAIO_INTERVALO
from entities.enemy import Enemy, TIPO_LACAIO

TIPO_TITAN = "BOSS_TITAN"
TIPO_SENTINELA = "BOSS_SENTINELA"
TIPO_FRAGMENTO = "BOSS_FRAGMENTO"

BOSS_TYPES = {TIPO_TITAN, TIPO_SENTINELA, TIPO_FRAGMENTO}

_BOSS_COLOR_MAP = {
    TIPO_TITAN: style.BOSS_MAIN,
    TIPO_SENTINELA: style.BOSS_MEDIO,
    TIPO_FRAGMENTO: style.BOSS_PEQUENO,
}

_BOSS_LABEL_MAP = {
    TIPO_TITAN: "TITAN",
    TIPO_SENTINELA: "SENTINELA",
    TIPO_FRAGMENTO: "FRAGMENTO",
}

_BOSS_ANNOUNCEMENTS = [
    "TITAN DE COMBATE DETECTADO!",
    "A SENTINELA ESTÁ EM CAMPO!",
    "FRAGMENTOS HOSTIS SE APROXIMAM!",
    "A ESTRUTURA TITAN DESPERTOU!",
    "SINAL DE CHEFE CONFIRMADO!",
    "ANOMALIA BÉLICA EMERGINDO!",
]


def is_boss_type(tipo: str) -> bool:
    return tipo in BOSS_TYPES


def random_boss_name() -> str:
    return random.choice(_BOSS_ANNOUNCEMENTS)


class BossEnemy:
    def __init__(self, x, y, velocidade, vida, raio, tipo):
        self.pos = pygame.Vector2(x, y)
        self.vel_base = velocidade
        self.vida = vida
        self.max_vida = vida
        self.raio = raio
        self.tipo = tipo

        self._ultimo_spawn = pygame.time.get_ticks()
        self._seed = random.uniform(0.0, 10.0)

    def update(self, target_pos: pygame.Vector2) -> list:
        agora = pygame.time.get_ticks()
        novos = []

        direcao = target_pos - self.pos
        if direcao.length() > 0:
            direcao = direcao.normalize()

        if self.tipo == TIPO_TITAN:
            self.pos += direcao * self.vel_base

            if agora - self._ultimo_spawn > BOSS_LACAIO_INTERVALO:
                offset = pygame.Vector2(random.randint(-18, 18), random.randint(-18, 18))
                novos.append(
                    Enemy(
                        self.pos.x + offset.x,
                        self.pos.y + offset.y,
                        2.5,
                        1,
                        15,
                        TIPO_LACAIO,
                    )
                )
                self._ultimo_spawn = agora

        elif self.tipo == TIPO_SENTINELA:
            # Persegue o jogador com leve desvio lateral
            lateral = pygame.Vector2(-direcao.y, direcao.x)
            drift = math.sin((agora / 220.0) + self._seed) * 0.55
            movimento = direcao + (lateral * drift)
            if movimento.length() > 0:
                movimento = movimento.normalize()
            self.pos += movimento * self.vel_base

        elif self.tipo == TIPO_FRAGMENTO:
            # Movimento mais agressivo / "nervoso"
            lateral = pygame.Vector2(-direcao.y, direcao.x)
            zigzag = math.sin((agora / 120.0) + self._seed) * 0.35
            movimento = direcao + (lateral * zigzag)
            if movimento.length() > 0:
                movimento = movimento.normalize()
            self.pos += movimento * self.vel_base

        return novos

    def draw(self, surface: pygame.Surface, fonte_pequena):
        agora = pygame.time.get_ticks()
        cor = _BOSS_COLOR_MAP.get(self.tipo, style.BOSS_MAIN)

        pygame.draw.circle(surface, cor, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.pos.x), int(self.pos.y)), self.raio, 2)

        pulse = 0
        if self.tipo == TIPO_TITAN:
            pulse = abs(math.sin(agora / 380)) * 6
        elif self.tipo == TIPO_SENTINELA:
            pulse = abs(math.sin(agora / 280)) * 4
        elif self.tipo == TIPO_FRAGMENTO:
            pulse = abs(math.sin(agora / 180)) * 3

        pygame.draw.circle(
            surface,
            cor,
            (int(self.pos.x), int(self.pos.y)),
            int(self.raio + pulse),
            2,
        )

        # Barra de vida
        bar_w = self.raio * 2
        bar_h = 5
        bx = int(self.pos.x) - self.raio
        by = int(self.pos.y) - self.raio - 10
        pygame.draw.rect(surface, (60, 20, 20), (bx, by, bar_w, bar_h))
        fill = int(bar_w * (self.vida / self.max_vida))
        if fill > 0:
            pygame.draw.rect(surface, (220, 50, 50), (bx, by, fill, bar_h))

        # Valor de vida no centro
        txt = fonte_pequena.render(str(int(self.vida)), True, (255, 255, 255))
        surface.blit(txt, (self.pos.x - txt.get_width() // 2, self.pos.y - txt.get_height() // 2))

        # Nome do boss acima
        label = _BOSS_LABEL_MAP.get(self.tipo, "BOSS")
        lbl = fonte_pequena.render(label, True, (255, 255, 255))
        surface.blit(lbl, (self.pos.x - lbl.get_width() // 2, by - 16))

    def compensate_pause(self, pause_ms: int):
        self._ultimo_spawn += pause_ms