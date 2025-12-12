# ⚽ Football Data Lake & Analytics

> **Projeto completo de ETL e análise de dados de futebol com Python e Power BI**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-green.svg)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Pipeline automatizado de dados de futebol que combina FBref e Transfermarkt para análise completa de carreiras de jogadores (1995-2025).

![CR7 Career Analysis](docs/images/cr7_scatter_chart.png)
*Análise da carreira de Cristiano Ronaldo: evolução de gols por idade*

---

## 🎯 O Que Este Projeto Faz

✅ **Extrai** dados históricos de 19.795 jogadores do FBref (1995-2025)  
✅ **Enriquece** com web scraping do Transfermarkt (ligas faltantes: MLS, Brasileirão, Saudi Pro League)  
✅ **Normaliza** formato de temporadas e remove duplicatas  
✅ **Gera** datasets prontos para Power BI/Tableau/Python  

### Casos de Uso:

- 📊 Análise comparativa de jogadores (CR7 vs Messi vs Kaká)
- 📈 Identificação de picos de performance por idade
- 🔍 Padrões de longevidade no futebol de elite
- 🎯 Storytelling visual com Power BI

---

## 🚀 Quick Start

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/datalake.git
cd datalake
```

### 2. Instale Dependências

```bash
# Crie ambiente conda (recomendado)
conda create -n datalake python=3.11
conda activate datalake

# Instale pacotes
pip install -r requirements.txt

# Instale lxml via conda (Windows - evita erros de compilação)
conda install -c conda-forge lxml
```

### 3. Execute Pipeline Básico

```bash
# Gerar dataset completo (1995-2025)
python scripts/generate_players_teams_historical.py

# Normalizar dados
python scripts/merge_normalize_players_teams.py

# Resultado: datalake/processed/players_complete_1995_2025.csv (19.795 jogadores)
```

### 4. Enriquecer Jogador Específico

```bash
# Exemplo: Cristiano Ronaldo
python scripts/enrich_player_complete.py "Cristiano Ronaldo"

