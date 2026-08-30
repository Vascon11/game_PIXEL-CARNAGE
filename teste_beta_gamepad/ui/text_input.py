"""
ui/text_input.py
Campo de texto com suporte a foco por teclado e clique do mouse.
"""

import pygame
from dataclasses import dataclass, field
from game import style
from ui.widgets import draw_panel


@dataclass
class TextInput:
    label: str
    value: str = ""
    placeholder: str = ""
    is_password: bool = False
    active: bool = False
    max_len: int = 64
    _last_rect: pygame.Rect = field(default_factory=lambda: pygame.Rect(0, 0, 0, 0))

    def set_rect(self, rect: pygame.Rect) -> None:
        self._last_rect = pygame.Rect(rect)

    def collidepoint(self, pos) -> bool:
        return self._last_rect.collidepoint(pos)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.collidepoint(event.pos)
            return

        if event.type != pygame.KEYDOWN or not self.active:
            return

        if event.key == pygame.K_BACKSPACE:
            self.value = self.value[:-1]
            return

        if event.key in (
            pygame.K_RETURN,
            pygame.K_KP_ENTER,
            pygame.K_TAB,
            pygame.K_UP,
            pygame.K_DOWN,
            pygame.K_ESCAPE,
        ):
            return

        ch = event.unicode
        if not ch or ord(ch) < 32:
            return

        if len(self.value) < self.max_len:
            self.value += ch

    def draw(self, surface: pygame.Surface, font_label, font_value, rect: pygame.Rect) -> None:
        self.set_rect(rect)
        draw_panel(surface, rect)

        lbl = font_label.render(self.label, True, style.TEXT_MUTED)
        surface.blit(lbl, (rect.x + style.PAD_X, rect.y + 8))

        if self.value:
            shown = ("•" * len(self.value)) if self.is_password else self.value
            val_color = style.TEXT
        else:
            shown = self.placeholder
            val_color = style.TEXT_MUTED

        val = font_value.render(shown, True, val_color)
        surface.blit(val, (rect.x + style.PAD_X, rect.y + 32))

        if self.active:
            pygame.draw.rect(surface, style.ACCENT, rect, width=2, border_radius=style.RADIUS)