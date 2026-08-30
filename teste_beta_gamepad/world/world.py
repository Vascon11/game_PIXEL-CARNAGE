"""
world/world.py
Lógica central do jogo: ondas, spawns, coletáveis, colisões, bosses e tempo da run.
"""

import random
import pygame

from game.config import (
    SPAWN_X_MIN,
    SPAWN_X_MAX,
    SPAWN_Y_MIN,
    SPAWN_Y_MAX,
    BOOMERANG_ABATES,
)
from entities.player import Player
from entities.collectible import Collectible
from entities.skins import PlayerSkin
from entities.boss import TIPO_TITAN, TIPO_SENTINELA
from world.spawners import (
    spawn_enemy,
    spawn_boss,
    spawn_boss_medio,
    spawn_boss_medio_r,
    spawn_boss_pequeno,
    spawn_boss_pequeno_r,
    random_boss_name,
)


def _rand_pos():
    return (
        random.randint(SPAWN_X_MIN, SPAWN_X_MAX),
        random.randint(SPAWN_Y_MIN, SPAWN_Y_MAX),
    )


class BossAnnouncement:
    def __init__(self):
        self.text = ""
        self.show_until = 0

    def trigger(self, text: str, duration_ms: int = 3000):
        self.text = text
        self.show_until = pygame.time.get_ticks() + duration_ms

    def is_active(self, now_ms: int) -> bool:
        return now_ms < self.show_until

    def alpha(self, now_ms: int) -> int:
        remaining = self.show_until - now_ms
        return max(0, min(255, int(255 * (remaining / 1000))))


