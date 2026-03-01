import pygame
import random
import math
import os
import json

# --- Configurações Iniciais ---
pygame.init()
LARGURA, ALTURA = 800, 650
ALTURA_HUD = 60
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("PIXEL CARNAGE")
relogio = pygame.time.Clock()
fonte_grande = pygame.font.SysFont("Arial", 50, bold=True)
fonte_media = pygame.font.SysFont("Arial", 32)
fonte_pequena = pygame.font.SysFont("Arial", 18)
fonte_hud = pygame.font.SysFont("Consolas", 15, bold=True)
fonte_hud_grande = pygame.font.SysFont("Consolas", 20, bold=True)

# Música
pasta = os.path.dirname(os.path.abspath(__file__))
pygame.mixer.init()
pygame.mixer.music.load(os.path.join(pasta, "Musica_de_fundo.mp3"))
pygame.mixer.music.set_volume(0.08)

# Sprite do jogador
sprite_jogador = pygame.image.load(os.path.join(pasta, "IA_jogador.png")).convert_alpha()
som_tiro = pygame.mixer.Sound(os.path.join(pasta, "tiro.wav"))
som_tiro.set_volume(0.4)
som_escudo_quebra = pygame.mixer.Sound(os.path.join(pasta, "escudo_quebra.wav"))
som_escudo_quebra.set_volume(0.6)
som_escudo_regenerando = pygame.mixer.Sound(os.path.join(pasta, "escudo_regenerando.wav"))
som_escudo_regenerando.set_volume(0.5)
som_troca_tela = pygame.mixer.Sound(os.path.join(pasta, "troca_tela.wav"))
som_troca_tela.set_volume(0.6)
som_morte = pygame.mixer.Sound(os.path.join(pasta, "morte_teste_ainda.wav"))
som_morte.set_volume(0.7)

# Cores
FUNDO = (20, 20, 20)
MATIAS_COR = (240, 200, 180)
TIRO_COR = (100, 200, 255)
INIMIGO_COR = (150, 0, 0)
COR_VEL = (0, 255, 0)
COR_CAD = (0, 100, 255)
COR_ESPECIAL = (255, 100, 0)
COR_VIDA = (255, 50, 50)
COR_ESCUDO = (100, 200, 255)

# Cores HUD
HUD_FUNDO = (12, 12, 18)
HUD_BORDA = (40, 40, 60)
HUD_SEPARADOR = (50, 50, 75)
HUD_TEXTO = (200, 200, 220)
HUD_DESTAQUE = (255, 220, 60)



# --- HUD ---

def desenhar_barra(surf, x, y, largura, altura, valor, maximo, cor_fill, cor_fundo=(40, 40, 55)):
    pygame.draw.rect(surf, cor_fundo, (x, y, largura, altura), border_radius=3)
    if maximo > 0:
        w = int(largura * (valor / maximo))
        if w > 0:
            pygame.draw.rect(surf, cor_fill, (x, y, w, altura), border_radius=3)
    pygame.draw.rect(surf, (80, 80, 100), (x, y, largura, altura), 1, border_radius=3)




