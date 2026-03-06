"""
ui/skin_select.py
Tela de seleção de skin do jogador com teclado, mouse e controle.
ESC / botão B cancela e volta ao menu.
"""

import pygame

from game import style
from game.state_machine import State
from entities.skins import PLAYER_SKINS, next_skin, prev_skin
from ui.widgets import draw_panel, draw_title, draw_subtitle
from ui.button import Button
from ui import gamepad as gp


class SkinSelectState(State):
    def __init__(self, surface, assets, sm, selected_skin, on_confirm, on_cancel):
        self.surface = surface
        self.assets = assets
        self.sm = sm
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.selected = selected_skin if selected_skin is not None else PLAYER_SKINS[0]
        self._mouse_pos = (-99999, -99999)
        self.buttons = []

    def enter(self, **kwargs):
        self._mouse_pos = (-99999, -99999)
        self.buttons = [
            Button("Anterior", self._prev_rect, self._go_prev, enabled=True),
            Button("Confirmar", self._confirm_rect, self._confirm, enabled=True),
            Button("Próxima", self._next_rect, self._go_next, enabled=True),
            Button("Voltar", self._back_rect, self._cancel, enabled=True),
        ]

    def _panel_rect(self, surface: pygame.Surface) -> pygame.Rect:
        screen = surface.get_rect()
        w = min(max(int(screen.w * 0.68), 520), 760)
        h = min(max(int(screen.h * 0.70), 380), 520)
        return pygame.Rect(screen.centerx - w // 2, screen.centery - h // 2, w, h)

    def _preview_rect(self, surface: pygame.Surface) -> pygame.Rect:
        panel = self._panel_rect(surface)
        size = min(max(int(panel.h * 0.24), 90), 120)
        return pygame.Rect(panel.centerx - size // 2, panel.y + 120, size, size)

    def _button_row_y(self, surface: pygame.Surface) -> int:
        panel = self._panel_rect(surface)
        return panel.bottom - 95

    def _prev_rect(self, surface: pygame.Surface) -> pygame.Rect:
        panel = self._panel_rect(surface)
        y = self._button_row_y(surface)
        return pygame.Rect(panel.x + 35, y, 150, 46)

    def _confirm_rect(self, surface: pygame.Surface) -> pygame.Rect:
        panel = self._panel_rect(surface)
        y = self._button_row_y(surface)
        return pygame.Rect(panel.centerx - 85, y, 170, 46)

    def _next_rect(self, surface: pygame.Surface) -> pygame.Rect:
        panel = self._panel_rect(surface)
        y = self._button_row_y(surface)
        return pygame.Rect(panel.right - 185, y, 150, 46)

    def _back_rect(self, surface: pygame.Surface) -> pygame.Rect:
        panel = self._panel_rect(surface)
        return pygame.Rect(panel.centerx - 85, panel.bottom - 42, 170, 34)

    def _go_prev(self):
        self.selected = prev_skin(self.selected)

    def _go_next(self):
        self.selected = next_skin(self.selected)

    def _confirm(self):
        self.on_confirm(self.selected)

    def _cancel(self):
        self.on_cancel()

    def handle_event(self, event):
        if hasattr(event, "pos"):
            self._mouse_pos = event.pos

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self._go_next()
                return
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._go_prev()
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._confirm()
                return
            if event.key == pygame.K_ESCAPE:
                self._cancel()
                return

        # Controle: D-Pad / analógico esquerdo para trocar skin
        lr = gp.nav_horizontal(event)
        if lr > 0:
            self._go_next()
            return
        if lr < 0:
            self._go_prev()
            return

        # Analógico vertical não faz nada aqui, mas D-Pad vertical
        # mapeia para prev/next também (confortável em alguns controles)
        ud = gp.nav_vertical(event)
        if ud > 0:
            self._go_next()
            return
        if ud < 0:
            self._go_prev()
            return

        if gp.is_confirm(event):
            self._confirm()
            return
        if gp.is_back(event):
            self._cancel()
            return

        for b in self.buttons:
            b.handle_event(event, self.surface, self._mouse_pos)

    def draw(self, surface: pygame.Surface):
        surface.fill(style.BG)

        panel = self._panel_rect(surface)
        draw_panel(surface, panel)

        draw_title(surface, self.assets.fonte_grande, "ESCOLHA SUA SKIN", panel.y + 18, style.HUD_HIGHLIGHT)
        draw_subtitle(
            surface,
            self.assets.fonte_pequena,
            "← / → mudar   |   ENTER confirmar   |   ESC voltar   |   🎮 D-Pad ←→ + A/B",
            panel.y + 72,
            style.TEXT_MUTED,
        )

        preview = self._preview_rect(surface)
        sprite = self.selected.get_sprite(preview.w)
        if sprite:
            surface.blit(sprite, preview.topleft)
        else:
            pygame.draw.rect(surface, self.selected.color, preview, border_radius=8)

        mg = 8
        pygame.draw.rect(
            surface,
            self.selected.shield_color,
            (preview.x - mg, preview.y - mg, preview.w + mg * 2, preview.h + mg * 2),
            3,
            border_radius=10,
        )

        idx = PLAYER_SKINS.index(self.selected)
        name_txt = self.assets.fonte_media.render(
            f"{self.selected.name} ({idx + 1}/{len(PLAYER_SKINS)})",
            True,
            style.TEXT,
        )
        surface.blit(name_txt, (panel.centerx - name_txt.get_width() // 2, preview.bottom + 22))

        shot_label = self.assets.fonte_pequena.render("Cor do tiro", True, style.TEXT_MUTED)
        label_x = panel.centerx - 72
        label_y = preview.bottom + 58
        surface.blit(shot_label, (label_x, label_y))

        ball_x = label_x + shot_label.get_width() + 18
        ball_y = label_y + shot_label.get_height() // 2 + 1
        pygame.draw.circle(surface, self.selected.shot_color, (ball_x, ball_y), 8)

        for b in self.buttons:
            b.draw(surface, self.assets.fonte_pequena, self._mouse_pos, focused=False)
