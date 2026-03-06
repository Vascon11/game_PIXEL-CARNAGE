"""
game/assets.py
Carrega e centraliza todos os assets (fontes, sons, sprites).
Sons do Pixel Carnage integrados; fallback silencioso se arquivo ausente.
"""

import os
import pygame


def _load_sound(path: str, volume: float = 0.5) -> pygame.mixer.Sound | None:
    """Carrega som com fallback silencioso."""
    if not os.path.exists(path):
        return None
    try:
        s = pygame.mixer.Sound(path)
        s.set_volume(volume)
        return s
    except Exception:
        return None


def _make_silent() -> pygame.mixer.Sound:
    """Cria um Sound vazio (silencioso) para evitar None checks."""
    buf = bytearray(44)  # header WAV mínimo
    return pygame.mixer.Sound(buffer=bytes(buf))


SOUNDS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


class Assets:
    def __init__(self):
        # ── Fontes ─────────────────────────────────────────
        self.fonte_grande  = pygame.font.SysFont("Consolas", 50, bold=True)
        self.fonte_media   = pygame.font.SysFont("Consolas", 32)
        self.fonte_pequena = pygame.font.SysFont("Consolas", 18)
        self.fonte_hud     = pygame.font.SysFont("Consolas", 15, bold=True)
        self.fonte_hud_g   = pygame.font.SysFont("Consolas", 20, bold=True)

        # ── Sons ────────────────────────────────────────────
        pygame.mixer.init()

        self.som_tiro             = _load_sound(os.path.join(SOUNDS_DIR, "tiro.wav"),              0.4)
        self.som_escudo_quebra    = _load_sound(os.path.join(SOUNDS_DIR, "escudo_quebra.wav"),     0.6)
        self.som_escudo_regen     = _load_sound(os.path.join(SOUNDS_DIR, "escudo_regenerando.wav"), 0.5)
        self.som_troca_tela       = _load_sound(os.path.join(SOUNDS_DIR, "troca_tela.wav"),        0.6)
        self.som_morte            = _load_sound(os.path.join(SOUNDS_DIR, "morte_teste_ainda.wav"), 0.7)
        self.som_boss             = _load_sound(os.path.join(SOUNDS_DIR, "boss_spawn.wav"),        0.7)
        self.som_powerup          = _load_sound(os.path.join(SOUNDS_DIR, "powerup.wav"),           0.5)
        self.som_boomerang        = _load_sound(os.path.join(SOUNDS_DIR, "boomerang.wav"),         0.5)

    def play(self, sound: pygame.mixer.Sound | None):
        """Toca um som se ele existir."""
        if sound:
            sound.play()

    def stop_music(self):
        pygame.mixer.music.stop()

    def play_music(self, loops: int = -1):
        music_path = os.path.join(SOUNDS_DIR, "Musica_de_fundo.mp3")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.08)
                pygame.mixer.music.play(loops)
            except Exception:
                pass
