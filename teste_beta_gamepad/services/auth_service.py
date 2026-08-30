from dataclasses import dataclass
from services.supabase_client import get_supabase


@dataclass
class AuthUser:
    user_id: str
    email: str
    username: str


def sign_up(email: str, password: str, username: str) -> AuthUser:
    supabase = get_supabase()

    resp = supabase.auth.sign_up({
        "email": email,
        "password": password,
        "options": {"data": {"username": username}}
    })

    if not resp.user:
        raise RuntimeError("Falha no cadastro (user vazio).")

    # Em alguns projetos, session pode ser None se exigir confirmação de email.
    # Mesmo assim, o usuário pode existir. Para o jogo, recomendo desativar confirmação por enquanto.
    meta = resp.user.user_metadata or {}
    uname = meta.get("username") or username

    return AuthUser(
        user_id=resp.user.id,
        email=resp.user.email or email,
        username=uname
    )


def sign_in(email: str, password: str) -> AuthUser:
    supabase = get_supabase()

    resp = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if not resp.user:
        raise RuntimeError("Falha no login: usuário/senha inválidos ou sem user.")

    meta = resp.user.user_metadata or {}
    uname = meta.get("username") or "PLAYER"

    return AuthUser(
        user_id=resp.user.id,
        email=resp.user.email or email,
        username=uname
    )


def sign_out() -> None:
    supabase = get_supabase()
    supabase.auth.sign_out()