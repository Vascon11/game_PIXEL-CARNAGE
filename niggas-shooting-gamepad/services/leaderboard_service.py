from typing import List, Dict, Optional
from services.supabase_client import get_supabase


FAKE_TIME_MS_THRESHOLD = 2147483647


def _require_auth():
    supabase = get_supabase()
    u = supabase.auth.get_user()
    if not u or not u.user:
        raise RuntimeError("Você não está autenticado no Supabase (session ausente).")
    return u.user


def normalize_time_ms(ms: int) -> int:
    ms = max(0, int(ms))
    if ms >= FAKE_TIME_MS_THRESHOLD:
        return 0
    return ms


def format_time_ms(ms: int) -> str:
    ms = normalize_time_ms(ms)
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def get_top10() -> List[Dict]:
    supabase = get_supabase()

    resp = (
        supabase.table("leaderboard")
        .select("username,best_wave,best_time_ms")
        .order("best_wave", desc=True)
        .order("best_time_ms", desc=False)
        .limit(10)
        .execute()
    )

    rows = resp.data or []
    for row in rows:
        row["best_time_ms"] = normalize_time_ms(row.get("best_time_ms", 0))
    return rows


def get_my_best(user_id: str) -> int:
    supabase = get_supabase()

    resp = (
        supabase.table("leaderboard")
        .select("best_wave")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not resp.data:
        return 0
    return int(resp.data[0]["best_wave"])


def get_my_best_entry(user_id: str) -> Optional[Dict]:
    supabase = get_supabase()

    resp = (
        supabase.table("leaderboard")
        .select("user_id,username,best_wave,best_time_ms")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if not resp.data:
        return None

    row = resp.data[0]
    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "best_wave": int(row["best_wave"]),
        "best_time_ms": normalize_time_ms(row.get("best_time_ms", 0)),
    }


def _is_better_score(new_wave: int, new_time_ms: int, current: Optional[Dict]) -> bool:
    if current is None:
        return True

    current_wave = int(current["best_wave"])
    current_time_ms = normalize_time_ms(current["best_time_ms"])

    if new_wave > current_wave:
        return True

    if new_wave < current_wave:
        return False

    return new_time_ms < current_time_ms


def submit_score(user_id: str, username: str, wave: int, time_ms: int) -> None:
    supabase = get_supabase()

    user = _require_auth()
    if user.id != user_id:
        raise RuntimeError("User logado não corresponde ao user_id do score.")

    wave = int(wave)
    time_ms = normalize_time_ms(time_ms)

    current = get_my_best_entry(user_id)

    if not _is_better_score(wave, time_ms, current):
        return

    (
        supabase.table("leaderboard")
        .upsert(
            {
                "user_id": user_id,
                "username": username,
                "best_wave": wave,
                "best_time_ms": time_ms,
            },
            on_conflict="user_id",
        )
        .execute()
    )