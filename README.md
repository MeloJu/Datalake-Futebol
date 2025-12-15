# ⚽ Football Analytics Data Lake

> **AI-powered football scouting system with clustering, vectorization, and transfer recommendations**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0+-green.svg)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Overview

Professional data lake and AI scouting system for football analytics. Integrates multiple data sources (FBref, Transfermarkt), applies machine learning clustering, and generates tactical transfer recommendations based on player-team compatibility.

### ✨ Key Features

- 🤖 **AI Football Scout** - K-Means clustering + cosine similarity for transfer recommendations
- 📊 **86,930 player records** (1995-2025) with 36+ statistical features  
- 🏆 **Squad composition database** - 16 top European teams (2025-26 season)
- 🎯 **Tactical profiling** - Players and teams clustered by playing style
- 📈 **Power BI ready** - Normalized CSVs with proper typing
- 🔄 **Automated pipelines** - Web scraping + data enrichment

---

## 🏗️ Project Structure

```
datalake/
├── datalake/
│   ├── raw/                    # Source data
│   │   ├── matches/           # Match JSON files (40+ games)
│   │   ├── metadata/          # Player biographical data
│   │   ├── squads/            # Team rosters (16 teams)
│   │   └── transfermarkt/     # Transfer market data
│   └── processed/
│       ├── players_complete_1995_2025.csv
│       ├── teams_complete_1995_2025.csv
│       ├── squads_complete.csv
│       └── enriched/          # Individual player datasets
│
├── scripts/
│   ├── clusterization                  # AI Scout (main)
│   ├── fetch_team_squads.py
│   ├── generate_squads_database.py
│   └── enrich_player_complete.py
│
├── notebooks/
│   └── ai_football_scout.ipynb        # Interactive ML
│
└── docs/
    ├── ARCHITECTURE.md
    ├── DATA_SOURCES.md
    └── POWERBI_GUIDE.md
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/yourusername/football-analytics-datalake.git
cd football-analytics-datalake

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run AI Football Scout

```bash
# Python script
python scripts/clusterization

# Jupyter Notebook (interactive)
jupyter notebook notebooks/ai_football_scout.ipynb
```

### 3. Generate Squad Data

```bash
# All 5 major leagues (2025-26)
python scripts/generate_squads_database.py --leagues "all" --seasons "2025"

# Single team
python scripts/fetch_team_squads.py --team "Manchester City" --season 2025
```

---

## 🤖 AI Football Scout

### How It Works

1. **Player Clustering** (K-Means)
   - 36 features: goals, assists, xG, progression, per-90 metrics
   - Grid search for optimal clusters (2-15 tested)
   - Silhouette score optimization
   - Result: 6-8 player profiles

2. **Team Vectorization**
   - Team vector = average of player vectors from squad
   - Captures tactical DNA of each team

3. **Transfer Recommendations**
   - Cosine similarity between player and team vectors
   - Contextual scoring: 40% vector + 60% tactical fit
   - Output: Top 7 compatible players per team

### Example Output

```
🎯 Top 5 Transfers for Real Madrid:

🟢 Bellingham    | CM  | 21y | Borussia Dortmund  | 0.8934
🟢 Haaland       | ST  | 24y | Manchester City    | 0.8821
🟡 Tchouameni    | DM  | 24y | Monaco             | 0.8165
```

---

## 📊 Datasets

| File | Records | Description |
|------|---------|-------------|
| `players_complete_1995_2025.csv` | 86,930 | Full player stats |
| `teams_complete_1995_2025.csv` | 8,450+ | Team stats |
| `squads_complete.csv` | 553 | Current rosters |
| `players_clustered.csv` | 86,930 | ML clustering |

---

## 📈 Power BI Integration

1. **Import CSVs** → Get Data → Text/CSV
2. **Create Relationships**:
   - `transfer_recommendations[player_cluster]` → `clusters_metadata[cluster_id]`
3. **Build Visuals**:
   - Scatter Plot (Age × Match Score)
   - Matrix (Top transfers per team)
   - Cluster Map (PCA 2D)

See [docs/POWERBI_GUIDE.md](docs/POWERBI_GUIDE.md) for details.

---

## 🛠️ Tech Stack

- **Data**: Pandas, NumPy
- **ML**: scikit-learn (KMeans, StandardScaler, cosine similarity)
- **Scraping**: BeautifulSoup4, Requests
- **Viz**: Jupyter, Power BI
- **Sources**: FBref, Transfermarkt

---

## 🎓 Skills Demonstrated

**Data Engineering:**
- ETL pipelines
- Web scraping with rate limiting
- Data normalization

**Machine Learning:**
- Unsupervised learning (K-Means)
- Grid search hyperparameter tuning
- Vector similarity
- Feature engineering (36 features)

**Software Engineering:**
- Modular architecture
- Documentation
- Version control

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

⭐ **Star this repo** if you found it helpful!

<div align="center">
  <sub>Built with ❤️ for football analytics</sub>
</div>
