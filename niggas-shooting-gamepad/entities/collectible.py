"""
entities/collectible.py
Coletáveis: velocidade, cadência, vida, power-ups especiais e boomerang.
"""

import pygame
from game import style


# Mapa tipo -> (cor, letra exibida)
_TIPO_MAP: dict[str, tuple[tuple, str]] = {
    "VEL":           (style.PICKUP_VEL,     "V"),
    "CAD":           (style.PICKUP_CAD,     "C"),
    "VIDA":          (style.PICKUP_VIDA,    "H"),
    "BACK":          (style.PICKUP_SPECIAL, "←"),
    "TRI":           (style.PICKUP_SPECIAL, "T"),
    "BOUNCE":        (style.PICKUP_SPECIAL, "B"),
    "DROP_BOOMERANG":(style.PICKUP_BOOM,    "⊙"),
    "DANO":          ((255, 80, 200),       "D"),
}


class Collectible:
    def __init__(self, x: float, y: float, tipo: str):
        self.pos = pygame.Vector2(x, y)
        self.tipo = tipo
        self.raio = 12
        self.nascimento = pygame.time.get_ticks()

    def draw(self, surface: pygame.Surface, fonte_pequena):
        cor, letra = _TIPO_MAP.get(self.tipo, (style.PICKUP_SPECIAL, "?"))

        # Pulso de brilho baseado no tempo
        agora = pygame.time.get_ticks()
        pulso = abs((agora % 800) - 400) / 400  # 0..1
        r_ext = self.raio + int(pulso * 3)

        pygame.draw.circle(surface, (cor[0]//3, cor[1]//3, cor[2]//3), (int(self.pos.x), int(self.pos.y)), r_ext)
        pygame.draw.circle(surface, cor,              (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(surface, (255, 255, 255),  (int(self.pos.x), int(self.pos.y)), self.raio, 2)

        txt = fonte_pequena.render(letra, True, (255, 255, 255))
        surface.blit(txt, (self.pos.x - txt.get_width() // 2, self.pos.y - txt.get_height() // 2))
