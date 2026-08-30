"""
diagnostico_controle.py
────────────────────────────────────────────────────────────────────────
Execute este script ANTES de abrir o jogo para verificar se o pygame
consegue detectar seu controle no Linux.

    python diagnostico_controle.py

O script abre uma janela pequena e fica escutando eventos por 30 segundos.
Pressione qualquer botão ou mova os analógicos — tudo aparecerá no terminal.
"""

import os, sys
if sys.platform.startswith("linux"):
    os.environ.setdefault("SDL_JOYSTICK_LINUX_EVDEV", "1")
import pygame
import sys

pygame.init()
pygame.joystick.init()

screen = pygame.display.set_mode((500, 200))
pygame.display.set_caption("Diagnóstico de Controle — feche para sair")
font = pygame.font.SysFont("monospace", 16)
clock = pygame.time.Clock()

print("=" * 60)
print("DIAGNÓSTICO DE CONTROLE")
print("=" * 60)

# Detecta joysticks já conectados
count = pygame.joystick.get_count()
joysticks = {}

if count == 0:
    print("⚠  Nenhum controle detectado pelo pygame.")
    print("   Verifique:")
    print("   1. ls /dev/input/js*   (deve existir js0 ou js1)")
    print("   2. sudo dnf install python3-pygame  (versão do sistema)")
    print("   3. Tente: SDL_JOYSTICK_DEVICE=/dev/input/js0 python diagnostico_controle.py")
else:
    for i in range(count):
        joy = pygame.joystick.Joystick(i)
        joy.init()
        joysticks[joy.get_instance_id()] = joy
        print(f"✓  Controle {i}: {joy.get_name()}")
        print(f"   axes={joy.get_numaxes()}  buttons={joy.get_numbuttons()}  hats={joy.get_numhats()}")

print("-" * 60)
print("Mexa no controle — os eventos aparecerão abaixo.")
print("Feche a janela ou Ctrl+C para sair.")
print("-" * 60)

running = True
while running:
    screen.fill((20, 20, 30))

    line1 = font.render("Mexa no controle — veja o terminal", True, (180, 180, 180))
    line2 = font.render(f"Controles detectados: {len(joysticks)}", True, (100, 220, 255))
    screen.blit(line1, (20, 60))
    screen.blit(line2, (20, 100))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            joy.init()
            joysticks[joy.get_instance_id()] = joy
            print(f"[HOT-PLUG] Conectado: {joy.get_name()}  axes={joy.get_numaxes()}  buttons={joy.get_numbuttons()}")

        elif event.type == pygame.JOYDEVICEREMOVED:
            print(f"[HOT-PLUG] Desconectado instance_id={event.instance_id}")
            joysticks.pop(event.instance_id, None)

        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"  BOTÃO PRESSIONADO  → button={event.button}  joy={event.instance_id}")

        elif event.type == pygame.JOYBUTTONUP:
            print(f"  botão solto        → button={event.button}")

        elif event.type == pygame.JOYAXISMOTION:
            if abs(event.value) > 0.15:  # filtra drift
                print(f"  EIXO               → axis={event.axis}  value={event.value:+.3f}")

        elif event.type == pygame.JOYHATMOTION:
            print(f"  D-PAD (hat)        → hat={event.hat}  value={event.value}")

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    clock.tick(60)

pygame.quit()
print("Diagnóstico encerrado.")
