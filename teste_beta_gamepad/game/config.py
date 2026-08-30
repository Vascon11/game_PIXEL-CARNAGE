"""
game/config.py
Configurações centralizadas do jogo.
"""

LARGURA = 1200
ALTURA = 700
ALTURA_HUD = 70          # altura da faixa HUD no topo
FPS = 60

WINDOW_TITLE = "Arena Shooting - Elite Edition"

# Mapa de gameplay começa abaixo da HUD
PLAY_Y_MIN = ALTURA_HUD
PLAY_Y_MAX = ALTURA

# Spawn de coletáveis na área de jogo
SPAWN_X_MIN = 60
SPAWN_X_MAX = LARGURA - 60
SPAWN_Y_MIN = PLAY_Y_MIN + 20
SPAWN_Y_MAX = PLAY_Y_MAX - 40

# Duração do boomerang (ms)
BOOMERANG_DURACAO = 10_000
BOOMERANG_ABATES = 50

# Escudo
ESCUDO_INTAN_MS = 2_000
ESCUDO_REGEN_EXTRA_MS = 5_000

# Boss
BOSS_LACAIO_INTERVALO = 3_500
