import pygame


class Anchor:
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"

    MID_LEFT = "mid_left"
    CENTER = "center"
    MID_RIGHT = "mid_right"

    BOT_LEFT = "bot_left"
    BOT_CENTER = "bot_center"
    BOT_RIGHT = "bot_right"


def anchored_rect(container: pygame.Rect, size, anchor=Anchor.TOP_LEFT, padding=(0, 0)):
    w, h = size
    px, py = padding
    r = pygame.Rect(0, 0, w, h)

    if anchor == Anchor.TOP_LEFT:
        r.topleft = (container.left + px, container.top + py)

    elif anchor == Anchor.TOP_CENTER:
        r.midtop = (container.centerx, container.top + py)
        r.x += px

    elif anchor == Anchor.TOP_RIGHT:
        r.topright = (container.right - px, container.top + py)

    elif anchor == Anchor.MID_LEFT:
        r.midleft = (container.left + px, container.centery)
        r.y += py

    elif anchor == Anchor.CENTER:
        r.center = container.center
        r.x += px
        r.y += py

    elif anchor == Anchor.MID_RIGHT:
        r.midright = (container.right - px, container.centery)
        r.y += py

    elif anchor == Anchor.BOT_LEFT:
        r.bottomleft = (container.left + px, container.bottom - py)

    elif anchor == Anchor.BOT_CENTER:
        r.midbottom = (container.centerx, container.bottom - py)
        r.x += px

    elif anchor == Anchor.BOT_RIGHT:
        r.bottomright = (container.right - px, container.bottom - py)

    return r


def stack_vertical(start_rect: pygame.Rect, item_h: int, gap: int, count: int):
    rects = []
    x = start_rect.x
    w = start_rect.w
    y = start_rect.y

    for _ in range(count):
        rects.append(pygame.Rect(x, y, w, item_h))
        y += item_h + gap

    return rects


def inset(rect: pygame.Rect, pad_x: int, pad_y: int) -> pygame.Rect:
    """Retorna um rect com padding interno."""
    return pygame.Rect(rect.x + pad_x, rect.y + pad_y, rect.w - pad_x * 2, rect.h - pad_y * 2)


def pct_rect(container: pygame.Rect, x_pct: float, y_pct: float, w_pct: float, h_pct: float) -> pygame.Rect:
    """
    Retorna rect por porcentagem dentro do container:
    x_pct=0.1 significa 10% da largura do container.
    """
    x = container.x + int(container.w * x_pct)
    y = container.y + int(container.h * y_pct)
    w = int(container.w * w_pct)
    h = int(container.h * h_pct)
    return pygame.Rect(x, y, w, h)


def clamp_size(value: int, min_v: int, max_v: int) -> int:
    return max(min_v, min(value, max_v))