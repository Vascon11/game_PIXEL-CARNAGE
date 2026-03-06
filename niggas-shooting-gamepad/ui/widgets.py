"""
ui/widgets.py
Widgets reutilizáveis de UI: painéis, overlays, títulos, badges, grade de jogo.
"""

import pygame
from game import style
from game.config import LARGURA, ALTURA, ALTURA_HUD


def _rgba(size):
    return pygame.Surface(size, pygame.SRCALPHA)


def draw_panel(surface: pygame.Surface, rect: pygame.Rect, radius=style.RADIUS):
    """Painel com sombra + borda + fundo semi-transparente."""
    # Sombra
    sr = rect.copy()
    sr.x += style.SHADOW_OFF[0]
    sr.y += style.SHADOW_OFF[1]
    shadow = _rgba((sr.w, sr.h))
    pygame.draw.rect(shadow, (*style.PANEL_SHADOW, style.PANEL_SHADOW_ALPHA), shadow.get_rect(), border_radius=radius)
    surface.blit(shadow, sr.topleft)

    # Fundo
    panel = _rgba((rect.w, rect.h))
    pygame.draw.rect(panel, (*style.PANEL_BG, style.PANEL_BG_ALPHA), panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, (*style.PANEL_BORDER, style.PANEL_BORDER_ALPHA), panel.get_rect(),
                     width=style.BORDER_W, border_radius=radius)
    surface.blit(panel, rect.topleft)


def draw_overlay(surface: pygame.Surface, alpha=style.OVERLAY_ALPHA):
    ov = _rgba(surface.get_size())
    ov.fill((*style.OVERLAY, alpha))
    surface.blit(ov, (0, 0))


def draw_title(surface: pygame.Surface, font, text: str, y: int, color=style.TEXT):
    s = font.render(text, True, color)
    surface.blit(s, (surface.get_width() // 2 - s.get_width() // 2, y))


def draw_subtitle(surface: pygame.Surface, font, text: str, y: int, color=style.TEXT_MUTED):
    s = font.render(text, True, color)
    surface.blit(s, (surface.get_width() // 2 - s.get_width() // 2, y))


def draw_badge(surface: pygame.Surface, rect: pygame.Rect, text: str, font,
               fg=style.TEXT, bg=style.ACCENT, radius=999):
    pill = _rgba((rect.w, rect.h))
    pygame.draw.rect(pill, (*bg, 210), pill.get_rect(), border_radius=radius)
    surface.blit(pill, rect.topleft)
    t = font.render(text, True, fg)
    surface.blit(t, (rect.centerx - t.get_width() // 2, rect.centery - t.get_height() // 2))


def draw_game_grid(surface: pygame.Surface):
    """Grade estilo matrix no campo de jogo."""
    gs = style.GRID_SIZE
    for x in range(0, LARGURA, gs):
        pygame.draw.line(surface, style.GRID_COLOR, (x, ALTURA_HUD), (x, ALTURA))
    for y in range(ALTURA_HUD, ALTURA, gs):
        pygame.draw.line(surface, style.GRID_COLOR, (0, y), (LARGURA, y))
