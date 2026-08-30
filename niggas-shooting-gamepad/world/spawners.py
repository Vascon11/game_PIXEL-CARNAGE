"""
world/spawners.py
Funções de spawn de inimigos normais e bosses.
"""

import random

from game.config import LARGURA, ALTURA, ALTURA_HUD
from entities.enemy import Enemy, TIPO_NORMAL, TIPO_AGIL
from entities.boss import BossEnemy, TIPO_TITAN, TIPO_SENTINELA, TIPO_FRAGMENTO, random_boss_name


def _borda_aleatoria() -> tuple[float, float]:
    lado = random.choice(["T", "B", "L", "R"])
    if lado == "T":
        return random.uniform(0, LARGURA), float(ALTURA_HUD - 40)
    if lado == "B":
        return random.uniform(0, LARGURA), float(ALTURA + 40)
    if lado == "L":
        return -40.0, random.uniform(ALTURA_HUD, ALTURA)
    return float(LARGURA + 40), random.uniform(ALTURA_HUD, ALTURA)


def spawn_enemy(wave: int) -> Enemy:
    x, y = _borda_aleatoria()

    vida_base = 1 + (wave // 4)
    raio = 18
    vel = min(1.2 + (wave * 0.15), 3.8)
    tipo = TIPO_NORMAL

    if wave >= 3 and random.random() < 0.30:
        tipo = TIPO_AGIL
        raio = 12
        vel = min(2.5 + (wave * 0.2), 5.5)
        vida_base = max(1, vida_base - 1)

    if wave >= 7:
        vida_base = 10 if tipo == TIPO_AGIL else vida_base * 3

    if wave >= 10:
        vida_base = int(vida_base * (1.2 ** (wave - 9)))

    chance_elite = 0.10 if wave == 6 else 0.20 if wave >= 7 else 0
    if random.random() < chance_elite:
        raio = 36
        vida_base *= 2

    return Enemy(x, y, vel, max(1, vida_base), raio, tipo)


def spawn_boss(wave: int) -> BossEnemy:
    vida = 100
    if wave >= 10:
        vida += ((wave // 5) - 1) * 100
    return BossEnemy(LARGURA / 2, float(ALTURA_HUD - 50), 0.6, vida, 60, TIPO_TITAN)


def spawn_boss_medio(x: float, y: float) -> BossEnemy:
    return BossEnemy(x - 30, y, 1.15, 34, 35, TIPO_SENTINELA)


def spawn_boss_medio_r(x: float, y: float) -> BossEnemy:
    return BossEnemy(x + 30, y, 1.15, 34, 35, TIPO_SENTINELA)


def spawn_boss_pequeno(x: float, y: float) -> BossEnemy:
    return BossEnemy(x - 20, y, 1.9, 16, 20, TIPO_FRAGMENTO)


def spawn_boss_pequeno_r(x: float, y: float) -> BossEnemy:
    return BossEnemy(x + 20, y, 1.9, 16, 20, TIPO_FRAGMENTO)