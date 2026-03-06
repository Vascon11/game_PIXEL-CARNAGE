"""
ui/hud.py
HUD visual no estilo Pixel Carnage: barras, ícones, seções separadas.
Desenhado na faixa superior (ALTURA_HUD px).
"""

import math
import pygame

from game import style
from game.config import LARGURA, ALTURA_HUD, BOOMERANG_ABATES
from services.session import get_session


def _draw_bar(surf, x, y, w, h, valor, maximo, cor_fill, cor_bg=(40, 40, 55)):
    pygame.draw.rect(surf, cor_bg, (x, y, w, h), border_radius=3)
    if maximo > 0:
        fill = int(w * max(0, valor / maximo))
        if fill > 0:
            pygame.draw.rect(surf, cor_fill, (x, y, fill, h), border_radius=3)
    pygame.draw.rect(surf, (80, 80, 100), (x, y, w, h), 1, border_radius=3)


def _sep(surf, x):
    pygame.draw.line(surf, style.HUD_SEP, (x, 8), (x, ALTURA_HUD - 8), 1)


def draw_hud(surface: pygame.Surface, assets, world, now_ms: int):
    """
    Desenha a HUD completa do jogo.
    Parâmetros:
        surface  : surface de desenho
        assets   : objeto Assets (fontes e sons)
        world    : objeto World (player, wave, enemies_alive)
        now_ms   : tempo atual em ms
    """
    player = world.player
    fh  = assets.fonte_hud
    fhg = assets.fonte_hud_g

    # ── Fundo da HUD ─────────────────────────────────────────────────────
    pygame.draw.rect(surface, style.HUD_BG, (0, 0, LARGURA, ALTURA_HUD))
    pygame.draw.line(surface, (60, 60, 100), (0, ALTURA_HUD - 2), (LARGURA, ALTURA_HUD - 2), 1)
    pygame.draw.line(surface, (30, 30, 50),  (0, ALTURA_HUD - 1), (LARGURA, ALTURA_HUD - 1), 1)

    ROW_LBL = 8    # Y da label
    ROW_ICO = 30   # Y do ícone / valor
    ROW_BAR = 50   # Y da barra

    cursor_x = 10  # posição horizontal atual

    # ══════════════════════════════════════════
    # SEÇÃO: VIDA
    # ══════════════════════════════════════════
    lbl = fh.render("VIDA", True, (180, 80, 80))
    surface.blit(lbl, (cursor_x, ROW_LBL))

    for i in range(player.vidas_maximas):
        cx = cursor_x + 9 + i * 22
        cy = ROW_ICO + 3
        cor_heart = style.HUD_VIDA if i < player.vidas else (80, 30, 30)
        pygame.draw.circle(surface, cor_heart, (cx - 3, cy - 2), 5)
        pygame.draw.circle(surface, cor_heart, (cx + 3, cy - 2), 5)
        pygame.draw.polygon(surface, cor_heart, [(cx - 8, cy), (cx, cy + 8), (cx + 8, cy)])

    _draw_bar(surface, cursor_x, ROW_BAR, 110, 9,
              player.vidas, player.vidas_maximas, style.HUD_VIDA)

    txt_v = fh.render(f"{player.vidas}/{player.vidas_maximas}", True, (220, 120, 120))
    surface.blit(txt_v, (cursor_x + 115, ROW_BAR - 1))

    cursor_x += 165
    _sep(surface, cursor_x)
    cursor_x += 10

    # ══════════════════════════════════════════
    # SEÇÃO: ESCUDO
    # ══════════════════════════════════════════
    lbl_esc = fh.render("ESCUDO", True, (60, 160, 220))
    surface.blit(lbl_esc, (cursor_x, ROW_LBL))

    def _hexagon(cx_s, cy_s, r, cor, borda=None):
        pts = []
        for ang in range(0, 360, 60):
            rad = math.radians(ang + 30)
            pts.append((cx_s + int(r * math.cos(rad)), cy_s + int(r * math.sin(rad))))
        pygame.draw.polygon(surface, cor, pts)
        if borda:
            pygame.draw.polygon(surface, borda, pts, 2)

    hex_cx = cursor_x + 10
    hex_cy = ROW_ICO + 3

    if player.escudo_ativo:
        _hexagon(hex_cx, hex_cy, 9, (30, 80, 140), style.HUD_ESCUDO)
        surface.blit(fhg.render("ATIVO", True, style.HUD_ESCUDO), (cursor_x + 24, ROW_ICO - 2))
        _draw_bar(surface, cursor_x, ROW_BAR, 110, 9, 1, 1, style.HUD_ESCUDO)

    elif now_ms < player.recarga_escudo_em:
        tempo_rest = (player.recarga_escudo_em - now_ms) / 1000
        progresso = max(0, 1 - (tempo_rest / 7.0))
        _hexagon(hex_cx, hex_cy, 9, (20, 40, 60), (60, 100, 140))
        surface.blit(fh.render(f"{tempo_rest:.1f}s", True, (100, 160, 200)), (cursor_x + 24, ROW_ICO + 1))
        _draw_bar(surface, cursor_x, ROW_BAR, 110, 9, progresso, 1, (60, 130, 200))

    else:
        surface.blit(fh.render("INATIVO", True, (100, 100, 130)), (cursor_x + 5, ROW_ICO + 1))
        _draw_bar(surface, cursor_x, ROW_BAR, 110, 9, 0, 1, style.HUD_ESCUDO)

    cursor_x += 140
    _sep(surface, cursor_x)
    cursor_x += 10

    # ══════════════════════════════════════════
    # SEÇÃO: DANO
    # ══════════════════════════════════════════
    lbl_d = fh.render("DANO", True, style.HUD_DANO)
    surface.blit(lbl_d, (cursor_x, ROW_LBL))

    surface.blit(fhg.render(f"x{player.dano}", True, (255, 180, 80)), (cursor_x, ROW_ICO - 4))

    for b in range(min(player.dano, 6)):
        bx = cursor_x + b * 12
        pygame.draw.rect(surface, (255, 150, 50), (bx, ROW_BAR, 8, 10), border_radius=2)
        pygame.draw.rect(surface, (255, 200, 100), (bx + 2, ROW_BAR, 4, 4), border_radius=1)

    cursor_x += 85
    _sep(surface, cursor_x)
    cursor_x += 10

    # ══════════════════════════════════════════
    # SEÇÃO: BOOMERANG (se desbloqueado)
    # ══════════════════════════════════════════
    if player.tem_boomerang:
        lbl_b = fh.render("BOOM [Q]", True, style.HUD_BOOM)
        surface.blit(lbl_b, (cursor_x, ROW_LBL))

        if now_ms < player.boomerang_ativo_ate:
            resto = (player.boomerang_ativo_ate - now_ms) / 1000
            surface.blit(fhg.render("ATIVO!", True, (255, 255, 0)), (cursor_x, ROW_ICO + 1))
            _draw_bar(surface, cursor_x, ROW_BAR, 110, 9, resto, 10.0, (255, 255, 0))
        elif player.abates_pro_boomerang >= BOOMERANG_ABATES:
            surface.blit(fhg.render("PRONTO!", True, (100, 255, 100)), (cursor_x, ROW_ICO + 1))
            _draw_bar(surface, cursor_x, ROW_BAR, 110, 9, 1, 1, (100, 255, 100))
        else:
            surface.blit(
                fh.render(f"{player.abates_pro_boomerang}/{BOOMERANG_ABATES}", True, (160, 160, 80)),
                (cursor_x, ROW_ICO + 4),
            )
            _draw_bar(surface, cursor_x, ROW_BAR, 110, 9,
                      player.abates_pro_boomerang, BOOMERANG_ABATES, style.HUD_BOOM)

        cursor_x += 130
        _sep(surface, cursor_x)
        cursor_x += 10

    # ══════════════════════════════════════════
    # SEÇÃO CENTRAL: ONDA + INIMIGOS
    # ══════════════════════════════════════════
    x_onda = cursor_x

    surface.blit(fh.render("ONDA", True, style.HUD_HIGHLIGHT), (x_onda, ROW_LBL))
    surface.blit(fhg.render(str(world.wave), True, style.HUD_HIGHLIGHT), (x_onda, ROW_ICO + 1))

    x_ini = x_onda + 55
    _sep(surface, x_ini - 5)

    n_vivos = world.enemies_alive()
    surface.blit(fh.render("INIMIGOS", True, (180, 100, 100)), (x_ini, ROW_LBL))
    cor_ini = (255, 120, 120) if n_vivos > 0 else (80, 180, 80)
    surface.blit(fhg.render(str(n_vivos), True, cor_ini), (x_ini, ROW_ICO + 1))

    # ══════════════════════════════════════════
    # DIREITA: RECORD + power-ups ativos
    # ══════════════════════════════════════════
    sess = get_session()
    record = sess.best_wave if sess else 0

    surface.blit(fh.render("RECORD", True, (180, 150, 50)), (LARGURA - 100, ROW_LBL))
    surface.blit(fhg.render(str(record), True, (255, 210, 60)), (LARGURA - 100, ROW_ICO - 2))

    # Indicadores de power-ups
    px = LARGURA - 15
    py = ROW_BAR

    if player.tiro_oposto:
        t = fh.render("←BACK→", True, style.HUD_DANO)
        px -= t.get_width()
        surface.blit(t, (px, py))
        px -= 8

    if player.tiro_triplo:
        t = fh.render("TRI", True, (150, 255, 150))
        px -= t.get_width()
        surface.blit(t, (px, py))
        px -= 8

    if player.ricochete > 0:
        t = fh.render("BCE", True, (255, 200, 100))
        px -= t.get_width()
        surface.blit(t, (px, py))


def draw_boss_announcement(surface: pygame.Surface, assets, announcement, now_ms: int):
    """Renderiza o banner de anúncio de boss com fade-out."""
    if not announcement.is_active(now_ms):
        return

    alpha = announcement.alpha(now_ms)
    h = surface.get_height()
    w = surface.get_width()

    banner = pygame.Surface((w, 80), pygame.SRCALPHA)
    banner.fill((80, 0, 0, max(0, alpha // 2)))
    surface.blit(banner, (0, h // 2 - 40))

    txt = assets.fonte_media.render(announcement.text, True, (255, int(alpha * 0.4), int(alpha * 0.4)))
    txt.set_alpha(alpha)
    surface.blit(txt, (w // 2 - txt.get_width() // 2, h // 2 - 16))
