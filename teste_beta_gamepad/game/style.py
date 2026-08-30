"""
game/style.py
Tokens visuais (cores, espaçamentos) no estilo do Pixel Carnage.
"""

# ── Fundo ──────────────────────────────────────────────────
BG            = (18, 18, 22)
GRID_COLOR    = (0, 40, 0)
GRID_SIZE     = 32

# ── Texto ──────────────────────────────────────────────────
TEXT          = (200, 200, 220)
TEXT_MUTED    = (140, 140, 160)

# ── Entidades ──────────────────────────────────────────────
PLAYER_COLOR  = (240, 200, 180)
SHOT          = (100, 200, 255)     # tiro normal
SHOT_BOOM     = (255, 255, 80)      # tiro boomerang
ENEMY_NORMAL  = (150,   0,   0)
ENEMY_AGIL    = (255,  50,   0)
ENEMY_LACAIO  = (100, 100, 100)
BOSS_MAIN     = (100,   0,  50)
BOSS_MEDIO    = (150,   0,  50)
BOSS_PEQUENO  = (200,   0,  50)

# ── Power-ups / coletáveis ─────────────────────────────────
PICKUP_VEL      = (0,   255,  0)
PICKUP_CAD      = (0,   100, 255)
PICKUP_SPECIAL  = (255, 130,  0)
PICKUP_VIDA     = (255,  50, 50)
PICKUP_BOOM     = (255, 255,  0)

# ── Acente / destaque ──────────────────────────────────────
ACCENT        = (100, 200, 255)
ACCENT_2      = (0,   255,   0)
DANGER        = (255,  70,  70)

# ── Escudo ─────────────────────────────────────────────────
SHIELD_COLOR  = (100, 200, 255)
SHIELD_BG     = (0,   40, 120)

# ── HUD ────────────────────────────────────────────────────
HUD_BG        = (12,  12,  18)
HUD_BORDER    = (40,  40,  60)
HUD_SEP       = (50,  50,  75)
HUD_TEXT      = (200, 200, 220)
HUD_HIGHLIGHT = (255, 220,  60)
HUD_VIDA      = (255,  50,  50)
HUD_ESCUDO    = (100, 200, 255)
HUD_DANO      = (255, 100,   0)
HUD_BOOM      = (200, 200,  50)

# ── Painéis UI ─────────────────────────────────────────────
PANEL_BG           = (30,  30,  38)
PANEL_BG_ALPHA     = 170
PANEL_BORDER       = (80,  80,  95)
PANEL_BORDER_ALPHA = 160
PANEL_SHADOW       = (0,   0,   0)
PANEL_SHADOW_ALPHA = 80

# ── Botões ─────────────────────────────────────────────────
BTN_BG       = (42, 42, 54)
BTN_BG_HOVER = (52, 52, 68)
BTN_BORDER   = (90, 90, 110)

# ── Overlay (pause/gameover) ───────────────────────────────
OVERLAY       = (0,  0, 0)
OVERLAY_ALPHA = 120

# ── Espaçamentos / dimensões ───────────────────────────────
PAD_X     = 12
PAD_Y     = 10
GAP       = 8
RADIUS    = 12
BORDER_W  = 2
SHADOW_OFF = (0, 6)

HUD_X     = 0
HUD_Y     = 0
HUD_WIDTH  = 320
HUD_HEIGHT = 66