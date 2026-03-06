"""
game/app.py
Ponto de entrada: cria janela, instancia state machine e roda o loop.

Melhorias:
- suporte a fullscreen com F11
- remapeamento do mouse da janela real -> resolução virtual
- correção de clique/hover deslocado ao redimensionar ou usar tela cheia
- suporte a controle (joystick) com hot-plug no Linux/Windows/Mac
"""

import pygame

from game.config import LARGURA, ALTURA, FPS, WINDOW_TITLE
from game.assets import Assets
from game.state_machine import StateMachine
from game.scaling import Scaling
from ui.screens import MenuState


def _remap_mouse_event(event: pygame.event.Event, scaling: Scaling) -> pygame.event.Event:
    if not hasattr(event, "pos"):
        return event

    if scaling.scale <= 0:
        return event

    if not scaling.is_inside_viewport(event.pos):
        data = dict(event.dict)
        data["pos"] = (-99999, -99999)
        if "rel" in data:
            data["rel"] = (0, 0)
        return pygame.event.Event(event.type, data)

    vx, vy = scaling.window_to_virtual(event.pos)
    vx = int(round(vx))
    vy = int(round(vy))

    data = dict(event.dict)
    data["pos"] = (vx, vy)

    if "rel" in data:
        rx, ry = data["rel"]
        data["rel"] = (
            int(round(rx / scaling.scale)),
            int(round(ry / scaling.scale)),
        )

    return pygame.event.Event(event.type, data)


def _init_all_joysticks():
    """Inicializa todos os joysticks já conectados e imprime diagnóstico."""
    count = pygame.joystick.get_count()
    if count == 0:
        print("[Gamepad] Nenhum controle detectado na inicialização.")
        return
    for i in range(count):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        print(
            f"[Gamepad] Controle {i}: {joy.get_name()} "
            f"| axes={joy.get_numaxes()} buttons={joy.get_numbuttons()} hats={joy.get_numhats()}"
        )


def run():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    pygame.joystick.init()

    # Inicializa controles já conectados (necessário no Linux antes de receber eventos)
    _init_all_joysticks()

    windowed_size = (LARGURA, ALTURA)
    fullscreen = False

    window = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    assets = Assets()

    scaling = Scaling(base_size=(LARGURA, ALTURA))
    scaling.update(window.get_size())

    virtual = pygame.Surface((LARGURA, ALTURA)).convert_alpha()

    sm = StateMachine(MenuState(virtual, assets, None))
    sm.state.sm = sm

    while True:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            # Hot-plug: controle conectado/desconectado durante o jogo
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joy.init()
                print(
                    f"[Gamepad] Conectado: {joy.get_name()} "
                    f"| axes={joy.get_numaxes()} buttons={joy.get_numbuttons()} hats={joy.get_numhats()}"
                )
                continue

            if event.type == pygame.JOYDEVICEREMOVED:
                print(f"[Gamepad] Desconectado (instance_id={event.instance_id})")
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                if fullscreen:
                    fullscreen = False
                    window = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
                else:
                    fullscreen = True
                    windowed_size = window.get_size()
                    window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

                scaling.update(window.get_size())
                continue

            if event.type == pygame.VIDEORESIZE and not fullscreen:
                windowed_size = event.size
                window = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                scaling.update(event.size)
                continue

            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                event = _remap_mouse_event(event, scaling)

            sm.handle_event(event)

        sm.update(now)
        sm.draw(virtual)

        scaling.present(window, virtual)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    run()
