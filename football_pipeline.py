import requests
import os
import json
import time

# Carrega variáveis de ambiente de um arquivo .env quando disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # Se python-dotenv não estiver instalado, apenas siga adiante e
    # use as variáveis de ambiente já presentes no sistema.
    pass

# ============================
# Chave da API e base URL (agora via env)
# ============================
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://api.football-data.org/v4")


# ============================
# HEADERS
# ============================
if API_KEY:
    HEADERS = {"X-Auth-Token": API_KEY}
else:
    HEADERS = {}
    print("Aviso: `API_KEY` não encontrada. Crie um arquivo `.env` com `API_KEY=seu_token` ou defina a variável de ambiente.")


# ============================
# Fetch genérico
# ============================
def fetch(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    r = requests.get(url, headers=HEADERS)

    if r.status_code == 200:
        time.sleep(0.2)
        return r.json()

    print(f"[ERRO {r.status_code}] -> {endpoint}")
    return None


# ============================
# Utilidades
# ============================
def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================
# 1. Coletar todas competições do Real Madrid
# ============================
def get_team_competitions(team_id):
    return fetch(f"teams/{team_id}/matches?status=FINISHED")


# ============================
# 2. Pegar todas as temporadas possíveis
# ============================
def get_seasons_from_matches(matches):
    seasons = set()
    for match in matches.get("matches", []):
        if "season" in match and "startDate" in match["season"]:
            seasons.add(match["season"]["startDate"][:4])
    return sorted(seasons)


# ============================
# 3. Baixar todos os jogos por temporada
# ============================
def get_team_matches_season(team_id, season_year):
    return fetch(f"teams/{team_id}/matches?season={season_year}")


# ============================
# PIPELINE COMPLETO
# ============================
def ingest_team_history(team_id, output_dir="datalake"):

    print(f"🚀 Baixando histórico completo do time {team_id}")

    ensure_dir(output_dir)
    ensure_dir(f"{output_dir}/raw")
    ensure_dir(f"{output_dir}/raw/matches")

    # 1. Baixar todos os jogos do time
    data = get_team_competitions(team_id)

    if not data:
        print("Nenhum dado retornado!")
        return

    # 2. Encontrar temporadas possíveis
    seasons = get_seasons_from_matches(data)
    print(f"📌 Temporadas encontradas: {seasons}")

    # 3. Baixar todos os jogos de cada temporada
    for season in seasons:
        print(f"\n📅 Baixando temporada {season}")

        season_matches = get_team_matches_season(team_id, season)

        if not season_matches or "matches" not in season_matches:
            continue

        for match in season_matches["matches"]:
            match_id = match["id"]
            print(f"   ⚽ Match {match_id}")
            save_json(match, f"{output_dir}/raw/matches/{match_id}.json")

    print("\n🎉 Download completo!")