# Output: datalake/processed/enriched/cristiano_ronaldo_enriched.csv
# Inclui: temporadas FBref + temporadas faltantes do Transfermarkt
```

---

## 📊 Datasets Gerados

### 1. Dataset Principal: `players_complete_1995_2025.csv`

**Dimensões:** 86.930 linhas × 38 colunas  
**Cobertura:** Big 5 European Leagues + World Cups  
**Período:** 1995-2025

**Colunas principais:**
- Identificação: `player`, `team`, `league`, `season`, `nation`, `pos`, `age`
- Performance: `Performance_Gls`, `Performance_Ast`, `Performance_G+A`
- Tempo de jogo: `Playing_Time_MP`, `Playing_Time_Min`, `Playing_Time_90s`
- Expected Goals: `Expected_xG`, `Expected_npxG`, `Expected_xAG`
- Per 90min: `Per_90_Minutes_Gls`, `Per_90_Minutes_Ast`, etc.

### 2. Datasets Enriched: `enriched/*.csv`

**Exemplo:** `cristiano_ronaldo_enriched.csv`

**Dimensões:** 38 temporadas × 49 colunas  
**Inclui:** Todas as ligas (incluindo MLS, Brasileirão, Saudi Pro League)  
**Extras:** 10 colunas de metadata (data nascimento, altura, títulos, etc.)

---

## 🛠️ Arquitetura do Pipeline

```
┌─────────────────┐
│   FBref API     │  (via soccerdata library)
│  1995-2025      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Extract        │  generate_players_teams_historical.py
│  86.930 rows    │  → players_2025.csv
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Transform      │  merge_normalize_players_teams.py
│  Normalize      │  → players_complete_1995_2025.csv
│  Deduplicate    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐       ┌──────────────────┐
│  Enrich         │◄──────┤ Transfermarkt    │
│  Player         │       │  Web Scraping    │
│  Specific       │       └──────────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Load           │  cristiano_ronaldo_enriched.csv
│  Power BI       │  → Dashboard
│  Ready          │
└─────────────────┘
```

---

## 📂 Estrutura do Projeto

```
datalake/
├── 📁 scripts/                      # Scripts de ETL
│   ├── generate_players_teams_historical.py   # Extração FBref
│   ├── merge_normalize_players_teams.py       # Merge e normalização
│   ├── extract_player_career.py               # Extração individual
│   ├── enrich_player_complete.py              # Pipeline completo (automático!)
│   ├── enrich_player_manual.py                # Enriquecimento manual
│   ├── fetch_transfermarkt_seasons.py         # Scraping Transfermarkt
│   ├── deduplicate_player_data.py             # Remoção de duplicatas
│   └── fill_missing_ages.py                   # Preenche idades faltantes
│
├── 📁 datalake/
│   ├── 📁 raw/
│   │   └── 📁 metadata/                       # Metadados de jogadores (JSON)
│   └── 📁 processed/
│       ├── players_complete_1995_2025.csv     # ⭐ Dataset principal
│       ├── teams_complete_1995_2025.csv       # Times agregados
│       └── 📁 enriched/                       # Jogadores individuais
│           ├── cristiano_ronaldo_enriched.csv
│           └── kaka_enriched.csv
│
├── 📄 DATABASE_VARIABLES_GUIDE.md   # 📚 Dicionário das 49 colunas
├── 📄 README_POWERBI_GUIDE_PT.md    # 📊 Guia completo Power BI
├── 📄 DATA_SOURCES.md                # 🔗 Fontes de dados
├── 📄 LINKEDIN_ARTICLE.md            # 📱 Artigos prontos LinkedIn
├── 📄 requirements.txt               # Dependências Python
├── 📄 LICENSE                        # MIT License
└── 📄 .gitignore                     # Arquivos ignorados
```

---

## 🔧 Scripts Principais

### 1. `enrich_player_complete.py` - Pipeline Automatizado ⭐

**O que faz:**
1. Busca jogador no dataset local
2. Encontra ID no Transfermarkt automaticamente
3. Faz scraping de temporadas faltantes
4. Converte formato Transfermarkt → FBref
5. Merge inteligente (sem duplicatas)
6. Cria metadata JSON template
7. Salva CSV enriched pronto para Power BI

**Uso:**
```bash
python scripts/enrich_player_complete.py "Cristiano Ronaldo"
```

**Output:**
```
🔍 Buscando 'Cristiano Ronaldo' no database local...
✅ Encontrado: 32 temporadas

🔍 Buscando ID Transfermarkt...
✅ Encontrado: https://www.transfermarkt.com/cristiano-ronaldo/profil/spieler/8198

🌐 Fazendo scraping Transfermarkt...
✅ 98 temporadas encontradas

📊 Comparando dados...
⚠️ 29 temporadas faltando no FBref:
   - Saudi Pro League (2023-2026)
   - Liga Portugal (2002-2003)
   [...]

🔄 Convertendo formato Transfermarkt → FBref...
✅ 29 temporadas convertidas

💾 Salvando dataset enriched...
✅ datalake/processed/enriched/cristiano_ronaldo_enriched.csv
   38 temporadas | 603 gols | 49 colunas
```

### 2. `generate_players_teams_historical.py` - Geração Dataset Completo

**Uso:**
```bash
python scripts/generate_players_teams_historical.py
```

Gera `players_complete_1995_2025.csv` com 86.930 linhas.

### 3. `deduplicate_player_data.py` - Limpeza de Duplicatas

**Uso:**
```bash
python scripts/deduplicate_player_data.py "Cristiano Ronaldo"
```

Remove linhas duplicadas onde `team="Premier League"` aparece junto com `team="Manchester Utd"`.

---

## 📚 Documentação Detalhada

### 🎯 Para Análise Power BI:
👉 **[README_POWERBI_GUIDE_PT.md](README_POWERBI_GUIDE_PT.md)**
- Como importar dados no Power BI
- Quando usar SUM vs AVERAGE
- Medidas DAX prontas para usar
- Erros comuns e soluções
- Template de dashboard

### 📖 Para Entender os Dados:
👉 **[DATABASE_VARIABLES_GUIDE.md](DATABASE_VARIABLES_GUIDE.md)**
- Explicação das 49 colunas
- Quando usar cada variável
- Exemplos de análises (gols × idade × performance)
- Fórmulas DAX para métricas avançadas

### 🔗 Para Saber as Fontes:
👉 **[DATA_SOURCES.md](DATA_SOURCES.md)**
- FBref coverage (Big 5 + World Cups)
- Transfermarkt coverage (global)
- Limitações conhecidas
- Metodologia de merge

### 📱 Para Divulgar no LinkedIn:
👉 **[LINKEDIN_ARTICLE.md](LINKEDIN_ARTICLE.md)**
- 3 versões de artigo (curta, média, longa)
- 5 opções de legendas para gráficos
- Estratégia de publicação (4 semanas)
- Templates de comentários

---

## 💡 Exemplos de Uso

### Exemplo 1: Comparar CR7 vs Kaká

```bash
# 1. Enriquecer ambos
python scripts/enrich_player_complete.py "Cristiano Ronaldo"
python scripts/enrich_player_complete.py "Kaká"

# 2. Importar os 2 CSVs no Power BI
# 3. Criar visual com player como filtro
```

### Exemplo 2: Análise de Longevidade

```python
import pandas as pd

# Carregar dataset principal
df = pd.read_csv('datalake/processed/players_complete_1995_2025.csv')

# Jogadores que jogaram após 35 anos
veterans = df[df['age'] > 35].groupby('player').agg({
    'age': 'max',
    'Performance_Gls': 'sum',
    'Playing_Time_MP': 'sum'
}).sort_values('age', ascending=False)

print(veterans.head(20))
```

### Exemplo 3: Identificar Picos de Performance

```python
# Idade média do pico (mais gols em uma temporada)
peak_ages = df.loc[df.groupby('player')['Performance_Gls'].idxmax()]
print(f"Idade média do pico: {peak_ages['age'].mean():.1f} anos")
# Output: ~27.3 anos
```

---

## 🎨 Visualizações Power BI

### Scatter Chart: Gols por Idade

```
Values: (vazio)
X Axis: age
Y Axis: Performance_Gls (Sum)
Legend: team
Size: Playing_Time_Min (Sum)
```

![Scatter Chart Example](docs/images/scatter_chart_tutorial.png)

### Line Chart: Evolução Temporal

```
X Axis: season_period
Y Axis: Performance_Gls (Sum)
Legend: player (para comparação)
```

### Bar Chart: Gols por Liga

```
Y Axis: league
X Axis: Performance_Gls (Sum)
Tooltips: Playing_Time_MP, Per_90_Minutes_Gls
```

---

## ⚠️ Limitações Conhecidas

### FBref Coverage
❌ Não inclui: MLS, Brasileirão, Saudi Pro League, Liga Portugal  
❌ Copas domésticas: parcial  
✅ Inclui: Big 5 European Leagues, World Cups, Euros

### Transfermarkt Coverage
✅ Inclui: Todas as ligas globalmente  
❌ Stats limitadas: apenas gols, assists, jogos (sem xG, passes, etc)

### Solução Hybrid
✅ FBref = stats detalhadas (38 colunas)  
✅ Transfermarkt = completude histórica (todas ligas)  
✅ Merge = melhor dos dois mundos!

---

## 🤝 Contribuindo

Contribuições são bem-vindas! 

### Como contribuir:
1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Áreas para contribuir:
- [ ] Adicionar mais fontes de dados (Understat, Whoscored)
- [ ] Criar testes automatizados
- [ ] Expandir para outras ligas (J-League, Eredivisie)
- [ ] API REST para consulta de dados
- [ ] Dashboard web interativo

---

## 📝 Changelog

### v1.0.0 (2025-01-12)
- ✅ Pipeline ETL completo (FBref + Transfermarkt)
- ✅ 86.930 jogadores (1995-2025)
- ✅ Enrichment automatizado
- ✅ Documentação completa em PT-BR
- ✅ Guias Power BI + LinkedIn

---

## 📜 Licença

Este projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

### Créditos:

- **FBref data:** Via biblioteca [soccerdata](https://github.com/probberechts/soccerdata)
- **Transfermarkt data:** Web scraping ético com rate limiting
- **Inspiração:** Kaká (melhor jogador de todos os tempos! ⚽)

---

## 🔗 Links Úteis

- 📊 [Power BI Desktop](https://powerbi.microsoft.com/downloads/)
- 🐍 [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- 📚 [soccerdata docs](https://soccerdata.readthedocs.io/)
- 🌐 [FBref](https://fbref.com/)
- 🌐 [Transfermarkt](https://www.transfermarkt.com/)

---

## 📧 Contato

Dúvidas? Sugestões? Abra uma [issue](https://github.com/seu-usuario/datalake/issues) ou entre em contato!

**Autor:** [Seu Nome]  
**LinkedIn:** [Seu perfil]  
**Email:** seu@email.com

---

⭐ **Se este projeto foi útil, deixe uma estrela no GitHub!** ⭐


### Primary: FBref (via soccerdata)
- **Method**: Python library `soccerdata` with FBref scraper
- **Why**: Handles FBref's irregular table structures and historical data gracefully
- **Coverage**: 1995-2025 seasons across major European leagues
- **Columns**: 38 metrics including basic stats, expected goals, progression metrics

### Future Sources (Ingestors Ready)
- **SofaScore**: Real-time match data and detailed player ratings
- **Understat**: Expected goals models and shot maps
- **Transfermarkt**: Transfer history and market values

## Setup

### Prerequisites
- Python 3.11+
- Miniconda or Anaconda (recommended for Windows)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd datalake
   ```

2. **Create conda environment (recommended)**
   ```bash
   conda create -n datalake python=3.11
   conda activate datalake
   ```

3. **Install dependencies**
   ```bash
   # Core dependencies via conda (avoids lxml compilation issues on Windows)
   conda install -c conda-forge pandas lxml requests -y
   
   # Python packages
   pip install soccerdata python-dotenv rapidfuzz requests-cache
   ```

4. **Configure environment** (optional)
   ```bash
   # Create .env file for API keys if using other sources
   echo "API_KEY=your_key_here" > .env
   ```

## Usage

### Quick Start: Use Existing Data

The repository includes pre-processed datasets ready for analysis:

```python
import pandas as pd

# Load complete player dataset (1995-2025)
players = pd.read_csv('datalake/processed/players_complete_1995_2025.csv')

# Load complete team dataset (1995-2025)
teams = pd.read_csv('datalake/processed/teams_complete_1995_2025.csv')

# Example: Find Cristiano Ronaldo's career stats
cr7 = players[players['player'].str.contains('Cristiano', case=False)]
print(cr7[['season_period', 'team', 'league', 'Performance_Gls', 'Performance_Ast']])
```

### Regenerate Data from Scratch

#### Option 1: Generate Historical Data (1995-2024)

```bash
conda activate datalake
python scripts/generate_players_teams_historical.py 1995 2024
```

This will:
- Fetch player-season stats from FBref for 30 seasons
- Save to `datalake/processed/players_historical_1995_2024.csv` and `teams_historical_1995_2024.csv`
- Takes ~6-10 minutes depending on network speed

#### Option 2: Generate Recent Data Only

```bash
conda activate datalake
python scripts/generate_players_teams.py
```

This uses `soccerdata` defaults (typically last 5 seasons).

#### Option 3: Merge Historical + Recent

```bash
conda activate datalake
python scripts/merge_normalize_players_teams.py
```

This script:
1. Loads historical and recent datasets
2. Normalizes column names and season formats
3. Concatenates and deduplicates by `[league, season, team, player]`
4. Outputs `players_complete_1995_2025.csv` and `teams_complete_1995_2025.csv`

## Data Schema

### Players Dataset (`players_complete_1995_2025.csv`)

| Column | Description | Example |
|--------|-------------|---------|
| `league` | League name | `ENG-Premier League` |
| `season` | Season code | `2021` (means 2020-2021) |
| `season_period` | Human-readable season | `2020-2021` |
| `team` | Team name | `Manchester City` |
| `player` | Player name | `Kevin De Bruyne` |
| `nation` | Nationality (3-letter code) | `BEL` |
| `pos` | Position | `MF`, `FW`, `DF`, `GK` |
| `age` | Player age during season | `29.0` |
| `Playing_Time_MP` | Matches played | `25` |
| `Playing_Time_Min` | Minutes played | `2250` |
| `Performance_Gls` | Goals scored | `10` |
| `Performance_Ast` | Assists | `18` |
| `Expected_xG` | Expected goals | `12.3` |
| `Expected_npxG` | Expected non-penalty goals | `10.1` |
| `Per_90_Minutes_Gls` | Goals per 90 minutes | `0.40` |

**Total**: 38 columns, 86,930 rows (as of historical 1995-2024 generation)

### Teams Dataset (`teams_complete_1995_2025.csv`)

Aggregated team-level statistics per season:
- Numeric columns summed across all players
- Same league/season/team structure
- **Total**: 3,206 rows (as of historical generation)

## Common Queries

### Find a Specific Player's Career

```python
import pandas as pd

players = pd.read_csv('datalake/processed/players_complete_1995_2025.csv')

# Search by name (case-insensitive)
ronaldo = players[players['player'].str.contains('Ronaldo', case=False, na=False)]

# Sort by season
ronaldo_sorted = ronaldo.sort_values('season_period')

print(ronaldo_sorted[['season_period', 'league', 'team', 'Performance_Gls', 'Performance_Ast']])
```

### Top Scorers by Season

```python
# Filter to a specific season
season_2023 = players[players['season'] == '2223']

# Get top 10 scorers
top_scorers = season_2023.nlargest(10, 'Performance_Gls')[
    ['player', 'team', 'league', 'Performance_Gls', 'Performance_Ast']
]
print(top_scorers)
```

### Team Performance Over Time

```python
teams = pd.read_csv('datalake/processed/teams_complete_1995_2025.csv')

# Filter to a specific team
man_city = teams[teams['team'] == 'Manchester City']

# Plot goals over time
import matplotlib.pyplot as plt
man_city_sorted = man_city.sort_values('season_period')
plt.plot(man_city_sorted['season_period'], man_city_sorted['Performance_Gls'])
plt.xlabel('Season')
plt.ylabel('Total Goals')
plt.title('Manchester City Goals per Season')
plt.xticks(rotation=45)
plt.show()
```

## Known Issues & Limitations

### Coverage Gaps
- **Historical players**: Some legendary players (e.g., Pelé, Maradona) are not in the dataset because FBref coverage starts around 1995 for most leagues
- **Lower divisions**: Only top-tier leagues are included by default
- **Women's football**: Limited coverage (can be added by specifying leagues)

### Anti-Bot Measures
- FBref and SofaScore sometimes return HTTP 403
- The `soccerdata` library handles most cases with proper headers and caching
- Fallback to Selenium/undetected-chromedriver is available but fragile (experimental code in `ingestors/`)

### Season Code Format
- Season codes like `0001` mean 2000-2001
- Season codes like `2223` mean 2022-2023
- The `season_period` column provides human-readable format

## Troubleshooting

### `ModuleNotFoundError: No module named 'lxml'`
**Solution**: Use conda to install lxml
```bash
conda install -c conda-forge lxml
```

### `HTTP 403 Forbidden` errors
**Solution**: The `soccerdata` library handles this with caching and retries. If persistent:
1. Wait 30-60 seconds between requests
2. Check if FBref is accessible in your browser
3. Use cached data (soccerdata stores in `~/.soccerdata/`)

### Data appears outdated
**Solution**: Delete soccerdata cache and regenerate
```bash
# On Windows
rmdir /s %USERPROFILE%\.soccerdata

# On macOS/Linux
rm -rf ~/.soccerdata

# Then regenerate
python scripts/generate_players_teams_historical.py 1995 2024
```

## Contributing

Future enhancements:
- [ ] Add Transfermarkt scraper for career histories and market values
- [ ] Implement StatsBomb integration for advanced tactical metrics
- [ ] Add player similarity analysis using embeddings
- [ ] Create interactive dashboards with Plotly/Dash
- [ ] Set up automated daily updates

## License

This project is for educational and research purposes. All data is sourced from publicly available websites. Please respect the terms of service of data providers (FBref, SofaScore, etc.) when using this data.

## Acknowledgments

- **FBref**: Primary data source for player statistics
- **soccerdata**: Python library that makes FBref scraping robust and maintainable
- **Sports Reference**: For providing comprehensive historical sports data

---

**Questions?** Check `datalake/DATA_PROVENANCE.md` for detailed methodology and data lineage documentation.
