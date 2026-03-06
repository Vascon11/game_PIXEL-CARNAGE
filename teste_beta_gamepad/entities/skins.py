"""
entities/skins.py
Sistema de skins para o jogador e inimigos.
Cada skin define cores/formas sem depender de imagens externas
(mas suporta sprite PNG se disponível em assets/).
"""

import os
import pygame
from dataclasses import dataclass, field
from typing import Callable


ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


@dataclass
class PlayerSkin:
    name: str
    color: tuple          # cor fallback (r, g, b)
    shield_color: tuple   # cor do escudo
    shot_color: tuple     # cor dos projéteis
    sprite_file: str = "" # nome do PNG em assets/ (opcional)
    _sprite: pygame.Surface | None = field(default=None, init=False, repr=False)

    def get_sprite(self, size: int) -> pygame.Surface | None:
        if self.sprite_file:
            path = os.path.join(ASSETS_DIR, self.sprite_file)
            if os.path.exists(path):
                if self._sprite is None:
                    raw = pygame.image.load(path).convert_alpha()
                    self._sprite = pygame.transform.scale(raw, (size, size))
                elif self._sprite.get_width() != size:
                    raw = pygame.image.load(path).convert_alpha()
                    self._sprite = pygame.transform.scale(raw, (size, size))
        return self._sprite


# ── Catálogo de skins do jogador ─────────────────────────────────────────────
PLAYER_SKINS: list[PlayerSkin] = [
    PlayerSkin(
        name="DEFAULT",
        color=(240, 200, 180),
        shield_color=(100, 200, 255),
        shot_color=(100, 200, 255),
        sprite_file="IA_jogador.png",
    ),
    PlayerSkin(
        name="CYBER",
        color=(50, 220, 255),
        shield_color=(0, 255, 180),
        shot_color=(0, 255, 180),
    ),
    PlayerSkin(
        name="INFERNO",
        color=(255, 80, 30),
        shield_color=(255, 160, 0),
        shot_color=(255, 120, 0),
    ),
    PlayerSkin(
        name="GHOST",
        color=(200, 200, 240),
        shield_color=(180, 140, 255),
        shot_color=(180, 140, 255),
    ),
    PlayerSkin(
        name="TOXIC",
        color=(80, 255, 80),
        shield_color=(0, 200, 50),
        shot_color=(100, 255, 100),
    ),
]


def get_skin(name: str) -> PlayerSkin:
    for s in PLAYER_SKINS:
        if s.name == name.upper():
            return s
    return PLAYER_SKINS[0]


def next_skin(current: PlayerSkin) -> PlayerSkin:
    idx = PLAYER_SKINS.index(current)
    return PLAYER_SKINS[(idx + 1) % len(PLAYER_SKINS)]


def prev_skin(current: PlayerSkin) -> PlayerSkin:
    idx = PLAYER_SKINS.index(current)
    return PLAYER_SKINS[(idx - 1) % len(PLAYER_SKINS)]