class World:
    def __init__(self, skin: PlayerSkin | None = None, assets=None):
        self.assets = assets
        self._skin = skin
        self.reset()

    def reset(self):
        self.player = Player(skin=self._skin)
        self.enemies = []
        self.collectibles = []

        self.wave = 1
        now = pygame.time.get_ticks()
        self.started_at_ms = now

        self.spawn_restantes = self._calc_spawn_count(1)
        self.boss_spawned = False
        self.boss_announcement = BossAnnouncement()

        self.next_spawn = now + 1000

        self.next_blue = now + random.randint(7000, 19000)
        self.next_green = now + random.randint(13000, 32000)
        self.next_special = now + 999_999
        self.next_vida = now + 999_999

        self.especiais_disp = ["BACK", "TRI", "BOUNCE"]

    def _calc_spawn_count(self, wave: int) -> int:
        if wave == 7:
            return 35
        return wave * 4 + 2

    def elapsed_ms(self, now_ms: int | None = None) -> int:
        if now_ms is None:
            now_ms = pygame.time.get_ticks()
        return max(0, int(now_ms - self.started_at_ms))

    def compensate_pause(self, pause_ms: int):
        self.started_at_ms += pause_ms
        self.next_spawn += pause_ms
        self.next_blue += pause_ms
        self.next_green += pause_ms
        self.next_special += pause_ms
        self.next_vida += pause_ms
        self.boss_announcement.show_until += pause_ms

        self.player.compensate_pause(pause_ms)
        for c in self.collectibles:
            c.nascimento += pause_ms
        for e in self.enemies:
            e.compensate_pause(pause_ms)

    def enemies_alive(self) -> int:
        return self.spawn_restantes + len(self.enemies)

    def update(self, now_ms: int) -> str | None:
        if self.spawn_restantes <= 0 and len(self.enemies) == 0:
            self.wave += 1
            self.boss_spawned = False
            self.spawn_restantes = self._calc_spawn_count(self.wave)
            self.next_spawn = now_ms + 1000

            if self.wave > 5:
                if self.next_special > now_ms + 90_000:
                    self.next_special = now_ms + random.randint(20_000, 40_000)
                if self.next_vida > now_ms + 90_000:
                    self.next_vida = now_ms + random.randint(13_000, 32_000)

        if self.spawn_restantes > 0 and now_ms > self.next_spawn:
            if self.wave % 5 == 0 and not self.boss_spawned:
                boss = spawn_boss(self.wave)
                self.enemies.append(boss)
                self.boss_spawned = True
                self.boss_announcement.trigger(random_boss_name())
                if self.assets:
                    self.assets.play(self.assets.som_boss)
            else:
                self.enemies.append(spawn_enemy(self.wave))
                if self.wave == 7:
                    self.enemies.append(spawn_enemy(self.wave))

            self.spawn_restantes -= 1
            self.next_spawn = now_ms + max(200, 1500 - (self.wave * 100))

        self._spawn_collectibles(now_ms)

        self.player.handle_controls(now_ms, self.assets)
        self.player.update_projectiles()
        self.player.update_status(now_ms, self.assets)
        center_p = self.player.center()

        self._process_collectibles(now_ms, center_p)

        result = self._process_enemies(now_ms, center_p)
        if result == "GAMEOVER":
            if self.assets:
                self.assets.play(self.assets.som_morte)
                self.assets.stop_music()
            return "GAMEOVER"

        return None

    def _spawn_collectibles(self, now_ms: int):
        if now_ms > self.next_blue:
            self.collectibles.append(Collectible(*_rand_pos(), "CAD"))
            self.next_blue = now_ms + random.randint(7_000, 19_000)

        if now_ms > self.next_green:
            self.collectibles.append(Collectible(*_rand_pos(), "VEL"))
            self.next_green = now_ms + random.randint(13_000, 32_000)

        if self.wave > 5:
            if now_ms > self.next_vida:
                self.collectibles.append(Collectible(*_rand_pos(), "VIDA"))
                self.next_vida = now_ms + random.randint(13_000, 32_000)

            if now_ms > self.next_special and self.especiais_disp:
                tipo = random.choice(self.especiais_disp)
                self.collectibles.append(Collectible(*_rand_pos(), tipo))
                self.next_special = now_ms + random.randint(35_000, 49_000)

    def _process_collectibles(self, now_ms: int, center_p: pygame.Vector2):
        for c in self.collectibles[:]:
            if c.tipo != "DROP_BOOMERANG" and now_ms - c.nascimento > 8_000:
                self.collectibles.remove(c)
                continue

            if (c.pos - center_p).length() < c.raio + 15:
                p = self.player

                if c.tipo == "VEL":
                    p.vel_max = min(p.vel_max + 0.4, 9.0)
                elif c.tipo == "CAD":
                    p.cadencia = max(70, p.cadencia - 50)
                elif c.tipo == "VIDA":
                    p.vidas = min(p.vidas + 1, p.vidas_maximas)
                elif c.tipo == "DROP_BOOMERANG":
                    p.tem_boomerang = True
                    p.abates_pro_boomerang = BOOMERANG_ABATES
                elif c.tipo == "BACK":
                    p.tiro_oposto = True
                    if "BACK" in self.especiais_disp:
                        self.especiais_disp.remove("BACK")
                elif c.tipo == "TRI":
                    p.tiro_triplo = True
                    if "TRI" in self.especiais_disp:
                        self.especiais_disp.remove("TRI")
                elif c.tipo == "BOUNCE":
                    p.ricochete = 2
                    if "BOUNCE" in self.especiais_disp:
                        self.especiais_disp.remove("BOUNCE")
                elif c.tipo == "DANO":
                    p.dano += 1

                if self.assets:
                    self.assets.play(self.assets.som_powerup)
                self.collectibles.remove(c)

    def _process_enemies(self, now_ms: int, center_p: pygame.Vector2) -> str | None:
        p = self.player

        for e in self.enemies[:]:
            novos = e.update(center_p)
            for n in novos:
                self.enemies.append(n)

            if (e.pos - center_p).length() < e.raio + 15:
                morreu = p.take_damage(now_ms, self.assets)
                if morreu:
                    return "GAMEOVER"

            for t in p.tiros[:]:
                if (t.pos - e.pos).length() < e.raio + t.raio:
                    e.vida -= t.dano
                    if not t.boomerang and t in p.tiros:
                        p.tiros.remove(t)

                    if e.vida <= 0:
                        self._on_enemy_killed(e)
                        if e in self.enemies:
                            self.enemies.remove(e)
                        break

        return None

    def _on_enemy_killed(self, e):
        p = self.player
        p.abates_pro_boomerang = min(BOOMERANG_ABATES, p.abates_pro_boomerang + 1)

        if e.tipo == TIPO_TITAN:
            p.dano += 1
            p.vidas_maximas += 1
            p.vidas += 1
            p.tiro_triplo_prob = min(1.0, p.tiro_triplo_prob + 0.05)

            if self.wave >= 10 and not p.tem_boomerang:
                self.collectibles.append(Collectible(e.pos.x, e.pos.y, "DROP_BOOMERANG"))

            self.enemies.append(spawn_boss_medio(e.pos.x, e.pos.y))
            self.enemies.append(spawn_boss_medio_r(e.pos.x, e.pos.y))

        elif e.tipo == TIPO_SENTINELA:
            self.enemies.append(spawn_boss_pequeno(e.pos.x, e.pos.y))
            self.enemies.append(spawn_boss_pequeno_r(e.pos.x, e.pos.y))