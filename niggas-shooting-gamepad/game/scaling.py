import pygame


class Scaling:
    """
    Responsividade por RESOLUÇÃO VIRTUAL.

    Você desenha sempre em (base_w, base_h), por exemplo 800x600.
    A janela pode ser qualquer tamanho (resizable/fullscreen).
    A classe calcula:
      - scale (fator)
      - viewport (offset x/y + w/h escalados)
      - conversão de coordenadas reais -> virtuais (mouse)
    """

    def __init__(self, base_size=(800, 600)):
        self.base_w, self.base_h = base_size

        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.dst_w = self.base_w
        self.dst_h = self.base_h

    def update(self, window_size):
        win_w, win_h = window_size

        # mantém aspect ratio (letterbox)
        scale_x = win_w / self.base_w
        scale_y = win_h / self.base_h
        self.scale = min(scale_x, scale_y)

        self.dst_w = int(self.base_w * self.scale)
        self.dst_h = int(self.base_h * self.scale)

        self.offset_x = (win_w - self.dst_w) // 2
        self.offset_y = (win_h - self.dst_h) // 2

    def get_virtual_surface(self):
        """
        Retorna a surface onde você deve desenhar o jogo (sempre na resolução base).
        Você pode manter uma surface global e reutilizar; aqui deixei como helper.
        """
        return pygame.Surface((self.base_w, self.base_h)).convert_alpha()

    def present(self, window_surface: pygame.Surface, virtual_surface: pygame.Surface):
        """
        Desenha o frame virtual na janela real, escalando e centralizando.
        """
        # (opcional) limpar janela real antes
        window_surface.fill((0, 0, 0))

        scaled = pygame.transform.smoothscale(virtual_surface, (self.dst_w, self.dst_h))
        window_surface.blit(scaled, (self.offset_x, self.offset_y))

    def window_to_virtual(self, pos):
        """
        Converte coordenada do mouse (janela) para (virtual).
        Útil se você usar mouse/cliques UI futuramente.
        """
        x, y = pos
        vx = (x - self.offset_x) / self.scale
        vy = (y - self.offset_y) / self.scale
        return pygame.Vector2(vx, vy)

    def virtual_to_window(self, pos):
        """
        Converte coordenada virtual para coordenada da janela.
        Útil se precisar desenhar algo no espaço real.
        """
        x, y = pos
        wx = int(x * self.scale + self.offset_x)
        wy = int(y * self.scale + self.offset_y)
        return wx, wy

    def is_inside_viewport(self, window_pos):
        """
        Se um ponto da janela está dentro da área útil (sem as barras).
        """
        x, y = window_pos
        return (
            self.offset_x <= x <= self.offset_x + self.dst_w
            and self.offset_y <= y <= self.offset_y + self.dst_h
        )