def desenhar_hud(surf, jogador, onda, inimigos_vivos, agora, record):
    # Fundo da HUD com gradiente simulado
    pygame.draw.rect(surf, HUD_FUNDO, (0, 0, LARGURA, ALTURA_HUD))
    # Linha brilhante na borda inferior
    pygame.draw.line(surf, (60, 60, 100), (0, ALTURA_HUD - 2), (LARGURA, ALTURA_HUD - 2), 1)
    pygame.draw.line(surf, (30, 30, 50), (0, ALTURA_HUD - 1), (LARGURA, ALTURA_HUD - 1), 1)

    # ===== VIDA hud (esquerda) =====
    x_vida = 10
    informacoes_hud = 8    # Y da label (linha de cima)
    icones_hud = 30   # Y do ícone/status (linha do meio)
    barra_de_progresso_hud = 46   # Y da barra (linha de baixo)

    #hud
    lbl = fonte_hud.render("VIDA", True, (180, 80, 80))
    surf.blit(lbl, (x_vida, informacoes_hud))

    #c--- espaçamento no hud ---
    for i in range(jogador.vidas_maximas):
        cx = x_vida + 9 + i * 22
        cy = icones_hud + 3   # centro vertical do coração
        if i < jogador.vidas:
            pygame.draw.circle(surf, COR_VIDA, (cx - 3, cy - 2), 5)
            pygame.draw.circle(surf, COR_VIDA, (cx + 3, cy - 2), 5)
            points = [(cx - 8, cy), (cx, cy + 8), (cx + 8, cy)]
            pygame.draw.polygon(surf, COR_VIDA, points)
        else:
            pygame.draw.circle(surf, (80, 30, 30), (cx - 3, cy - 2), 5)
            pygame.draw.circle(surf, (80, 30, 30), (cx + 3, cy - 2), 5)
            points = [(cx - 8, cy), (cx, cy + 8), (cx + 8, cy)]
            pygame.draw.polygon(surf, (80, 30, 30), points)

    # Barra de vida
    desenhar_barra(surf, x_vida, barra_de_progresso_hud, 110, 9, jogador.vidas, jogador.vidas_maximas, COR_VIDA)
    txt_v = fonte_hud.render(f"{jogador.vidas}/{jogador.vidas_maximas}", True, (220, 120, 120))
    surf.blit(txt_v, (x_vida + 115, barra_de_progresso_hud - 1))

    # Separador
    pygame.draw.line(surf, HUD_SEPARADOR, (165, 8), (165, ALTURA_HUD - 8), 1)

    # --- escudo hud (centro-esquerda) ----
    x_esc = 175

    lbl_esc = fonte_hud.render("ESCUDO", True, (60, 160, 220))
    surf.blit(lbl_esc, (x_esc, informacoes_hud))

    if jogador.escudo_ativo:
        # Ícone hexágono — alinhado com icones_hud
        cx_s = x_esc + 10
        cy_s = icones_hud + 3
        pts = []
        for ang in range(0, 360, 60):
            r = math.radians(ang + 30)
            pts.append((cx_s + int(9 * math.cos(r)), cy_s + int(9 * math.sin(r))))
        pygame.draw.polygon(surf, (30, 80, 140), pts)
        pygame.draw.polygon(surf, COR_ESCUDO, pts, 2)

        status_txt = fonte_hud_grande.render("ATIVO", True, COR_ESCUDO)
        surf.blit(status_txt, (x_esc + 24, icones_hud - 2))

        desenhar_barra(surf, x_esc, barra_de_progresso_hud, 110, 9, 1, 1, COR_ESCUDO)


    #codigo para o escudo no hud
    elif agora < jogador.recarga_escudo_em:
        tempo_rest = (jogador.recarga_escudo_em - agora) / 1000
        total = 7.0
        progresso = max(0, 1 - (tempo_rest / total))

        cx_s = x_esc + 10
        cy_s = icones_hud + 3
        pts = []
        for ang in range(0, 360, 60):
            r = math.radians(ang + 30)
            pts.append((cx_s + int(9 * math.cos(r)), cy_s + int(9 * math.sin(r))))
        pygame.draw.polygon(surf, (20, 40, 60), pts)
        pygame.draw.polygon(surf, (60, 100, 140), pts, 1)

        status_txt = fonte_hud.render(f"{tempo_rest:.1f}s", True, (100, 160, 200))
        surf.blit(status_txt, (x_esc + 24, icones_hud + 1))

        desenhar_barra(surf, x_esc, barra_de_progresso_hud, 110, 9, progresso, 1, (60, 130, 200))
    else:
        status_txt = fonte_hud.render("INATIVO", True, (100, 100, 130))
        surf.blit(status_txt, (x_esc + 5, icones_hud + 1))
        desenhar_barra(surf, x_esc, barra_de_progresso_hud, 110, 9, 0, 1, COR_ESCUDO)



    # --- espaçamento no hud ---
    pygame.draw.line(surf, HUD_SEPARADOR, (305, 8), (305, ALTURA_HUD - 8), 1)


    # ===== SEÇÃO DANO =====
    x_dano = 315


    lbl_d = fonte_hud.render("DANO", True, COR_ESPECIAL)
    surf.blit(lbl_d, (x_dano, informacoes_hud))

    dano_txt = fonte_hud_grande.render(f"x{jogador.dano}", True, (255, 180, 80))
    surf.blit(dano_txt, (x_dano, icones_hud - 4))

    #icones de balas alinhadas na barra_de_progresso_hud
    for b in range(min(jogador.dano, 5)):
        bx = x_dano + b * 12
        pygame.draw.rect(surf, (255, 150, 50), (bx, barra_de_progresso_hud, 8, 10), border_radius=2)
        pygame.draw.rect(surf, (255, 200, 100), (bx + 2, barra_de_progresso_hud, 4, 4), border_radius=1)


    # --- espaçamento no hud ---
    pygame.draw.line(surf, HUD_SEPARADOR, (390, 8), (390, ALTURA_HUD - 8), 1)


    # --- BOOMERANG hud ---
    x_boom = 400

    if jogador.tem_boomerang:
        lbl_b = fonte_hud.render("BOOM [Q]", True, (200, 200, 50))
        surf.blit(lbl_b, (x_boom, informacoes_hud))

        if agora < jogador.boomerang_ativo_ate:
            resto = (jogador.boomerang_ativo_ate - agora) / 1000
            b_txt = fonte_hud_grande.render("ATIVO!", True, (255, 255, 0))
            surf.blit(b_txt, (x_boom, icones_hud + 1))
            desenhar_barra(surf, x_boom, barra_de_progresso_hud, 110, 9, resto, 10.0, (255, 255, 0))
        elif jogador.abates_pro_boomerang >= 50:
            b_txt = fonte_hud_grande.render("PRONTO!", True, (100, 255, 100))
            surf.blit(b_txt, (x_boom, icones_hud + 1))
            desenhar_barra(surf, x_boom, barra_de_progresso_hud, 110, 9, 1, 1, (100, 255, 100))
        else:
            b_txt = fonte_hud.render(f"{jogador.abates_pro_boomerang}/50", True, (160, 160, 80))
            surf.blit(b_txt, (x_boom, icones_hud + 4))
            desenhar_barra(surf, x_boom, barra_de_progresso_hud, 110, 9, jogador.abates_pro_boomerang, 50, (200, 200, 50))

        pygame.draw.line(surf, HUD_SEPARADOR, (530, 8), (530, ALTURA_HUD - 8), 1)
        x_onda = 540
    else:
        x_onda = 400

    # --- Seçao onde hud (direita) ---
    lbl_o = fonte_hud.render("ONDA", True, HUD_DESTAQUE)
    surf.blit(lbl_o, (x_onda, informacoes_hud))

    onda_txt = fonte_hud_grande.render(str(onda), True, HUD_DESTAQUE)
    surf.blit(onda_txt, (x_onda, icones_hud + 1))

    # --- espaçamento no hud ---
    pygame.draw.line(surf, HUD_SEPARADOR, (x_onda + 50, 8), (x_onda + 50, ALTURA_HUD - 8), 1)

    # inimigos restantes
    x_ini = x_onda + 60
    lbl_i = fonte_hud.render("INIMIGOS", True, (180, 100, 100))
    surf.blit(lbl_i, (x_ini, informacoes_hud))

    ini_txt = fonte_hud_grande.render(str(inimigos_vivos), True, (255, 120, 120) if inimigos_vivos > 0 else (80, 180, 80))
    surf.blit(ini_txt, (x_ini, icones_hud + 1))

    # Record do jogador
    lbl_rec = fonte_hud.render("RECORD", True, (180, 150, 50))
    surf.blit(lbl_rec, (LARGURA - 90, informacoes_hud))
    rec_txt = fonte_hud_grande.render(str(record), True, (255, 210, 60))
    surf.blit(rec_txt, (LARGURA - 90, icones_hud - 2))

    # Indicadores de power-ups ativos (canto direito)
    px = LARGURA - 15
    py = barra_de_progresso_hud
    if jogador.tiro_oposto:
        t = fonte_hud.render("←BACK→", True, COR_ESPECIAL)
        px -= t.get_width()
        surf.blit(t, (px, py))
        px -= 8

    if jogador.tiro_triplo:
        t = fonte_hud.render("TRI", True, (150, 255, 150))
        px -= t.get_width()
        surf.blit(t, (px, py))
        px -= 8

    if jogador.ricochete > 0:
        t = fonte_hud.render("BCE", True, (255, 200, 100))
        px -= t.get_width()
        surf.blit(t, (px, py))


