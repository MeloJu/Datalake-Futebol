# ⚽ Football Analytics Data Lake

> **Comprehensive football statistics pipeline from FBref & Transfermarkt to Power BI analytics**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-green.svg)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📊 Overview

A professional data lake solution for football analytics, integrating data from multiple sources (FBref, Transfermarkt) and providing automated pipelines for player career analysis. Built for Power BI visualization and statistical analysis.

### Key Features

- 🎯 **19,795+ players** from 1995-2025
- 🏆 **Multi-source integration** (FBref + Transfermarkt)
- 📈 **Automated enrichment pipeline** with classification
- 🔄 **Power BI ready** datasets with proper typing
- 🌍 **International coverage** (all major leagues + competitions)

## 🏗️ Architecture

```
datalake/
├── datalake/
│   ├── raw/                    # Source data (FBref, Transfermarkt)
│   │   ├── metadata/          # Player biographical data
│   │   ├── matches/           # Match-level statistics
│   │   └── transfermarkt/     # Supplemental transfer data
│   └── processed/
│       ├── enriched/          # Ready for Power BI
│       │   ├── cristiano_ronaldo_enriched.csv
│       │   └── kaka_enriched.csv
│       ├── players_complete_1995_2025.csv    # 19,795 players
│       ├── teams_complete_1995_2025.csv      # Team statistics
│       └── players_historical_1995_2024.csv  # Historical view
│
├── scripts/
│   └── enrich_player.py       # Main pipeline (automated)
│
└── docs/                       # Documentation
    ├── DATA_SOURCES.md        # Data provenance
    ├── POWERBI_GUIDE.md       # Power BI integration
    └── CONTRIBUTING.md        # Development guide
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone <your-repo-url>
cd datalake

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Player Dataset

```bash
# Automatically fetch FBref + Transfermarkt data
python scripts/enrich_player.py "Cristiano Ronaldo"
python scripts/enrich_player.py "Lionel Messi"
python scripts/enrich_player.py "Kaká"
```

**Output:** `datalake/processed/enriched/{player}_enriched.csv`

### 3. Power BI Integration

1. Open Power BI Desktop
2. **Get Data → Text/CSV**
3. Select `datalake/processed/enriched/cristiano_ronaldo_enriched.csv`
4. **Transform Data** → Set column types:
   - `Performance_Gls`: Whole Number
   - `Per_90_Minutes_Gls`: Decimal Number
   - `season_period`: Text
5. **Close & Apply**

See [docs/POWERBI_GUIDE.md](docs/POWERBI_GUIDE.md) for advanced DAX measures.

## 📈 Dataset Schema

### Enriched Player Dataset (53 columns)

| Column | Type | Description |
|--------|------|-------------|
| `season_period` | Text | Format: "2023-2024" |
| `age` | Number | Player age during season |
| `team` | Text | Club name |
| `league` | Text | Format: "ENG-Premier League" |
| `competition_type` | Text | "Domestic League" / "International Competition" |
| `is_domestic_league` | Boolean | Filter for league-only stats |
| `Performance_Gls` | Number | Goals scored |
| `Performance_Ast` | Number | Assists |
| `Playing_Time_Min` | Number | Minutes played |
| `Per_90_Minutes_Gls` | Decimal | Goals per 90 minutes |
| `Per_90_Minutes_Ast` | Decimal | Assists per 90 minutes |
| `meta_transfermarkt_url` | Text | Player Transfermarkt profile |
| `meta_honors` | Text | Career achievements |

**Full schema:** See [docs/DATABASE_VARIABLES_GUIDE.md](docs/DATABASE_VARIABLES_GUIDE.md)

## 🔧 Main Pipeline: `enrich_player.py`

**Automated workflow:**

1. ✅ **Search** player in FBref database (19,795 players)
2. ✅ **Classify** competitions (domestic vs international)
3. ✅ **Fetch** missing leagues from Transfermarkt (Saudi Pro League, MLS, etc.)
4. ✅ **Enrich** with metadata (birthplace, honors, position)
5. ✅ **Format** for Power BI (correct types, rounded decimals)
6. ✅ **Save** to `enriched/` folder

**Example output:**
```
============================================================
📊 RESUMO: Cristiano Ronaldo
============================================================

📈 Total de registros: 35
   - Ligas domésticas: 24
   - Competições internacionais: 11

⚽ Estatísticas (ligas domésticas):
   - Total de gols: 565
   - Total de assistências: 150
   - Gols por 90 min: 0.89

📅 Período: 2003-2004 até 2025-2026
```

## 📊 Use Cases

### 1. Career Trajectory Analysis
Compare goals per 90 minutes across different leagues and career phases.

### 2. League Difficulty Comparison
Analyze performance metrics (xG, npxG) across Premier League, La Liga, Serie A, etc.

### 3. International vs Club Performance
Filter with `is_domestic_league` to separate club and country statistics.

### 4. Historical Trends
Track evolution of playing style using progression metrics (PrgC, PrgP, PrgR).

## 📂 Data Sources

| Source | Coverage | Usage |
|--------|----------|-------|
| **FBref** | 1995-2025, Top 5 leagues + internationals | Primary source (90% of data) |
| **Transfermarkt** | 2000-2025, All leagues worldwide | Supplemental (Saudi, MLS, Brazil) |

**Data freshness:** Updated manually. FBref data frozen at collection date.

See [docs/DATA_SOURCES.md](docs/DATA_SOURCES.md) for detailed provenance.

## 🛠️ Development

### Project Structure

- `scripts/enrich_player.py` - **Main pipeline** (use this)
- `scripts/generate_players_teams_historical.py` - Historical aggregation
- `scripts/deduplicate_player_data.py` - Data cleaning utilities
- `datalake/processed/players_complete_1995_2025.csv` - **Master database**

### Adding New Players

```python
# Automatic (recommended)
python scripts/enrich_player.py "Neymar"

# Manual (if needed)
# 1. Ensure player exists in players_complete_1995_2025.csv
# 2. Create metadata file: datalake/raw/metadata/neymar_metadata.json
# 3. Run enrichment pipeline
```

### Contributing

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for:
- Code style guidelines
- Testing procedures
- Pull request process

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- **FBref** - Primary football statistics source
- **Transfermarkt** - Transfer data and supplemental league coverage
- **Sports Reference** - Data infrastructure

## 📧 Contact

Questions or suggestions? Open an issue or reach out via LinkedIn.

---

**Built with:** Python 3.11 | Pandas 2.0 | BeautifulSoup4 | Power BI

⭐ Star this repo if you find it useful!
