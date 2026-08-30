import pygame

from game.state_machine import State
from game import style

from world.world import World
from ui.hud import draw_hud, draw_boss_announcement
from ui.widgets import draw_panel, draw_overlay, draw_title, draw_subtitle, draw_game_grid
from ui.text_input import TextInput
from ui.button import Button
from ui.layout import inset, stack_vertical, clamp_size
from ui.skin_select import SkinSelectState
from ui import gamepad as gp

from services.auth_service import sign_in, sign_up, sign_out
from services.leaderboard_service import (
    get_top10,
    submit_score,
    get_my_best,
    format_time_ms,
)
from services.session import set_session, clear_session, get_session, set_best_wave, is_logged_in
from entities.skins import PLAYER_SKINS


def menu_panel_rect(surface: pygame.Surface) -> pygame.Rect:
    screen = surface.get_rect()
    w = clamp_size(int(screen.w * 0.80), 520, 900)
    h = clamp_size(int(screen.h * 0.72), 360, 590)
    return pygame.Rect(screen.centerx - w // 2, int(screen.h * 0.16), w, h)


def menu_buttons_rects(surface: pygame.Surface) -> list[pygame.Rect]:
    panel = menu_panel_rect(surface)
    pad_x = clamp_size(int(panel.w * 0.06), 24, 56)
    pad_top = clamp_size(int(panel.h * 0.31), 120, 185)
    pad_bot = clamp_size(int(panel.h * 0.16), 60, 100)
    inner = inset(panel, pad_x, 0)
    area = pygame.Rect(inner.x, panel.y + pad_top, inner.w, panel.h - pad_top - pad_bot)
    gap = clamp_size(int(area.h * 0.06), 10, 18)
    btn_h = clamp_size(int((area.h - gap * 4) / 5), 42, 60)
    return stack_vertical(pygame.Rect(area.x, area.y, area.w, btn_h), btn_h, gap, 5)


def hint_y(surface: pygame.Surface) -> int:
    panel = menu_panel_rect(surface)
    return panel.bottom - clamp_size(int(panel.h * 0.10), 34, 48)


def auth_panel_rect(surface: pygame.Surface, tall: bool = False) -> pygame.Rect:
    base = menu_panel_rect(surface)
    if tall:
        return pygame.Rect(base.x, base.y - 8, base.w, clamp_size(int(base.h * 1.02), 420, 580))
    return pygame.Rect(base.x, base.y, base.w, clamp_size(int(base.h * 0.90), 360, 520))


class ConfirmDialog:
    def __init__(self, message: str):
        self.message = message
        self._choice = 0

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_UP):
                self._choice = 1 - self._choice
            elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                self._choice = 1 - self._choice
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return "yes" if self._choice == 1 else "no"
            elif event.key == pygame.K_ESCAPE:
                return "no"

        # Controle
        lr = gp.nav_horizontal(event)
        if lr != 0:
            self._choice = 1 - self._choice
        if gp.is_confirm(event):
            return "yes" if self._choice == 1 else "no"
        if gp.is_back(event):
            return "no"

        return None

    def draw(self, surface: pygame.Surface, assets):
        ov = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        surface.blit(ov, (0, 0))

        screen = surface.get_rect()
        w = clamp_size(int(screen.w * 0.46), 340, 520)
        h = clamp_size(int(screen.h * 0.26), 160, 220)
        rect = pygame.Rect(screen.centerx - w // 2, screen.centery - h // 2, w, h)
        draw_panel(surface, rect)

        msg = assets.fonte_media.render(self.message, True, style.TEXT)
        surface.blit(msg, (rect.centerx - msg.get_width() // 2, rect.y + 22))

        btn_w = clamp_size(int(w * 0.36), 110, 160)
        btn_h = clamp_size(int(h * 0.30), 44, 58)
        gap = clamp_size(int(w * 0.08), 18, 36)
        total = btn_w * 2 + gap
        bx = rect.centerx - total // 2
        by = rect.bottom - btn_h - 22

        labels = ["Não", "Sim"]
        colors = [(180, 80, 80), (80, 200, 120)]

        for i, (lbl, cor) in enumerate(zip(labels, colors)):
            r = pygame.Rect(bx + i * (btn_w + gap), by, btn_w, btn_h)
            focused = (self._choice == i)

            bg_surf = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            bg_surf.fill((*cor, 60) if focused else (*style.PANEL_BG, style.PANEL_BG_ALPHA))
            surface.blit(bg_surf, r.topleft)

            pygame.draw.rect(surface, cor if focused else style.PANEL_BORDER, r, width=2, border_radius=style.RADIUS)
            txt = assets.fonte_media.render(lbl, True, cor if focused else style.TEXT_MUTED)
            surface.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))

        dica = assets.fonte_pequena.render(
            "←→ escolher   |   ENTER confirmar   |   ESC cancelar",
            True,
            style.TEXT_MUTED,
        )
        surface.blit(dica, (rect.centerx - dica.get_width() // 2, rect.bottom + 8))


class MenuState(State):
    def __init__(self, surface, assets, sm):
        self.surface = surface
        self.assets = assets
        self.sm = sm
        self.msg = ""
        self.buttons = []
        self._focused = 0
        self._mouse_pos = (-99999, -99999)
        self.selected_skin = PLAYER_SKINS[0]

    def enter(self, **kwargs):
        self.msg = kwargs.get("msg", "")
        self._focused = 0
        self._mouse_pos = (-99999, -99999)
        self.selected_skin = kwargs.get("selected_skin", getattr(self, "selected_skin", PLAYER_SKINS[0]))

        sess = get_session()
        if sess:
            try:
                set_best_wave(get_my_best(sess.user_id))
            except Exception:
                pass

        def go_login():
            self.sm.change(LoginState(self.surface, self.assets, self.sm, selected_skin=self.selected_skin))

        def go_signup():
            self.sm.change(SignupState(self.surface, self.assets, self.sm, selected_skin=self.selected_skin))

        def go_play():
            if not is_logged_in():
                self.msg = "Você precisa logar para jogar."
                return
            world = World(skin=self.selected_skin, assets=self.assets)
            self.assets.play_music()
            self.sm.change(
                PlayingState(
                    self.surface,
                    self.assets,
                    self.sm,
                    world,
                    selected_skin=self.selected_skin,
                )
            )

        def go_select_skin():
            if not is_logged_in():
                self.msg = "Você precisa logar para jogar."
                return

            def on_skin(skin):
                self.sm.change(
                    MenuState(self.surface, self.assets, self.sm),
                    msg=f"Skin selecionada: {skin.name}",
                    selected_skin=skin,
                )

            def on_cancel():
                self.sm.change(
                    MenuState(self.surface, self.assets, self.sm),
                    selected_skin=self.selected_skin,
                )

            self.sm.change(
                SkinSelectState(
                    self.surface,
                    self.assets,
                    self.sm,
                    self.selected_skin,
                    on_skin,
                    on_cancel,
                )
            )

        def do_logout():
            try:
                sign_out()
            except Exception:
                pass
            clear_session()
            self.sm.change(
                MenuState(self.surface, self.assets, self.sm),
                msg="Saiu da conta.",
                selected_skin=self.selected_skin,
            )

        rects = [lambda s, i=i: menu_buttons_rects(s)[i] for i in range(5)]
        self.buttons = [
            Button("Login", rects[0], go_login, enabled=True),
            Button("Cadastro", rects[1], go_signup, enabled=True),
            Button("Jogar", rects[2], go_play, enabled=is_logged_in()),
            Button("Selecionar Skin", rects[3], go_select_skin, enabled=is_logged_in()),
            Button("Logout", rects[4], do_logout, enabled=is_logged_in()),
        ]

    def _move_focus(self, delta: int):
        n = len(self.buttons)
        for _ in range(n):
            self._focused = (self._focused + delta) % n
            if self.buttons[self._focused].enabled:
                break

    def handle_event(self, event):
        if hasattr(event, "pos"):
            self._mouse_pos = event.pos

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self._move_focus(+1)
                return
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move_focus(-1)
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                btn = self.buttons[self._focused]
                if btn.enabled:
                    btn.on_click()
                return

        # Controle
        nav = gp.nav_vertical(event)
        if nav != 0:
            self._move_focus(nav)
            return
        if gp.is_confirm(event):
            btn = self.buttons[self._focused]
            if btn.enabled:
                btn.on_click()
            return
        if gp.is_back(event):
            pygame.quit()
            raise SystemExit

        for b in self.buttons:
            b.handle_event(event, self.surface, mouse_pos=self._mouse_pos)

        if event.type == pygame.MOUSEMOTION:
            for i, b in enumerate(self.buttons):
                if b.enabled and b.rect(self.surface).collidepoint(self._mouse_pos):
                    self._focused = i

    def draw(self, surface: pygame.Surface):
        surface.fill(style.BG)

        panel = menu_panel_rect(surface)
        draw_panel(surface, panel)

        draw_title(surface, self.assets.fonte_grande, "OVERCLOCK ARENA", panel.y + 18, style.TEXT)

        sess = get_session()
        info = f"Logado: {sess.username}  |  Record: {sess.best_wave}" if sess else "Não logado"
        draw_subtitle(surface, self.assets.fonte_pequena, info, panel.y + 80, style.TEXT_MUTED)

        skin_info = f"Skin atual: {self.selected_skin.name}"
        draw_subtitle(surface, self.assets.fonte_pequena, skin_info, panel.y + 108, style.TEXT_MUTED)

        self.buttons[2].enabled = is_logged_in()
        self.buttons[3].enabled = is_logged_in()
        self.buttons[4].enabled = is_logged_in()

        if not self.buttons[self._focused].enabled:
            self._move_focus(1)

        for i, b in enumerate(self.buttons):
            b.draw(surface, self.assets.fonte_media, mouse_pos=self._mouse_pos, focused=(i == self._focused))

        hint = "↑↓ navegar   |   ENTER selecionar   |   F11 tela cheia   |   ESC sair   |   🎮 D-Pad + A"
        ht = self.assets.fonte_pequena.render(hint, True, style.TEXT_MUTED)
        surface.blit(ht, (surface.get_width() // 2 - ht.get_width() // 2, hint_y(surface)))

        if self.msg:
            w = self.assets.fonte_pequena.render(self.msg, True, style.DANGER)
            surface.blit(w, (surface.get_width() // 2 - w.get_width() // 2, panel.bottom + 10))


class LoginState(State):
    def __init__(self, surface, assets, sm, selected_skin=None):
        self.surface = surface
        self.assets = assets
        self.sm = sm
        self.selected_skin = selected_skin if selected_skin is not None else PLAYER_SKINS[0]
        self.email = TextInput("Email", placeholder="email@exemplo.com", max_len=80)
        self.password = TextInput("Senha", placeholder="••••••••", is_password=True, max_len=80)
        self._focus = 0
        self.msg = ""
        self._mouse_pos = (-99999, -99999)

    def _input_rects(self, surface: pygame.Surface):
        panel = auth_panel_rect(surface, tall=False)
        inner = inset(panel, clamp_size(int(panel.w * 0.06), 24, 56), 0)
        box_w = inner.w
        box_h = clamp_size(int(panel.h * 0.18), 70, 90)
        r1 = pygame.Rect(inner.x, panel.y + clamp_size(int(panel.h * 0.28), 110, 150), box_w, box_h)
        r2 = pygame.Rect(inner.x, r1.bottom + 18, box_w, box_h)
        return panel, r1, r2

    def _login_button_rect(self, surface: pygame.Surface) -> pygame.Rect:
        panel, _, r2 = self._input_rects(surface)
        return pygame.Rect(panel.centerx - 90, r2.bottom + 22, 180, 44)

    def _back_button_rect(self, surface: pygame.Surface) -> pygame.Rect:
        panel = auth_panel_rect(surface, tall=False)
        return pygame.Rect(panel.centerx - 70, panel.bottom - 44, 140, 30)

    def _update_active(self):
        self.email.active = (self._focus == 0)
        self.password.active = (self._focus == 1)

    def _move_focus(self, delta: int):
        self._focus = (self._focus + delta) % 2
        self._update_active()

    def enter(self, **kwargs):
        self._mouse_pos = (-99999, -99999)
        self._update_active()

    def handle_event(self, event):
        if hasattr(event, "pos"):
            self._mouse_pos = event.pos

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.sm.change(MenuState(self.surface, self.assets, self.sm), selected_skin=self.selected_skin)
                return
            if event.key in (pygame.K_DOWN, pygame.K_TAB):
                self._move_focus(+1)
                return
            if event.key == pygame.K_UP:
                self._move_focus(-1)
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._do_login()
                return

        # Controle: navega campos e confirma (não digita texto)
        nav = gp.nav_vertical(event)
        if nav != 0:
            self._move_focus(nav)
            return
        if gp.is_confirm(event):
            self._do_login()
            return
        if gp.is_back(event):
            self.sm.change(MenuState(self.surface, self.assets, self.sm), selected_skin=self.selected_skin)
            return

        _, r1, r2 = self._input_rects(self.surface)
        self.email.set_rect(r1)
        self.password.set_rect(r2)

        self.email.handle_event(event)
        self.password.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.email.collidepoint(event.pos):
                self._focus = 0
                self._update_active()
                return
            if self.password.collidepoint(event.pos):
                self._focus = 1
                self._update_active()
                return
            if self._login_button_rect(self.surface).collidepoint(event.pos):
                self._do_login()
                return
            if self._back_button_rect(self.surface).collidepoint(event.pos):
                self.sm.change(MenuState(self.surface, self.assets, self.sm), selected_skin=self.selected_skin)
                return

    def _do_login(self):
        self.msg = ""
        try:
            u = sign_in(self.email.value.strip(), self.password.value)
            set_session(u.user_id, u.email, u.username)
            try:
                set_best_wave(get_my_best(u.user_id))
            except Exception:
                set_best_wave(0)
            self.sm.change(
                MenuState(self.surface, self.assets, self.sm),
                msg="Login OK.",
                selected_skin=self.selected_skin,
            )
        except Exception as e:
            self.msg = f"Falha no login: {e}"

    def draw(self, surface: pygame.Surface):
        surface.fill(style.BG)
        panel, r1, r2 = self._input_rects(surface)
        draw_panel(surface, panel)

        draw_title(surface, self.assets.fonte_grande, "LOGIN", panel.y + 18, style.TEXT)
        draw_subtitle(
            surface,
            self.assets.fonte_pequena,
            "↑↓/TAB alterna campo   |   ENTER confirma   |   ESC volta   |   🎮 D-Pad + A/B",
            panel.y + 80,
            style.TEXT_MUTED,
        )

        self.email.draw(surface, self.assets.fonte_pequena, self.assets.fonte_media, r1)
        self.password.draw(surface, self.assets.fonte_pequena, self.assets.fonte_media, r2)

        login_btn = Button("Entrar", self._login_button_rect, self._do_login, enabled=True)
        back_btn = Button(
            "Voltar",
            self._back_button_rect,
            lambda: self.sm.change(MenuState(self.surface, self.assets, self.sm), selected_skin=self.selected_skin),
            enabled=True,
        )

        login_btn.draw(surface, self.assets.fonte_pequena, self._mouse_pos, focused=False)
        back_btn.draw(surface, self.assets.fonte_pequena, self._mouse_pos, focused=False)

        if self.msg:
            m = self.assets.fonte_pequena.render(self.msg, True, style.DANGER)
            surface.blit(m, (surface.get_width() // 2 - m.get_width() // 2, panel.bottom - 72))


class SignupState(State):
    def __init__(self, surface, assets, sm, selected_skin=None):
        self.surface = surface
        self.assets = assets
        self.sm = sm
        self.selected_skin = selected_skin if selected_skin is not None else PLAYER_SKINS[0]
        self.username = TextInput("Username", placeholder="Seu nome no ranking", max_len=18)
        self.email = TextInput("Email", placeholder="email@exemplo.com", max_len=80)
        self.password = TextInput("Senha", placeholder="••••••••", is_password=True, max_len=80)
        self._focus = 0
        self.msg = ""
        self._mouse_pos = (-99999, -99999)

    def _input_rects(self, surface: pygame.Surface):
        panel = auth_panel_rect(surface, tall=True)
        inner = inset(panel, clamp_size(int(panel.w * 0.06), 24, 56), 0)
        box_w = inner.w
        box_h = clamp_size(int(panel.h * 0.15), 70, 90)
        y0 = panel.y + clamp_size(int(panel.h * 0.24), 110, 150)
        r0 = pygame.Rect(inner.x, y0, box_w, box_h)
        r1 = pygame.Rect(inner.x, r0.bottom + 16, box_w, box_h)
        r2 = pygame.Rect(inner.x, r1.bottom + 16, box_w, box_h)
        return panel, r0, r1, r2

    def _signup_button_rect(self, surface: pygame.Surface) -> pygame.Rect:
        panel, _, _, r2 = self._input_rects(surface)
        return pygame.Rect(panel.centerx - 90, r2.bottom + 18, 180, 44)

    def _back_button_rect(self, surface: pygame.Surface) -> pygame.Rect:
        panel = auth_panel_rect(surface, tall=True)
        return pygame.Rect(panel.centerx - 70, panel.bottom - 44, 140, 30)

    def _update_active(self):
        self.username.active = (self._focus == 0)
        self.email.active = (self._focus == 1)
        self.password.active = (self._focus == 2)

    def _move_focus(self, delta: int):
        self._focus = (self._focus + delta) % 3
        self._update_active()

    def enter(self, **kwargs):
        self._mouse_pos = (-99999, -99999)
        self._update_active()

    def handle_event(self, event):
        if hasattr(event, "pos"):
            self._mouse_pos = event.pos

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.sm.change(MenuState(self.surface, self.assets, self.sm), selected_skin=self.selected_skin)
                return
            if event.key in (pygame.K_DOWN, pygame.K_TAB):
                self._move_focus(+1)
                return
            if event.key == pygame.K_UP:
                self._move_focus(-1)
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._do_signup()
                return

        # Controle: navega campos e confirma
        nav = gp.nav_vertical(event)
        if nav != 0:
            self._move_focus(nav)
            return
        if gp.is_confirm(event):
            self._do_signup()
            return
        if gp.is_back(event):
            self.sm.change(MenuState(self.surface, self.assets, self.sm), selected_skin=self.selected_skin)
            return

        _, r0, r1, r2 = self._input_rects(self.surface)
        self.username.set_rect(r0)
        self.email.set_rect(r1)
        self.password.set_rect(r2)

        self.username.handle_event(event)
        self.email.handle_event(event)
        self.password.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.username.collidepoint(event.pos):
                self._focus = 0
                self._update_active()
                return
            if self.email.collidepoint(event.pos):
                self._focus = 1
                self._update_active()
                return
            if self.password.collidepoint(event.pos):
                self._focus = 2
                self._update_active()
                return
            if self._signup_button_rect(self.surface).collidepoint(event.pos):
                self._do_signup()
                return
            if self._back_button_rect(self.surface).collidepoint(event.pos):
                self.sm.change(MenuState(self.surface, self.assets, self.sm), selected_skin=self.selected_skin)
                return

    def _do_signup(self):
        self.msg = ""
        try:
            uname = self.username.value.strip()
            if not uname:
                self.msg = "Username é obrigatório."
                return
            u = sign_up(self.email.value.strip(), self.password.value, uname)
            set_session(u.user_id, u.email, u.username)
            try:
                set_best_wave(get_my_best(u.user_id))
            except Exception:
                set_best_wave(0)
            self.sm.change(
                MenuState(self.surface, self.assets, self.sm),
                msg="Cadastro OK. Você já está logado.",
                selected_skin=self.selected_skin,
            )
        except Exception as e:
            self.msg = f"Falha no cadastro: {e}"

    def draw(self, surface: pygame.Surface):
        surface.fill(style.BG)
        panel, r0, r1, r2 = self._input_rects(surface)
        draw_panel(surface, panel)

        draw_title(surface, self.assets.fonte_grande, "CADASTRO", panel.y + 14, style.TEXT)
        draw_subtitle(
            surface,
            self.assets.fonte_pequena,
            "↑↓/TAB alterna campo   |   ENTER confirma   |   ESC volta   |   🎮 D-Pad + A/B",
            panel.y + 78,
            style.TEXT_MUTED,
        )

        self.username.draw(surface, self.assets.fonte_pequena, self.assets.fonte_media, r0)
        self.email.draw(surface, self.assets.fonte_pequena, self.assets.fonte_media, r1)
        self.password.draw(surface, self.assets.fonte_pequena, self.assets.fonte_media, r2)

        signup_btn = Button("Cadastrar", self._signup_button_rect, self._do_signup, enabled=True)
        back_btn = Button(
            "Voltar",
            self._back_button_rect,
            lambda: self.sm.change(MenuState(self.surface, self.assets, self.sm), selected_skin=self.selected_skin),
            enabled=True,
        )

        signup_btn.draw(surface, self.assets.fonte_pequena, self._mouse_pos, focused=False)
        back_btn.draw(surface, self.assets.fonte_pequena, self._mouse_pos, focused=False)

        if self.msg:
            m = self.assets.fonte_pequena.render(self.msg, True, style.DANGER)
            surface.blit(m, (surface.get_width() // 2 - m.get_width() // 2, panel.bottom - 72))


class PlayingState(State):
    def __init__(self, surface, assets, sm, world: World, selected_skin=None):
        self.surface = surface
        self.assets = assets
        self.sm = sm
        self.world = world
        self.selected_skin = selected_skin if selected_skin is not None else PLAYER_SKINS[0]

    def handle_event(self, event):
        pause = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pause = True
        # Botão Start (7 ou 9) ou botão B (1) pausam
        if event.type == pygame.JOYBUTTONDOWN and event.button in (7, 9, 1):
            pause = True
        if pause:
            self.sm.change(
                PauseState(
                    self.surface,
                    self.assets,
                    self.sm,
                    self.world,
                    selected_skin=self.selected_skin,
                )
            )

    def update(self, now_ms: int):
        result = self.world.update(now_ms)
        if result == "GAMEOVER":
            elapsed_ms = self.world.elapsed_ms(now_ms)
            self.sm.change(
                GameOverState(
                    self.surface,
                    self.assets,
                    self.sm,
                    self.world.wave,
                    elapsed_ms,
                    selected_skin=self.selected_skin,
                )
            )

    def draw(self, surface: pygame.Surface):
        surface.fill(style.BG)
        draw_game_grid(surface)

        for c in self.world.collectibles:
            c.draw(surface, self.assets.fonte_pequena)
        for e in self.world.enemies:
            e.draw(surface, self.assets.fonte_pequena)
        self.world.player.draw(surface)

        now = pygame.time.get_ticks()
        draw_hud(surface, self.assets, self.world, now)
        draw_boss_announcement(surface, self.assets, self.world.boss_announcement, now)


_PAUSE_OPTIONS = ["Continuar", "Voltar ao Menu"]


class PauseState(State):
    def __init__(self, surface, assets, sm, world: World, selected_skin=None):
        self.surface = surface
        self.assets = assets
        self.sm = sm
        self.world = world
        self.selected_skin = selected_skin if selected_skin is not None else PLAYER_SKINS[0]
        self.pause_start = 0
        self._selected = 0
        self._confirming = False
        self._dialog = ConfirmDialog("Voltar ao menu?")
        self._mouse_pos = (-99999, -99999)

    def enter(self, **kwargs):
        self.pause_start = pygame.time.get_ticks()
        self._selected = 0
        self._confirming = False
        self._mouse_pos = (-99999, -99999)

    def _resume(self):
        now = pygame.time.get_ticks()
        self.world.compensate_pause(now - self.pause_start)
        self.sm.change(
            PlayingState(
                self.surface,
                self.assets,
                self.sm,
                self.world,
                selected_skin=self.selected_skin,
            )
        )

    def _go_menu(self):
        self.assets.stop_music()
        self.sm.change(MenuState(self.surface, self.assets, self.sm), selected_skin=self.selected_skin)

    def _panel_rect(self, surface: pygame.Surface) -> pygame.Rect:
        screen = surface.get_rect()
        w = clamp_size(int(screen.w * 0.40), 340, 480)
        h = clamp_size(int(screen.h * 0.38), 220, 300)
        return pygame.Rect(screen.centerx - w // 2, screen.centery - h // 2, w, h)

    def _option_rect(self, surface: pygame.Surface, idx: int) -> pygame.Rect:
        rect = self._panel_rect(surface)
        w, h = rect.w, rect.h
        btn_h = clamp_size(int(h * 0.22), 44, 56)
        gap = clamp_size(int(h * 0.07), 10, 16)
        pad_x = clamp_size(int(w * 0.10), 20, 40)
        area_y = rect.y + clamp_size(int(h * 0.40), 90, 120)
        return pygame.Rect(rect.x + pad_x, area_y + idx * (btn_h + gap), w - pad_x * 2, btn_h)

    def handle_event(self, event):
        if hasattr(event, "pos"):
            self._mouse_pos = event.pos

        if self._confirming:
            result = self._dialog.handle_event(event)
            if result == "yes":
                self._go_menu()
            elif result == "no":
                self._confirming = False
                self.pause_start = pygame.time.get_ticks()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._resume()
                return
            if event.key in (pygame.K_UP, pygame.K_w):
                self._selected = (self._selected - 1) % len(_PAUSE_OPTIONS)
                return
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self._selected = (self._selected + 1) % len(_PAUSE_OPTIONS)
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self._selected == 0:
                    self._resume()
                else:
                    self._confirming = True
                    self._dialog = ConfirmDialog("Voltar ao menu?")
                return

        # Controle
        nav = gp.nav_vertical(event)
        if nav != 0:
            self._selected = (self._selected + nav) % len(_PAUSE_OPTIONS)
            return
        if gp.is_confirm(event):
            if self._selected == 0:
                self._resume()
            else:
                self._confirming = True
                self._dialog = ConfirmDialog("Voltar ao menu?")
            return
        if gp.is_back(event):
            self._resume()
            return

        if event.type == pygame.MOUSEMOTION:
            for i in range(len(_PAUSE_OPTIONS)):
                if self._option_rect(self.surface, i).collidepoint(self._mouse_pos):
                    self._selected = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._option_rect(self.surface, 0).collidepoint(self._mouse_pos):
                self._resume()
                return
            if self._option_rect(self.surface, 1).collidepoint(self._mouse_pos):
                self._confirming = True
                self._dialog = ConfirmDialog("Voltar ao menu?")
                return

    def draw(self, surface: pygame.Surface):
        surface.fill(style.BG)
        draw_game_grid(surface)
        for c in self.world.collectibles:
            c.draw(surface, self.assets.fonte_pequena)
        for e in self.world.enemies:
            e.draw(surface, self.assets.fonte_pequena)
        self.world.player.draw(surface)
        draw_hud(surface, self.assets, self.world, pygame.time.get_ticks())

        draw_overlay(surface)

        rect = self._panel_rect(surface)
        draw_panel(surface, rect)

        draw_title(surface, self.assets.fonte_grande, "PAUSADO", rect.y + 18, style.TEXT)

        option_colors = [style.ACCENT, style.DANGER]
        for i, label in enumerate(_PAUSE_OPTIONS):
            r = self._option_rect(surface, i)
            focused = (i == self._selected)
            cor = option_colors[i]

            bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            bg.fill((*cor, 40) if focused else (*style.PANEL_BG, 80))
            surface.blit(bg, r.topleft)
            pygame.draw.rect(surface, cor if focused else style.PANEL_BORDER, r, width=2, border_radius=style.RADIUS)

            if focused:
                cx, cy = r.left - 14, r.centery
                pygame.draw.polygon(surface, cor, [(cx, cy - 6), (cx, cy + 6), (cx + 8, cy)])

            txt = self.assets.fonte_media.render(label, True, cor if focused else style.TEXT_MUTED)
            surface.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))

        hint = self.assets.fonte_pequena.render(
            "↑↓ navegar   |   ENTER selecionar   |   ESC continuar",
            True,
            style.TEXT_MUTED,
        )
        surface.blit(hint, (surface.get_width() // 2 - hint.get_width() // 2, rect.bottom + 10))

        if self._confirming:
            self._dialog.draw(surface, self.assets)


_GO_OPTIONS = ["Menu Principal", "Jogar de Novo"]


class GameOverState(State):
    def __init__(self, surface, assets, sm, wave_dead: int, elapsed_ms: int, selected_skin=None):
        self.surface = surface
        self.assets = assets
        self.sm = sm
        self.wave_dead = wave_dead
        self.elapsed_ms = int(elapsed_ms)
        self.selected_skin = selected_skin if selected_skin is not None else PLAYER_SKINS[0]
        self.msg = ""
        self.top10 = []
        self._selected = 0
        self._mouse_pos = (-99999, -99999)

    def enter(self, **kwargs):
        self._selected = 0
        self._mouse_pos = (-99999, -99999)

        sess = get_session()
        if sess:
            try:
                submit_score(sess.user_id, sess.username, self.wave_dead, self.elapsed_ms)
            except Exception as e:
                self.msg = f"Falha ao enviar score: {e}"

            try:
                set_best_wave(get_my_best(sess.user_id))
            except Exception:
                pass

        try:
            self.top10 = get_top10()
        except Exception as e:
            if not self.msg:
                self.msg = f"Falha ao carregar ranking: {e}"
            self.top10 = []

    def _panel_rect(self, surface: pygame.Surface) -> pygame.Rect:
        screen = surface.get_rect()
        w = clamp_size(int(screen.w * 0.86), 640, 860)
        h = clamp_size(int(screen.h * 0.82), 480, 580)
        return pygame.Rect(screen.centerx - w // 2, int(screen.h * 0.09), w, h)

    def _option_rect(self, surface: pygame.Surface, idx: int) -> pygame.Rect:
        rect = self._panel_rect(surface)
        btn_w = clamp_size(int(rect.w * 0.34), 140, 220)
        btn_h = 46
        gap = clamp_size(int(rect.w * 0.06), 16, 32)
        total = btn_w * 2 + gap
        bx = rect.centerx - total // 2
        by = rect.bottom - btn_h - 28
        return pygame.Rect(bx + idx * (btn_w + gap), by, btn_w, btn_h)

    def _activate_selected(self):
        if self._selected == 0:
            self.sm.change(MenuState(self.surface, self.assets, self.sm), selected_skin=self.selected_skin)
        else:
            if is_logged_in():
                world = World(skin=self.selected_skin, assets=self.assets)
                self.assets.play_music()
                self.sm.change(
                    PlayingState(
                        self.surface,
                        self.assets,
                        self.sm,
                        world,
                        selected_skin=self.selected_skin,
                    )
                )
            else:
                self.sm.change(
                    MenuState(self.surface, self.assets, self.sm),
                    msg="Logue para jogar.",
                    selected_skin=self.selected_skin,
                )

    def handle_event(self, event):
        if hasattr(event, "pos"):
            self._mouse_pos = event.pos

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_UP):
                self._selected = (self._selected - 1) % len(_GO_OPTIONS)
                return
            if event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                self._selected = (self._selected + 1) % len(_GO_OPTIONS)
                return
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._activate_selected()
                return

        # Controle
        nav = gp.nav_horizontal(event) or gp.nav_vertical(event)
        if nav != 0:
            self._selected = (self._selected + nav) % len(_GO_OPTIONS)
            return
        if gp.is_confirm(event):
            self._activate_selected()
            return

        if event.type == pygame.MOUSEMOTION:
            for i in range(len(_GO_OPTIONS)):
                if self._option_rect(self.surface, i).collidepoint(self._mouse_pos):
                    self._selected = i

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(_GO_OPTIONS)):
                if self._option_rect(self.surface, i).collidepoint(self._mouse_pos):
                    self._selected = i
                    self._activate_selected()
                    return

    def draw(self, surface: pygame.Surface):
        surface.fill((28, 10, 12))
        screen = surface.get_rect()
        rect = self._panel_rect(surface)
        draw_panel(surface, rect)

        draw_title(surface, self.assets.fonte_grande, "GAME OVER", rect.y + 12, style.DANGER)
        draw_subtitle(surface, self.assets.fonte_media, f"Você alcançou a wave {self.wave_dead}", rect.y + 78, style.TEXT)
        draw_subtitle(
            surface,
            self.assets.fonte_pequena,
            f"Tempo: {format_time_ms(self.elapsed_ms)}",
            rect.y + 112,
            style.TEXT_MUTED,
        )

        sess = get_session()
        sub = f"Seu record: {sess.best_wave}" if sess else "Faça login para salvar record."
        draw_subtitle(surface, self.assets.fonte_pequena, sub, rect.y + 138, style.TEXT_MUTED)

        y = rect.y + 182
        title = self.assets.fonte_media.render("TOP 10", True, style.ACCENT)
        surface.blit(title, (screen.centerx - title.get_width() // 2, y))
        y += 44

        if self.top10:
            for idx, row in enumerate(self.top10[:10], start=1):
                name = row.get("username", "PLAYER")
                best = int(row.get("best_wave", 0))
                best_time_ms = int(row.get("best_time_ms", 0))

                line = f"{idx}. {name} - Onda {best} - {format_time_ms(best_time_ms)}"

                color = style.ACCENT if sess and name == sess.username else style.TEXT
                s = self.assets.fonte_pequena.render(line, True, color)
                surface.blit(s, (screen.centerx - s.get_width() // 2, y))
                y += 26
        else:
            s = self.assets.fonte_pequena.render("Ranking indisponível.", True, style.TEXT_MUTED)
            surface.blit(s, (screen.centerx - s.get_width() // 2, y))

        option_colors = [style.TEXT_MUTED, style.ACCENT]
        for i, label in enumerate(_GO_OPTIONS):
            r = self._option_rect(surface, i)
            focused = (i == self._selected)
            cor = option_colors[i]

            bg = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
            bg.fill((*cor, 40) if focused else (*style.PANEL_BG, 80))
            surface.blit(bg, r.topleft)
            pygame.draw.rect(surface, cor if focused else style.PANEL_BORDER, r, width=2, border_radius=style.RADIUS)

            txt = self.assets.fonte_pequena.render(label, True, cor if focused else style.TEXT_MUTED)
            surface.blit(txt, (r.centerx - txt.get_width() // 2, r.centery - txt.get_height() // 2))

        hint = self.assets.fonte_pequena.render(
            "←→ navegar   |   ENTER / clique confirmar",
            True,
            style.TEXT_MUTED,
        )
        surface.blit(hint, (screen.centerx - hint.get_width() // 2, rect.bottom - 18))

        if self.msg:
            m = self.assets.fonte_pequena.render(self.msg, True, style.DANGER)
            surface.blit(m, (screen.centerx - m.get_width() // 2, rect.bottom + 8))