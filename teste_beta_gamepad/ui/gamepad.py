"""
ui/gamepad.py
Helper centralizado para leitura do controle nas telas de UI.

Mapeamento padrão (Xbox / PS / genérico):
  D-Pad cima/baixo    (hat 0, eixo y  ±1) → navegar menus
  Analógico esq. cima/baixo (axis 1)      → navegar menus (dead-zone 0.5)
  Botão A / Cruz      (btn 0)             → confirmar / ENTER
  Botão B / Círculo   (btn 1)             → voltar / ESC
  Botão Start         (btn 7 / btn 9)     → confirmar / pause
  Gatilho / LB        (btn 4)             → boomerang (in-game)

Para texto (login / signup), o teclado continua sendo o único meio;
o controle navega entre os campos e confirma, mas não digita.
"""

import pygame

DEAD_ZONE = 0.5

# Índices de botões padrão
BTN_CONFIRM = (0, 7, 9)   # A / Cross / Start
BTN_BACK    = (1,)         # B / Circle
BTN_LEFT    = (14,)        # D-pad esquerda (alguns controles)
BTN_RIGHT   = (15,)        # D-pad direita


def _joy() -> pygame.joystick.JoystickType | None:
    if pygame.joystick.get_count() == 0:
        return None
    joy = pygame.joystick.Joystick(0)
    if not joy.get_init():
        joy.init()
    return joy


def _axis_nav(joy) -> int:
    """Retorna -1 (cima), +1 (baixo) ou 0 via analógico esquerdo."""
    if joy is None or joy.get_numaxes() < 2:
        return 0
    v = joy.get_axis(1)
    if v < -DEAD_ZONE:
        return -1
    if v > DEAD_ZONE:
        return 1
    return 0


def _hat_nav(joy) -> int:
    """Retorna -1 (cima), +1 (baixo) ou 0 via D-pad (hat 0)."""
    if joy is None or joy.get_numhats() == 0:
        return 0
    _, y = joy.get_hat(0)
    if y > 0:
        return -1   # hat y=+1 é cima
    if y < 0:
        return 1
    return 0


def _hat_lr(joy) -> int:
    """Retorna -1 (esq), +1 (dir) ou 0 via D-pad horizontal."""
    if joy is None or joy.get_numhats() == 0:
        return 0
    x, _ = joy.get_hat(0)
    return x  # -1 esq, +1 dir, 0 neutro


def is_confirm(event: pygame.event.Event) -> bool:
    """Botão de confirmação pressionado (JOYBUTTONDOWN)."""
    if event.type != pygame.JOYBUTTONDOWN:
        return False
    return event.button in BTN_CONFIRM


def is_back(event: pygame.event.Event) -> bool:
    """Botão de voltar pressionado (JOYBUTTONDOWN)."""
    if event.type != pygame.JOYBUTTONDOWN:
        return False
    return event.button in BTN_BACK


def nav_vertical(event: pygame.event.Event) -> int:
    """
    Retorna +1 (baixo), -1 (cima) ou 0 a partir de eventos de joystick.
    Trata JOYHATMOTION e JOYAXISMOTION (axis 1).
    """
    if event.type == pygame.JOYHATMOTION and event.hat == 0:
        _, y = event.value
        if y > 0: return -1
        if y < 0: return 1

    if event.type == pygame.JOYAXISMOTION and event.axis == 1:
        if event.value < -DEAD_ZONE: return -1
        if event.value >  DEAD_ZONE: return 1

    return 0


def nav_horizontal(event: pygame.event.Event) -> int:
    """
    Retorna +1 (direita), -1 (esquerda) ou 0 a partir de eventos de joystick.
    """
    if event.type == pygame.JOYHATMOTION and event.hat == 0:
        x, _ = event.value
        return x  # -1, 0, +1

    if event.type == pygame.JOYAXISMOTION and event.axis == 0:
        if event.value < -DEAD_ZONE: return -1
        if event.value >  DEAD_ZONE: return 1

    return 0
