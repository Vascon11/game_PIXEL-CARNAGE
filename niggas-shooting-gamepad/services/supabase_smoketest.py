from services.supabase_client import get_supabase


def main():
    supabase = get_supabase()

    print("✅ Supabase client criado com sucesso.")
    print("URL:", supabase.supabase_url)

    # Teste simples: pegar o usuário atual (vai ser None se não estiver logado)
    try:
        user = supabase.auth.get_user()
        print("Auth get_user() OK:", user.user is not None)
    except Exception as e:
        print("Auth get_user() falhou:", e)

    # Teste tabela (vai falhar se você ainda não criou o leaderboard)
    try:
        resp = supabase.table("leaderboard").select("username,best_wave").limit(1).execute()
        print("✅ SELECT leaderboard OK:", resp.data)
    except Exception as e:
        print("⚠️ SELECT leaderboard falhou (normal se tabela não foi criada):", e)


if __name__ == "__main__":
    main()