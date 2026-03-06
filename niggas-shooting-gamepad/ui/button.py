"""
ui/button.py
Botão com suporte a hover de mouse E foco de teclado.
"""

import pygame
from dataclasses import dataclass
from typing import Callable

from game import style
from ui.widgets import draw_panel


RectGetter = Callable[[pygame.Surface], pygame.Rect]


@dataclass
class Button:
    text: str
    get_rect: RectGetter
    on_click: Callable[[], None]
    enabled: bool = True

    def rect(self, surface: pygame.Surface) -> pygame.Rect:
        return self.get_rect(surface)

    def handle_event(self, event: pygame.event.Event, surface: pygame.Surface, mouse_pos) -> None:
        if not self.enabled:
            return
        r = self.rect(surface)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if r.collidepoint(mouse_pos):
                self.on_click()

    def draw(
        self,
        surface: pygame.Surface,
        font,
        mouse_pos,
        focused: bool = False,
    ) -> None:
        r = self.rect(surface)
        mouse_hover = self.enabled and r.collidepoint(mouse_pos)
        highlighted = (mouse_hover or focused) and self.enabled

        draw_panel(surface, r, radius=style.RADIUS)

        if highlighted:
            hl = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            hl.fill((*style.ACCENT, 28))
            surface.blit(hl, r.topleft)
            pygame.draw.rect(surface, style.ACCENT, r, width=2, border_radius=style.RADIUS)
            cx = r.left - 14
            cy = r.centery
            pygame.draw.polygon(surface, style.ACCENT, [
                (cx,     cy - 7),
                (cx,     cy + 7),
                (cx + 9, cy),
            ])

        if not self.enabled:
            dim = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 130))
            surface.blit(dim, r.topleft)

        txt_color = style.TEXT if self.enabled else style.TEXT_MUTED
        txt = font.render(self.text, True, txt_color)
        surface.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))