# --- Classes ---

class Projetil:
    def __init__(self, x, y, vel_x, vel_y, bounces=0, boomerang=False):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vel_x, vel_y)
        self.raio = 6
        self.bounces_restantes = bounces
        self.boomerang = boomerang
        self.nascimento = pygame.time.get_ticks()

    def atualizar(self, player_pos):
        agora = pygame.time.get_ticks()
        if self.boomerang and agora - self.nascimento > 400:
            direcao = (player_pos - self.pos)
            if direcao.length() > 0:
                self.vel += direcao.normalize() * 0.8
            if self.vel.length() > 15:
                self.vel = self.vel.normalize() * 15

        self.pos += self.vel

        if self.bounces_restantes > 0 and not self.boomerang:
            if self.pos.x <= 0 or self.pos.x >= LARGURA:
                self.vel.x *= -1
                self.bounces_restantes -= 1
            if self.pos.y <= ALTURA_HUD or self.pos.y >= ALTURA:
                self.vel.y *= -1
                self.bounces_restantes -= 1

    def desenhar(self, superficie):
        pygame.draw.circle(superficie, TIRO_COR, (int(self.pos.x), int(self.pos.y)), self.raio)


class Inimigo:
    def __init__(self, x, y, velocidade, vida, raio=18, tipo='NORMAL', pode_dash=False):
        self.pos = pygame.Vector2(x, y)
        self.vel_base = velocidade
        self.raio = raio
        self.vida = vida
        self.max_vida = vida
        self.tipo = tipo
        self.ultimo_spawn = pygame.time.get_ticks()
        self.pode_dash = pode_dash
        self.proximo_dash = pygame.time.get_ticks() + random.randint(1000, 3000)
        self.fim_dash = 0

    def atualizar(self, alvo_pos):
        agora = pygame.time.get_ticks()
        spawns = []
        direcao = (alvo_pos - self.pos)
        if direcao.length() > 0:
            direcao = direcao.normalize()

        velocidade_movimento = self.vel_base
        if self.pode_dash and self.tipo in ['NORMAL', 'AGIL']:
            if agora > self.proximo_dash:
                self.fim_dash = agora + 250
                self.proximo_dash = agora + random.randint(2000, 4000)
            if agora < self.fim_dash:
                velocidade_movimento = self.vel_base * 4

        self.pos += direcao * velocidade_movimento

        if self.tipo == 'BOSS' and agora - self.ultimo_spawn > 3500:
            spawns.append(Inimigo(self.pos.x, self.pos.y, 2.5, 1, 15, 'LACAIO'))
            self.ultimo_spawn = agora

        return spawns

    def desenhar(self, superficie):
        cor = INIMIGO_COR
        agora = pygame.time.get_ticks()
        if self.pode_dash and agora < self.fim_dash:
            cor = (255, 255, 255)
        elif self.tipo == 'BOSS':
            cor = (100, 0, 50)
        elif self.tipo == 'BOSS_MEDIO':
            cor = (150, 0, 50)
        elif self.tipo == 'BOSS_PEQUENO':
            cor = (200, 0, 50)
        elif self.tipo == 'LACAIO':
            cor = (100, 100, 100)
        elif self.tipo == 'AGIL':
            cor = (255, 50, 0)

        pygame.draw.circle(superficie, cor, (int(self.pos.x), int(self.pos.y)), self.raio)
        if self.raio > 20:
            pygame.draw.circle(superficie, (0, 0, 0), (int(self.pos.x), int(self.pos.y)), self.raio, 2)

        if self.raio > 12:
            txt_vida = fonte_pequena.render(str(int(self.vida)), True, (255, 255, 255))
            superficie.blit(txt_vida, (self.pos.x - txt_vida.get_width() // 2, self.pos.y - txt_vida.get_height() // 2))


class Coletavel:
    def __init__(self, x, y, tipo):
        self.pos = pygame.Vector2(x, y)
        self.tipo = tipo
        self.raio = 12
        self.nascimento = pygame.time.get_ticks()

    def desenhar(self, superficie):
        cor = COR_VEL if self.tipo == 'VEL' else COR_CAD if self.tipo == 'CAD' else COR_ESPECIAL
        if self.tipo == 'VIDA':
            cor = COR_VIDA
        elif self.tipo == 'DROP_BOOMERANG':
            cor = (255, 255, 0)

        pygame.draw.circle(superficie, cor, (int(self.pos.x), int(self.pos.y)), self.raio)
        pygame.draw.circle(superficie, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), self.raio, 2)

        letra = "H" if self.tipo == 'VIDA' else "B" if self.tipo == 'DROP_BOOMERANG' else self.tipo[0]
        txt = fonte_pequena.render(letra, True, (255, 255, 255))
        superficie.blit(txt, (self.pos.x - txt.get_width() // 2, self.pos.y - txt.get_height() // 2))


class Jogador:
    def __init__(self):
        self.pos = pygame.Vector2(LARGURA // 2, ALTURA // 2)
        self.vel_max = 4.0
        self.tamanho = 79
        self.tiros = []
        self.cadencia = 400
        self.ultimo_tiro = 0
        self.velocidade_atual = pygame.Vector2(0, 0)
        self.fator_inercia = 0.5
        self.vidas_maximas = 1
        self.vidas = 1
        self.escudo_ativo = True
        self.intangivel_ate = 0
        self.recarga_escudo_em = 0
        self.dano = 1
        self.tiro_oposto = False
        self.tiro_triplo = False
        self.ricochete = 0
        self.tiro_triplo_prob = 0.16
        self.tem_boomerang = False
        self.abates_pro_boomerang = 50
        self.boomerang_ativo_ate = 0

    def tomar_dano(self, agora):
        if agora > self.intangivel_ate:
            if self.escudo_ativo:
                self.escudo_ativo = False
                self.intangivel_ate = agora + 2000
                self.recarga_escudo_em = self.intangivel_ate + 5000
                som_escudo_quebra.play()
                return False
            else:
                self.vidas -= 1
                self.intangivel_ate = agora + 2000
                if self.vidas <= 0:
                    return True
        return False

    def atualizar_status(self, agora):
        if not self.escudo_ativo and agora > self.recarga_escudo_em:
            self.escudo_ativo = True
            som_escudo_regenerando.play()

    def controlar(self):
        teclas = pygame.key.get_pressed()
        direcao_mov = pygame.Vector2(0, 0)
        if teclas[pygame.K_a]: direcao_mov.x -= 1
        if teclas[pygame.K_d]: direcao_mov.x += 1
        if teclas[pygame.K_w]: direcao_mov.y -= 1
        if teclas[pygame.K_s]: direcao_mov.y += 1
        if direcao_mov.length() > 0: direcao_mov = direcao_mov.normalize()

        self.velocidade_atual = direcao_mov * self.vel_max
        self.pos += self.velocidade_atual
        self.pos.x = max(0, min(self.pos.x, LARGURA - self.tamanho))
        # Limita Y para não entrar na HUD
        self.pos.y = max(ALTURA_HUD + 5, min(self.pos.y, ALTURA - self.tamanho))

        agora = pygame.time.get_ticks()

        if teclas[pygame.K_q] and self.tem_boomerang and self.abates_pro_boomerang >= 50:
            self.abates_pro_boomerang = 0
            self.boomerang_ativo_ate = agora + 10000

        if agora - self.ultimo_tiro > self.cadencia:
            v_tiro = pygame.Vector2(0, 0)
            atirei = False
            if teclas[pygame.K_UP]:
                v_tiro.y = -7; atirei = True
            elif teclas[pygame.K_DOWN]:
                v_tiro.y = 7; atirei = True
            elif teclas[pygame.K_LEFT]:
                v_tiro.x = -7; atirei = True
            elif teclas[pygame.K_RIGHT]:
                v_tiro.x = 7; atirei = True
            if atirei:
                self.disparar(v_tiro, agora)
                self.ultimo_tiro = agora

    def disparar(self, v_base, agora):
        som_tiro.play()
        direcoes = [v_base]
        if self.tiro_triplo and random.random() < self.tiro_triplo_prob:
            direcoes.extend([v_base.rotate(25), v_base.rotate(-25)])
        if self.tiro_oposto:
            for d in list(direcoes): direcoes.append(d * -1)

        is_boomerang = agora < self.boomerang_ativo_ate

        for d in direcoes:
            v_final = d + (self.velocidade_atual * self.fator_inercia)
            spawn_pos = self.pos + pygame.Vector2(self.tamanho // 2, self.tamanho // 2)
            self.tiros.append(Projetil(spawn_pos.x, spawn_pos.y, v_final.x, v_final.y, self.ricochete, is_boomerang))

    def atualizar_tiros(self):
        centro_p = self.pos + pygame.Vector2(self.tamanho / 2, self.tamanho / 2)
        for t in self.tiros[:]:
            t.atualizar(centro_p)
            if t.boomerang and (t.pos - centro_p).length() < 25 and pygame.time.get_ticks() - t.nascimento > 400:
                self.tiros.remove(t)
                continue
            if not (0 <= t.pos.x <= LARGURA and ALTURA_HUD <= t.pos.y <= ALTURA) and t.bounces_restantes <= 0 and not t.boomerang:
                if t in self.tiros: self.tiros.remove(t)

    def desenhar(self, superficie):
        agora = pygame.time.get_ticks()
        for t in self.tiros: t.desenhar(superficie)

        if agora < self.intangivel_ate:
            if (agora // 100) % 2 == 0: return

        # Sprite do jogador escalado pro tamanho
        img = pygame.transform.scale(sprite_jogador, (self.tamanho, self.tamanho))
        superficie.blit(img, (self.pos.x, self.pos.y))

        if self.escudo_ativo:
            margem = 6
            pygame.draw.rect(superficie, (0, 40, 120),
                (self.pos.x - margem, self.pos.y - margem,
                 self.tamanho + margem * 2, self.tamanho + margem * 2), 3, border_radius=6)


# --- Funções do Jogo ---

def spawn_inimigo(onda):
    lado = random.choice(['T', 'B', 'L', 'R'])
    if lado == 'T':
        x, y = random.randint(0, LARGURA), ALTURA_HUD - 40
    elif lado == 'B':
        x, y = random.randint(0, LARGURA), ALTURA + 40
    elif lado == 'L':
        x, y = -40, random.randint(ALTURA_HUD, ALTURA)
    else:
        x, y = LARGURA + 40, random.randint(ALTURA_HUD, ALTURA)

    tipo = 'NORMAL'
    vida_base = 1 + (onda // 4)
    raio = 18
    vel = min(1.2 + (onda * 0.15), 3.8)
    pode_dash = onda >= 15

    if onda >= 3 and random.random() < 0.3:
        tipo = 'AGIL'
        raio = 12
        vel = min(2.5 + (onda * 0.2), 5.5)
        vida_base = max(1, vida_base - 1)

    if onda >= 7:
        if tipo == 'AGIL':
            vida_base = 10
        else:
            vida_base *= 3

    if onda >= 10:
        fator_exponencial = 1.2 ** (onda - 9)
        vida_base = int(vida_base * fator_exponencial)

    if random.random() < (0.10 if onda == 6 else 0.20 if onda >= 7 else 0):
        raio = 36
        vida_base *= 2

    return Inimigo(x, y, vel, vida_base, raio, tipo, pode_dash)


def spawn_boss(x, y, onda):
    vida = 100
    if onda >= 10:
        incrementos = (onda // 5) - 1
        vida += incrementos * 100
    return Inimigo(x, y, 0.6, vida, 60, 'BOSS', False)


def reset_jogo():
    p = Jogador()
    agora = pygame.time.get_ticks()
    t_azul = agora + random.randint(7000, 19000)
    t_verde = agora + random.randint(13000, 32000)
    t_especial = agora + 999999
    t_vida = agora + 999999
    return p, [], [], 1, agora, 5, t_azul, t_verde, t_especial, t_vida, ['BACK', 'TRI', 'BOUNCE']


def carregar_ranking():
    caminho = os.path.join(pasta, "ranking.json")
    if os.path.exists(caminho):
        with open(caminho, "r") as f:
            return json.load(f)
    return []

def salvar_ranking(ranking):
    caminho = os.path.join(pasta, "ranking.json")
    with open(caminho, "w") as f:
        json.dump(ranking, f)

def adicionar_ao_ranking(nome, onda):
    ranking = carregar_ranking()
    ranking.append({"nome": nome.upper(), "onda": onda})
    ranking = sorted(ranking, key=lambda x: x["onda"], reverse=True)[:10]  # top 10
    salvar_ranking(ranking)
    return ranking


# --- Loop Principal ---
ESTADO = "NOME"  # começa pedindo o nome
nome_jogador = ""
ranking_atual = carregar_ranking()
player, inimigos, coletaveis, onda_atual, next_spawn, spawn_restantes, p_azul, p_verde, p_especial, p_vida, itens_especiais_disp = reset_jogo()
pausa_inicio = 0
boss_spawned_this_wave = False
anuncio_boss = ""
anuncio_boss_ate = 0

NOMES_BOSS = [
    "O SLIME SUPREMO CHEGOU!",
    "DESTRUIDOR DE MUNDOS APARECEU!",
    "O BLOB ANCESTRAL DESPERTA!",
    "A MANCHA DO APOCALIPSE!",
    "O HORROR GELATINOSO AVANÇA!",
    "MESTRE DO CAOS SURGIU!",
    "O DEVORADOR DE ALMAS VEIO!",
]

while True:
    agora = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT: pygame.quit(); exit()
        if evento.type == pygame.KEYDOWN:

            # --- Tela de nome ---
            if ESTADO == "NOME":
                if evento.key == pygame.K_RETURN and len(nome_jogador) > 0:
                    ESTADO = "MENU"
                elif evento.key == pygame.K_BACKSPACE:
                    nome_jogador = nome_jogador[:-1]
                elif len(nome_jogador) < 6 and evento.unicode.isalnum():
                    nome_jogador += evento.unicode.upper()

            elif ESTADO == "TROCAR_JOGADOR":
                if evento.key == pygame.K_s:  # Sim, sou eu
                    player, inimigos, coletaveis, onda_atual, next_spawn, spawn_restantes, p_azul, p_verde, p_especial, p_vida, itens_especiais_disp = reset_jogo()
                    pygame.mixer.music.play(-1)
                    som_troca_tela.play()
                    ESTADO = "JOGANDO"
                    boss_spawned_this_wave = False
                elif evento.key == pygame.K_n:  # Não, trocar jogador
                    som_troca_tela.play()
                    nome_jogador = ""
                    ESTADO = "NOME"

            elif evento.key == pygame.K_SPACE:
                if ESTADO == "GAMEOVER":
                    som_troca_tela.play()
                    ESTADO = "TROCAR_JOGADOR"
                elif ESTADO == "MENU":
                    player, inimigos, coletaveis, onda_atual, next_spawn, spawn_restantes, p_azul, p_verde, p_especial, p_vida, itens_especiais_disp = reset_jogo()
                    pygame.mixer.music.play(-1)
                    ESTADO = "JOGANDO"
                    boss_spawned_this_wave = False

            elif evento.key == pygame.K_ESCAPE:
                if ESTADO == "JOGANDO":
                    ESTADO = "PAUSA"
                    pausa_inicio = agora
                elif ESTADO == "PAUSA":
                    ESTADO = "JOGANDO"
                    duracao_pausa = agora - pausa_inicio
                    next_spawn += duracao_pausa
                    p_azul += duracao_pausa
                    p_verde += duracao_pausa
                    p_especial += duracao_pausa
                    p_vida += duracao_pausa
                    for c in coletaveis: c.nascimento += duracao_pausa
                    if player.escudo_ativo == False:
                        player.recarga_escudo_em += duracao_pausa

    if ESTADO == "NOME":
        tela.fill(FUNDO)
        txt = fonte_grande.render("PIXEL CARNAGE", True, (255, 255, 255))
        tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, 160))

        lbl = fonte_media.render("SEU NOME (até 6 letras):", True, (180, 180, 180))
        tela.blit(lbl, (LARGURA // 2 - lbl.get_width() // 2, 260))

        # Caixinha do nome
        pygame.draw.rect(tela, (40, 40, 60), (LARGURA // 2 - 160, 300, 320, 60), border_radius=6)
        pygame.draw.rect(tela, (100, 100, 180), (LARGURA // 2 - 160, 300, 320, 60), 2, border_radius=6)
        nome_txt = fonte_grande.render(nome_jogador + ("_" if (agora // 500) % 2 == 0 else " "), True, (255, 255, 100))
        tela.blit(nome_txt, (LARGURA // 2 - nome_txt.get_width() // 2, 305))

        enter = fonte_pequena.render("ENTER para confirmar", True, (120, 120, 120))
        tela.blit(enter, (LARGURA // 2 - enter.get_width() // 2, 380))

    elif ESTADO == "MENU":
        tela.fill(FUNDO)
        txt = fonte_grande.render("PIXEL CARNAGE", True, (255, 255, 255))
        tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, 200))
        ola = fonte_media.render(f"Olá, {nome_jogador}!", True, (255, 220, 60))
        tela.blit(ola, (LARGURA // 2 - ola.get_width() // 2, 270))
        sub = fonte_pequena.render("ESPAÇO PARA INICIAR", True, (150, 150, 150))
        tela.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 330))

    elif ESTADO == "PAUSA":
        txt_pausa = fonte_grande.render("PAUSADO", True, (255, 255, 0))
        sub_pausa = fonte_media.render("ESC para continuar", True, (255, 255, 255))
        tela.blit(txt_pausa, (LARGURA // 2 - txt_pausa.get_width() // 2, 250))
        tela.blit(sub_pausa, (LARGURA // 2 - sub_pausa.get_width() // 2, 320))

    elif ESTADO == "GAMEOVER":
        tela.fill((40, 0, 0))
        txt = fonte_grande.render("PERDEU TUDO!", True, (255, 0, 0))
        txt_round = fonte_media.render(f"{nome_jogador} - Onda: {onda_atual}", True, (255, 255, 255))
        tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, 60))
        tela.blit(txt_round, (LARGURA // 2 - txt_round.get_width() // 2, 130))

        # Ranking
        rank_lbl = fonte_media.render("🏆 TOP 10", True, (255, 220, 60))
        tela.blit(rank_lbl, (LARGURA // 2 - rank_lbl.get_width() // 2, 185))

        ranking_exibir = carregar_ranking()
        for idx, entry in enumerate(ranking_exibir):
            cor = (255, 220, 60) if entry["nome"] == nome_jogador.upper() else (200, 200, 200)
            medalha = ["🥇", "🥈", "🥉"][idx] if idx < 3 else f"{idx+1}."
            linha = fonte_pequena.render(f"{medalha}  {entry['nome']}  —  Onda {entry['onda']}", True, cor)
            tela.blit(linha, (LARGURA // 2 - linha.get_width() // 2, 225 + idx * 28))

        sub = fonte_pequena.render("ESPAÇO PARA JOGAR DE NOVO", True, (150, 150, 150))
        tela.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 520))

    elif ESTADO == "TROCAR_JOGADOR":
        tela.fill(FUNDO)
        txt = fonte_media.render(f"Ainda é você, {nome_jogador}?", True, (255, 255, 255))
        tela.blit(txt, (LARGURA // 2 - txt.get_width() // 2, 240))

        sim = fonte_media.render("[S]  Sim, sou eu!", True, (100, 220, 100))
        nao = fonte_media.render("[N]  Não, trocar jogador", True, (220, 100, 100))
        tela.blit(sim, (LARGURA // 2 - sim.get_width() // 2, 310))
        tela.blit(nao, (LARGURA // 2 - nao.get_width() // 2, 360))

    elif ESTADO == "JOGANDO":
        if spawn_restantes <= 0 and len(inimigos) == 0:
            onda_atual += 1
            boss_spawned_this_wave = False
            if onda_atual == 7:
                spawn_restantes = 35
            else:
                spawn_restantes = onda_atual * 4 + 2
            next_spawn = agora + 1000

        if spawn_restantes > 0 and agora > next_spawn:
            if onda_atual % 5 == 0 and not boss_spawned_this_wave:
                inimigos.append(spawn_boss(LARGURA // 2, -50, onda_atual))
                boss_spawned_this_wave = True
                anuncio_boss = random.choice(NOMES_BOSS)
                anuncio_boss_ate = agora + 3000
            else:
                inimigos.append(spawn_inimigo(onda_atual))
                if onda_atual == 7: inimigos.append(spawn_inimigo(onda_atual))
            spawn_restantes -= 1
            next_spawn = agora + max(200, 1500 - (onda_atual * 100))

        if agora > p_azul:
            coletaveis.append(Coletavel(random.randint(50, 750), random.randint(ALTURA_HUD + 20, 580), 'CAD'))
            p_azul = agora + random.randint(7000, 19000)
        if agora > p_verde:
            coletaveis.append(Coletavel(random.randint(50, 750), random.randint(ALTURA_HUD + 20, 580), 'VEL'))
            p_verde = agora + random.randint(13000, 32000)

        if onda_atual > 5:
            if p_vida > agora + 90000: p_vida = agora + random.randint(13000, 32000)
            if agora > p_vida:
                coletaveis.append(Coletavel(random.randint(50, 750), random.randint(ALTURA_HUD + 20, 580), 'VIDA'))
                p_vida = agora + random.randint(13000, 32000)

            if p_especial > agora + 90000: p_especial = agora + random.randint(20000, 40000)
            if agora > p_especial and len(itens_especiais_disp) > 0:
                tipo = random.choice(itens_especiais_disp)
                coletaveis.append(Coletavel(random.randint(50, 750), random.randint(ALTURA_HUD + 20, 580), tipo))
                p_especial = agora + random.randint(35000, 49000)

        player.controlar()
        player.atualizar_tiros()
        player.atualizar_status(agora)
        centro_p = player.pos + pygame.Vector2(player.tamanho / 2, player.tamanho / 2)

        for c in coletaveis[:]:
            if agora - c.nascimento > 8000 and c.tipo != 'DROP_BOOMERANG':
                coletaveis.remove(c)
            elif (c.pos - centro_p).length() < c.raio + 15:
                if c.tipo == 'VEL':
                    player.vel_max += 0.4
                elif c.tipo == 'CAD':
                    player.cadencia = max(70, player.cadencia - 50)
                elif c.tipo == 'VIDA':
                    player.vidas = min(player.vidas + 1, player.vidas_maximas)
                elif c.tipo == 'DROP_BOOMERANG':
                    player.tem_boomerang = True
                    player.abates_pro_boomerang = 50
                elif c.tipo in ['BACK', 'TRI', 'BOUNCE']:
                    if c.tipo == 'BACK':
                        player.tiro_oposto = True
                    elif c.tipo == 'TRI':
                        player.tiro_triplo = True
                    elif c.tipo == 'BOUNCE':
                        player.ricochete = 2
                    itens_especiais_disp.remove(c.tipo)
                coletaveis.remove(c)

        for i in inimigos[:]:
            novos_lacaios = i.atualizar(centro_p)
            for nl in novos_lacaios: inimigos.append(nl)

            if (i.pos - centro_p).length() < i.raio + 15:
                morreu = player.tomar_dano(agora)
                if morreu:
                    ranking_atual = adicionar_ao_ranking(nome_jogador, onda_atual)
                    som_morte.play()
                    pygame.mixer.music.stop()
                    ESTADO = "GAMEOVER"

            for t in player.tiros[:]:
                if (t.pos - i.pos).length() < i.raio + t.raio:
                    i.vida -= player.dano
                    if t in player.tiros and not t.boomerang: player.tiros.remove(t)

                    if i.vida <= 0:
                        player.abates_pro_boomerang = min(50, player.abates_pro_boomerang + 1)

                        if i.tipo == 'BOSS':
                            player.dano += 1
                            player.vidas_maximas += 1
                            player.vidas += 1
                            if player.tiro_triplo_prob > 0:
                                player.tiro_triplo_prob = min(1.0, player.tiro_triplo_prob + 0.05)
                            if onda_atual >= 10 and not player.tem_boomerang:
                                coletaveis.append(Coletavel(i.pos.x, i.pos.y, 'DROP_BOOMERANG'))
                            inimigos.append(Inimigo(i.pos.x - 30, i.pos.y, 1.0, 30, 35, 'BOSS_MEDIO', onda_atual >= 15))
                            inimigos.append(Inimigo(i.pos.x + 30, i.pos.y, 1.0, 30, 35, 'BOSS_MEDIO', onda_atual >= 15))

                        elif i.tipo == 'BOSS_MEDIO':
                            inimigos.append(Inimigo(i.pos.x - 20, i.pos.y, 1.5, 15, 20, 'BOSS_PEQUENO', onda_atual >= 15))
                            inimigos.append(Inimigo(i.pos.x + 20, i.pos.y, 1.5, 15, 20, 'BOSS_PEQUENO', onda_atual >= 15))

                        if i in inimigos: inimigos.remove(i)
                        break

        # --- Desenho ---
        tela.fill(FUNDO)

        # Grade estilo matrix
        tamanho_celula = 32
        cor_grade = (0, 40, 0)
        for x in range(0, LARGURA, tamanho_celula):
            pygame.draw.line(tela, cor_grade, (x, ALTURA_HUD), (x, ALTURA))
        for y in range(ALTURA_HUD, ALTURA, tamanho_celula):
            pygame.draw.line(tela, cor_grade, (0, y), (LARGURA, y))
        for c in coletaveis: c.desenhar(tela)
        for i in inimigos: i.desenhar(tela)
        player.desenhar(tela)

        # HUD sempre por cima de tudo
        inimigos_vivos_total = spawn_restantes + len(inimigos)
        ranking = carregar_ranking()
        record_jogador = next((e["onda"] for e in ranking if e["nome"] == nome_jogador.upper()), 0)
        desenhar_hud(tela, player, onda_atual, inimigos_vivos_total, agora, record_jogador)

        # Anúncio do boss com fade out
        if agora < anuncio_boss_ate:
            tempo_restante = anuncio_boss_ate - agora
            alpha = min(255, int(255 * (tempo_restante / 1000)))  # fade nos últimos 1s

            surf_anuncio = pygame.Surface((LARGURA, 80), pygame.SRCALPHA)
            surf_anuncio.fill((80, 0, 0, max(0, alpha // 2)))
            tela.blit(surf_anuncio, (0, ALTURA // 2 - 40))

            txt_boss = fonte_media.render(anuncio_boss, True, (255, int(alpha * 0.4), int(alpha * 0.4)))
            txt_boss.set_alpha(alpha)
            tela.blit(txt_boss, (LARGURA // 2 - txt_boss.get_width() // 2, ALTURA // 2 - 16))

    pygame.display.flip()
    relogio.tick(60)