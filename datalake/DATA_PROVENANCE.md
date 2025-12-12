Resumo da origem dos dados e instruções de reprodução

Fontes principais
- FBref: estatísticas por temporada (player-season). Coletadas usando a biblioteca `soccerdata` (instalada no ambiente `datalake`).

Como os dados foram obtidos
- Preferimos `soccerdata.FBref()` porque lida com versões históricas e estruturas de tabela irregulares do site.
- Para casos em que o acesso por HTTP era bloqueado (HTTP 403), experimentamos fallback por navegador (`undetected-chromedriver` + Selenium) e extração de blocos comentados no HTML; isso é frágil e só usado como fallback experimental.
- Geramos dois conjuntos principais:
  - `players_historical_1995_2024.csv` e `teams_historical_1995_2024.csv` — resultados do `scripts/generate_players_teams_historical.py` (seasons 1995–2024).
  - `players.csv` e `teams.csv` — dados obtidos anteriormente (padrão/configuração do `soccerdata`).
- Unimos e normalizei os arquivos em:
  - `players_complete_1995_2025.csv`
  - `teams_complete_1995_2025.csv`

Scripts-chave
- `scripts/generate_players_teams_historical.py` — baixa vários anos (aceita args start_year end_year).
- `scripts/generate_players_teams.py` — gerador curto (padrão).
- `scripts/normalize_players_teams.py` — normaliza `season_period` e nomes de colunas.
- `scripts/merge_normalize_players_teams.py` — normaliza e concatena histórico + atual, produz arquivos `*_complete_1995_2025.csv`.

Ambiente e dependências
- Recomendado: Miniconda + conda env `datalake` (Python 3.11). Usamos `conda install -c conda-forge pandas lxml requests` e `pip install soccerdata` quando necessário.
- Alternativa para Windows: usar o `conda` para evitar erros de compilação do `lxml` via `pip`.

Observações e pontos a considerar
- Cobertura histórica: FBref nem sempre tem todas as temporadas em todas as ligas; se um jogador histórico não aparecer (ex.: Ronaldinho), podemos estender o range de temporadas ou recorrer a Transfermarkt para históricos de carreira.
- Anti-bot: muitos endpoints (SofaScore/alguns caminhos do FBref) retornam 403; a abordagem está documentada em `ingestors/` (Selenium fallback, headers, requests-cache).
- Arquivos removidos: scripts de teste temporários em `tests/` foram apagados para limpeza. A virtualenv local `.venv/` foi mantida — se quiser, posso removê-la também.

Comandos úteis
1) Rodar gerador histórico (exemplo 1995–2024):
   conda activate datalake; python scripts/generate_players_teams_historical.py 1995 2024
2) Normalizar e juntar:
   conda activate datalake; python scripts/merge_normalize_players_teams.py

Se quiser um notebook com análises, eu gero um `notebook.ipynb` pronto com exemplos de consultas (busca por nome, agregações por temporada, carreiras).
