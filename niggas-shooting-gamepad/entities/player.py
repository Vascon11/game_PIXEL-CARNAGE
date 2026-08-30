"""
entities/player.py
Jogador com sistema de escudo, boomerang, skins e integração de sons
inspirados no Pixel Carnage.
"""

import pygame
import random

from game.config import (
    LARGURA, ALTURA, ALTURA_HUD,
    BOOMERANG_DURACAO, BOOMERANG_ABATES,
    ESCUDO_INTAN_MS, ESCUDO_REGEN_EXTRA_MS,
)
from game import style
from entities.projectile import Projectile
from entities.skins import PlayerSkin, PLAYER_SKINS


class Player:
    def __init__(self, skin: PlayerSkin | None = None):
        self.pos = pygame.Vector2(LARGURA // 2, ALTURA // 2)
        self.vel_max = 4.0
        self.tamanho = 35

        # Projéteis
        self.tiros: list[Projectile] = []
        self.cadencia = 400
        self.ultimo_tiro = 0
        self.velocidade_atual = pygame.Vector2(0, 0)
        self.fator_inercia = 0.5
        self.dano = 1

        # Power-ups de tiro
        self.tiro_oposto = False
        self.tiro_triplo = False
        self.tiro_triplo_prob = 0.16
        self.ricochete = 0

        # Vida e escudo (do Pixel Carnage)
        self.vidas_maximas = 1
        self.vidas = 1
        self.escudo_ativo = True
        self.intangivel_ate = 0
        self.recarga_escudo_em = 0

        # Boomerang
        self.tem_boomerang = False
        self.abates_pro_boomerang = 0
        self.boomerang_ativo_ate = 0

        # Skin
        self.skin: PlayerSkin = skin or PLAYER_SKINS[0]
        self._sprite_cache: pygame.Surface | None = None
        self._sprite_size = 0

    # ── Centro do jogador ──────────────────────────────────────────────────
    def center(self) -> pygame.Vector2:
        return self.pos + pygame.Vector2(self.tamanho / 2, self.tamanho / 2)

    # ── Atualiza regeneração do escudo ─────────────────────────────────────
    def update_status(self, now_ms: int, assets=None):
        if not self.escudo_ativo and now_ms > self.recarga_escudo_em:
            self.escudo_ativo = True
            if assets:
                assets.play(assets.som_escudo_regen)

    # ── Recebe dano ────────────────────────────────────────────────────────
    def take_damage(self, now_ms: int, assets=None) -> bool:
        """Retorna True se o jogador morreu."""
        if now_ms <= self.intangivel_ate:
            return False

        if self.escudo_ativo:
            self.escudo_ativo = False
            self.intangivel_ate = now_ms + ESCUDO_INTAN_MS
            self.recarga_escudo_em = self.intangivel_ate + ESCUDO_REGEN_EXTRA_MS
            if assets:
                assets.play(assets.som_escudo_quebra)
            return False

        self.vidas -= 1
        self.intangivel_ate = now_ms + ESCUDO_INTAN_MS
        return self.vidas <= 0

    # ── Controles ─────────────────────────────────────────────────────────
    def handle_controls(self, now_ms: int, assets=None):
        teclas = pygame.key.get_pressed()

        # Movimento via teclado
        direcao = pygame.Vector2(0, 0)
        if teclas[pygame.K_a]: direcao.x -= 1
        if teclas[pygame.K_d]: direcao.x += 1
        if teclas[pygame.K_w]: direcao.y -= 1
        if teclas[pygame.K_s]: direcao.y += 1

        # ── Suporte a controle (pygame.joystick) ──────────────────────────
        # Mapeamento padrão (Xbox / PS / genérico):
        #   Analógico esquerdo (axes 0, 1) → mover
        #   Analógico direito  (axes 2, 3) → atirar
        #   Botão 4 (LB) ou botão 0 (A/X)  → boomerang
        #
        # Eixo com dead-zone de 0.2 para evitar drift
        DEAD_ZONE = 0.2
        TIRO_VEL  = 7.0

        joy = None
        if pygame.joystick.get_count() > 0:
            joy = pygame.joystick.Joystick(0)
            if not joy.get_init():
                joy.init()

        if joy is not None:
            # Movimento analógico esquerdo
            ax = joy.get_axis(0) if joy.get_numaxes() > 0 else 0.0
            ay = joy.get_axis(1) if joy.get_numaxes() > 1 else 0.0
            if abs(ax) > DEAD_ZONE: direcao.x += ax
            if abs(ay) > DEAD_ZONE: direcao.y += ay

        if direcao.length() > 0:
            direcao = direcao.normalize()

        self.velocidade_atual = direcao * self.vel_max
        self.pos += self.velocidade_atual

        # Limita dentro do mapa (respeitando HUD)
        self.pos.x = max(0, min(self.pos.x, LARGURA - self.tamanho))
        self.pos.y = max(ALTURA_HUD + 5, min(self.pos.y, ALTURA - self.tamanho))

        # Ativar boomerang (teclado Q ou botão 4/LB do controle)
        boomerang_btn = False
        if joy is not None and joy.get_numbuttons() > 4:
            boomerang_btn = bool(joy.get_button(4))

        if (
            (teclas[pygame.K_q] or boomerang_btn)
            and self.tem_boomerang
            and self.abates_pro_boomerang >= BOOMERANG_ABATES
            and now_ms >= self.boomerang_ativo_ate
        ):
            self.abates_pro_boomerang = 0
            self.boomerang_ativo_ate = now_ms + BOOMERANG_DURACAO
            if assets:
                assets.play(assets.som_boomerang)

        # Atirar com setas (teclado) ou analógico direito (controle)
        if now_ms - self.ultimo_tiro > self.cadencia:
            v = pygame.Vector2(0, 0)
            atirei = False

            # Teclado
            if teclas[pygame.K_UP]:     v.y = -TIRO_VEL; atirei = True
            elif teclas[pygame.K_DOWN]:  v.y =  TIRO_VEL; atirei = True
            elif teclas[pygame.K_LEFT]:  v.x = -TIRO_VEL; atirei = True
            elif teclas[pygame.K_RIGHT]: v.x =  TIRO_VEL; atirei = True

            # Analógico direito do controle (axes 2, 3)
            if not atirei and joy is not None and joy.get_numaxes() > 3:
                rx = joy.get_axis(2)
                ry = joy.get_axis(3)
                if abs(rx) > DEAD_ZONE or abs(ry) > DEAD_ZONE:
                    v = pygame.Vector2(rx, ry).normalize() * TIRO_VEL
                    atirei = True

            if atirei:
                self._shoot(v, now_ms, assets)
                self.ultimo_tiro = now_ms

    def _shoot(self, v_base: pygame.Vector2, now_ms: int, assets=None):
        if assets:
            assets.play(assets.som_tiro)

        direcoes = [v_base]

        if self.tiro_triplo and random.random() < self.tiro_triplo_prob:
            direcoes.extend([v_base.rotate(25), v_base.rotate(-25)])

        if self.tiro_oposto:
            for d in list(direcoes):
                direcoes.append(d * -1)

        is_boom = now_ms < self.boomerang_ativo_ate
        spawn = self.pos + pygame.Vector2(self.tamanho // 2, self.tamanho // 2)

        for d in direcoes:
            v_final = d + (self.velocidade_atual * self.fator_inercia)
            self.tiros.append(
                Projectile(
                    spawn.x, spawn.y,
                    v_final.x, v_final.y,
                    self.ricochete,
                    boomerang=is_boom,
                    shot_color=self.skin.shot_color,
                    dano=self.dano,
                )
            )

    # ── Atualiza projéteis ─────────────────────────────────────────────────
    def update_projectiles(self):
        centro = self.center()
        for t in self.tiros[:]:
            t.update(centro if t.boomerang else None)

            # Boomerang retorna ao jogador
            if t.boomerang:
                if (t.pos - centro).length() < 25 and pygame.time.get_ticks() - t.nascimento > 400:
                    self.tiros.remove(t)
                    continue

            if t.is_outside() and t.bounces_restantes <= 0 and not t.boomerang:
                if t in self.tiros:
                    self.tiros.remove(t)

    # ── Desenho ───────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface):
        # Projéteis
        for t in self.tiros:
            t.draw(surface)

        agora = pygame.time.get_ticks()

        # Piscada de intangibilidade
        if agora < self.intangivel_ate and (agora // 100) % 2 == 0:
            return

        # Sprite ou fallback colorido
        sprite = self.skin.get_sprite(self.tamanho)
        if sprite:
            surface.blit(sprite, (int(self.pos.x), int(self.pos.y)))
        else:
            # Fallback: quadrado com cor da skin + ícone de mira
            pygame.draw.rect(surface, self.skin.color, (self.pos.x, self.pos.y, self.tamanho, self.tamanho), border_radius=4)
            cx = int(self.pos.x + self.tamanho // 2)
            cy = int(self.pos.y + self.tamanho // 2)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 5, 2)
            pygame.draw.line(surface, (255, 255, 255), (cx - 8, cy), (cx + 8, cy), 1)
            pygame.draw.line(surface, (255, 255, 255), (cx, cy - 8), (cx, cy + 8), 1)

        # Escudo visual
        if self.escudo_ativo:
            mg = 6
            pygame.draw.rect(
                surface, self.skin.shield_color,
                (self.pos.x - mg, self.pos.y - mg, self.tamanho + mg * 2, self.tamanho + mg * 2),
                3, border_radius=6,
            )

    # ── Compensação de pause ───────────────────────────────────────────────
    def compensate_pause(self, pause_ms: int):
        self.ultimo_tiro += pause_ms
        if self.intangivel_ate > 0:
            self.intangivel_ate += pause_ms
        if self.recarga_escudo_em > 0:
            self.recarga_escudo_em += pause_ms
        if self.boomerang_ativo_ate > 0:
            self.boomerang_ativo_ate += pause_ms
