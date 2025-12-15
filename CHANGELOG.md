# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] - 2025-12

### Added
- **AI Football Scout System**
  - K-Means clustering with grid search (2-15 clusters)
  - Player vectorization (36 statistical features)
  - Team vectorization (aggregated player vectors)
  - Cosine similarity transfer recommendations
  - Contextual scoring (40% vector + 60% tactical fit)
  
- **Squad Composition Database**
  - Transfermarkt scraper (`fetch_team_squads.py`)
  - Batch processor for multi-league scraping
  - 553 records across 16 top European teams (2025-26)
  - Coverage: Premier League, La Liga, Bundesliga, Serie A, Ligue 1

- **Data Pipeline**
  - Player statistics database (86,930 records, 1995-2025)
  - Team statistics database (8,450+ records)
  - Automated enrichment scripts
  - Data normalization and cleaning

- **Power BI Integration**
  - Normalized CSV exports
  - Proper data typing and relationships
  - Dashboard-ready outputs

- **Documentation**
  - Professional README with badges
  - Architecture documentation
  - Data sources guide
  - Power BI integration guide
  - Contribution guidelines

- **Interactive Notebook**
  - Jupyter notebook with 26 cells
  - Google Colab compatible
  - Step-by-step ML workflow

### Fixed
- Current club attribution (Bellingham now shows Real Madrid instead of Borussia Dortmund)
- Display all 16 teams in cluster balance (was showing only 5)
- Feature leakage in team clustering (separated style from production metrics)

### Changed
- Team vectorization uses squad composition instead of raw team stats
- Team clustering uses tactical features (possession, pressure) not production metrics
- Season updated to 2025-26 (current season)

### Technical
- Python 3.13.1
- Dependencies: pandas, beautifulsoup4, requests, lxml, scikit-learn, numpy
- ML: StandardScaler normalization, silhouette score optimization
- Rate limiting: 2-3s between scraping requests

---

## Future Roadmap

### Planned Features
- [ ] Match prediction model
- [ ] Real-time data updates
- [ ] API endpoints for recommendations
- [ ] Expanded tactical metrics (pressing intensity, buildup patterns)
- [ ] Player injury/form tracking
- [ ] Transfer value estimation

### Under Consideration
- [ ] Web dashboard (Streamlit/Dash)
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Unit tests coverage

---

**Legend:**
- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security improvements
