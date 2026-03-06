"""
game/state_machine.py
Máquina de estados simples para gerenciar telas do jogo.
"""


class State:
    def enter(self, **kwargs):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, now_ms: int):
        pass

    def draw(self, screen):
        pass


class StateMachine:
    def __init__(self, initial_state: State):
        self.state = initial_state
        self.state.enter()

    def change(self, new_state: State, **kwargs):
        self.state.exit()
        self.state = new_state
        self.state.enter(**kwargs)

    def handle_event(self, event):
        self.state.handle_event(event)

    def update(self, now_ms: int):
        self.state.update(now_ms)

    def draw(self, screen):
        self.state.draw(screen)
