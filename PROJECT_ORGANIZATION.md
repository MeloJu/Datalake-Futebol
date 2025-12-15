# 📁 Project Organization Guide

> **Professional data engineering project structure for GitHub portfolio**

---

## 🎯 Project Overview

**Football Analytics Data Lake** - AI-powered scouting system demonstrating:
- Data engineering (ETL, web scraping)
- Machine learning (clustering, vectorization)
- Business intelligence (Power BI integration)
- Software engineering (modular architecture)

**Target Level:** Pleno/Junior Data Engineer/ML Engineer  
**Key Skills:** Python, ML, Data Pipelines, Documentation

---

## 📂 Directory Structure

```
datalake/                           # Project root
│
├── 📄 README.md                    # Main project documentation
├── 📄 CHANGELOG.md                 # Version history
├── 📄 LICENSE                      # MIT License
├── 📄 requirements.txt             # Python dependencies
├── 📄 .gitignore                   # Git exclusions
├── 📄 .env                         # Environment variables (not in repo)
│
├── 📂 datalake/                    # Data storage
│   ├── 📂 raw/                     # Source data (unprocessed)
│   │   ├── matches/               # Match JSON files
│   │   ├── metadata/              # Player biographical data
│   │   ├── squads/                # Team rosters (16 teams)
│   │   └── transfermarkt/         # Transfer market data
│   │
│   └── 📂 processed/               # Cleaned/normalized data
│       ├── players_complete_1995_2025.csv    # 86,930 records
│       ├── teams_complete_1995_2025.csv      # 8,450+ records
│       ├── squads_complete.csv               # 553 records
│       └── enriched/              # Individual enriched datasets
│
├── 📂 scripts/                     # Python processing scripts
│   ├── clusterization             # ⭐ AI Football Scout (main)
│   ├── fetch_team_squads.py       # Transfermarkt scraper
│   ├── generate_squads_database.py # Batch squad processor
│   ├── enrich_player.py           # Player data enrichment
│   └── [10+ utility scripts]
│
├── 📂 notebooks/                   # Interactive analysis
│   └── ai_football_scout.ipynb    # ML clustering notebook
│
└── 📂 docs/                        # Documentation
    ├── ARCHITECTURE.md            # System design
    ├── DATA_SOURCES.md            # Data provenance
    ├── POWERBI_GUIDE.md           # BI integration
    ├── CONTRIBUTING.md            # Development workflow
    └── archive/                   # Historical docs
```

---

## 🚀 Key Scripts

### 🎯 Main Script: `scripts/clusterization`
**Purpose:** AI Football Scout - ML-based transfer recommendations  
**Features:**
- K-Means clustering (grid search 2-15)
- Player vectorization (36 features)
- Team tactical profiling
- Cosine similarity matching

**Usage:**
```bash
python scripts/clusterization
```

**Outputs:**
- `players_clustered.csv` - Player profiles with cluster assignments
- `transfer_recommendations.csv` - Top 7 matches per team
- `clusters_metadata.csv` - Cluster characteristics

---

### 📥 Data Collection: `scripts/fetch_team_squads.py`
**Purpose:** Scrape team rosters from Transfermarkt  
**Features:**
- BeautifulSoup4 HTML parsing
- Rate limiting (2-3s delays)
- Market value extraction

**Usage:**
```bash
python scripts/fetch_team_squads.py --team "Manchester City" --season 2025
```

---

### 🔄 Batch Processing: `scripts/generate_squads_database.py`
**Purpose:** Generate squad database for multiple leagues  
**Coverage:** 5 major European leagues (16 teams)

**Usage:**
```bash
python scripts/generate_squads_database.py --leagues "all" --seasons "2025"
```

---

## 📊 Data Files

| File | Records | Size | Description |
|------|---------|------|-------------|
| `players_complete_1995_2025.csv` | 86,930 | ~50MB | Full player statistics |
| `teams_complete_1995_2025.csv` | 8,450+ | ~5MB | Team statistics |
| `squads_complete.csv` | 553 | <1MB | Current rosters (2025-26) |
| `players_clustered.csv` | 86,930 | ~55MB | ML clustering output |
| `transfer_recommendations.csv` | ~100 | <1MB | Top matches per team |

---

## 📖 Documentation

### Essential Docs (docs/)
1. **ARCHITECTURE.md** - System design and data flow
2. **DATA_SOURCES.md** - FBref, Transfermarkt details
3. **POWERBI_GUIDE.md** - Dashboard integration steps
4. **CONTRIBUTING.md** - Development workflow

### Archived Docs (docs/archive/)
- Historical guides (Portuguese versions, Git commands, etc.)
- Not essential for project understanding

---

## 🛠️ Tech Stack

**Data Processing:**
- Python 3.13.1
- Pandas 2.0+
- NumPy

**Machine Learning:**
- scikit-learn (KMeans, StandardScaler, cosine_similarity)
- Grid search hyperparameter tuning
- Silhouette score optimization

**Web Scraping:**
- BeautifulSoup4
- Requests
- lxml parser

**Visualization:**
- Jupyter Notebook
- Power BI Desktop

---

## 🎓 Skills Showcase

### Data Engineering
✅ ETL pipeline design  
✅ Web scraping with rate limiting  
✅ Data normalization and cleaning  
✅ CSV/JSON handling at scale

### Machine Learning
✅ Unsupervised learning (K-Means)  
✅ Feature engineering (36 features)  
✅ Hyperparameter tuning (grid search)  
✅ Vector similarity algorithms

### Software Engineering
✅ Modular architecture  
✅ Documentation (README, CHANGELOG, docstrings)  
✅ Version control (Git)  
✅ Virtual environments  
✅ Dependency management

### Business Intelligence
✅ Power BI data modeling  
✅ Dashboard-ready outputs  
✅ Relationship management  
✅ Data typing for BI tools

---

## 📋 Project Checklist

### ✅ Completed
- [x] Professional README with badges
- [x] Clean directory structure
- [x] Documentation consolidated (4 essential docs)
- [x] CHANGELOG created
- [x] .gitignore configured
- [x] Empty folders removed
- [x] Scripts organized
- [x] Jupyter notebook added

### 🎯 Ready for GitHub
- [x] No sensitive data (.env excluded)
- [x] No large binaries (CSVs gitignored or LFS)
- [x] Clear installation instructions
- [x] Working examples provided
- [x] License included (MIT)

---

## 🚀 Next Steps

### Before Publishing
1. ✅ Review README for typos
2. ✅ Test installation from scratch
3. ✅ Verify notebook runs end-to-end
4. ✅ Check all links work

### After Publishing
1. Add GitHub topics: `machine-learning`, `data-engineering`, `football-analytics`, `clustering`
2. Create releases for versions
3. Add GitHub Actions (optional)
4. Create example outputs folder
5. Add screenshots to README

---

## 📞 Contact

**Portfolio:** [Your website]  
**LinkedIn:** [Your profile]  
**Email:** [Your email]

---

<div align="center">
  <sub>Organized for professional GitHub showcase | Pleno/Junior level project</sub>
</div>
