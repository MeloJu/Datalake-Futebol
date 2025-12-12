# Fontes de Dados de Futebol

## ✅ Fontes Ativas

### FBref (via soccerdata)
- **Status:** ✅ Funcionando
- **Cobertura:** Big 5 European Leagues + Copas do Mundo
- **Ligas:** Premier League, La Liga, Serie A, Bundesliga, Ligue 1
- **Limitações:** ❌ Não tem MLS, Brasileirão, ligas secundárias
- **Biblioteca:** `soccerdata` (Python)
- **Uso:** `scripts/generate_players_teams_historical.py`

## 🔍 Opções para Temporadas Faltantes (MLS/Brasileirão)

### 1. Transfermarkt (Web Scraping) ⭐ RECOMENDADO
- **URL:** https://www.transfermarkt.com
- **Cobertura:** Global (MLS, Brasileirão, todas as ligas)
- **Dados Disponíveis:**
  - Estatísticas por temporada (jogos, gols, assistências)
  - Transferências e valores de mercado
  - Dados biográficos completos
- **Método:** BeautifulSoup4 scraping (já instalado)
- **Desafios:** 
  - HTML pode mudar (requer manutenção)
  - Rate limiting (respeitar delays entre requests)
- **Exemplo de URL:**
  - Kaká: https://www.transfermarkt.com/kaka/leistungsdaten/spieler/3368
  - São Paulo 2014: filtrar por temporada

### 2. API-Football (RapidAPI) 💰
- **URL:** https://rapidapi.com/api-sports/api/api-football
- **Cobertura:** Global (550+ ligas)
- **Dados:** Estatísticas completas, jogadores, times, partidas
- **Limitações:**
  - ⚠️ Free tier: 100 requests/dia
  - 💰 Planos pagos a partir de $10/mês
- **Vantagem:** API estruturada, fácil de usar
- **Biblioteca:** `requests` (já instalado)

### 3. FBref Direto (Manual scraping)
- **URL:** https://fbref.com/en/comps/22/Major-League-Soccer-Stats
- **Cobertura:** MLS disponível no site, mas não via soccerdata
- **Método:** `pandas.read_html()` direto do HTML
- **Desafio:** Estrutura de tabelas complexa

### 4. Transfermarkt API (Não Oficial)
- **Biblioteca:** `transfermarkt-api` (PyPI)
- **Status:** ⚠️ Não oficial, pode quebrar
- **Instalação:** `pip install transfermarkt-api`
- **Documentação:** https://github.com/felipeall/transfermarkt-api

### 5. SofaScore API
- **URL:** https://api.sofascore.com
- **Cobertura:** Global
- **Status:** ❌ Bloqueada (403 Forbidden em testes anteriores)
- **Alternativa:** Requer browser automation (selenium/undetected-chromedriver)

## 📋 Recomendação para Kaká (MLS + São Paulo)

### Opção A: Transfermarkt Web Scraping (Mais Simples)
```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_player_season_stats(player_id, player_name):
    """
    Extrai estatísticas de todas as temporadas do Transfermarkt.
    
    Args:
        player_id: ID do jogador no Transfermarkt (ex: 3368 para Kaká)
        player_name: Nome do jogador para o arquivo
    """
    url = f"https://www.transfermarkt.com/{player_name}/leistungsdaten/spieler/{player_id}/plus/1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extrair tabela de estatísticas
    # (implementar parsing específico)
    
    return df

# Uso
kaka_missing = get_player_season_stats(3368, 'kaka')
# Filtrar temporadas: 2001, 2014-2015 (São Paulo), 2015-2017 (Orlando)
```

### Opção B: API-Football (Mais Robusto)
```python
import requests

API_KEY = "sua_chave_aqui"
url = "https://api-football-v1.p.rapidapi.com/v3/players"

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

# Buscar estatísticas do Kaká em temporadas específicas
params = {
    "search": "Kaká",
    "season": 2015,
    "league": 253  # MLS league ID
}

response = requests.get(url, headers=headers, params=params)
data = response.json()
```

### Opção C: Entrada Manual (Mais Rápido para 1 jogador)
Criar CSV manual com as temporadas faltantes:

```csv
season,team,league,MP,Starts,Min,Gls,Ast
2001,São Paulo,BRA-Serie A,27,25,2200,12,8
1415,São Paulo,BRA-Serie A,18,15,1234,2,3
1516,Orlando City,USA-MLS,30,29,2514,9,9
1617,Orlando City,USA-MLS,22,20,1711,2,7
1718,Orlando City,USA-MLS,11,9,756,1,3
```

Depois merge com o dataset existente.

## 🎯 Próximos Passos

1. **Decidir abordagem:** Scraping Transfermarkt vs API vs Manual
2. **Criar script:** `scripts/fetch_missing_seasons_transfermarkt.py`
3. **Merge:** Combinar com `kaka_enriched.csv` existente
4. **Documentar:** Adicionar fonte no metadata JSON

## 📚 Recursos

- Transfermarkt: https://www.transfermarkt.com/kaka/profil/spieler/3368
- API-Football Docs: https://www.api-football.com/documentation-v3
- FBref MLS: https://fbref.com/en/comps/22/Major-League-Soccer-Stats
- Soccerdata Docs: https://soccerdata.readthedocs.io/
