# Kaká Career Storytelling Guide for Power BI

## Dataset Ready
✅ `datalake/processed/kaka_enriched.csv` (17 seasons, 48 columns)

## Power BI Import Steps

### 1. Load Data
- **Get Data** → **Text/CSV** → Select `kaka_enriched.csv`
- **Transform Data** (Power Query Editor):
  - Convert numeric columns to proper types (goals, assists, minutes, etc.)
  - Ensure `season_period` is text (e.g., "2003-2004")
  - Create calculated column `club_clean` = extract main club name from `team`

### 2. Data Model Enhancements

Create these measures in Power BI:

```DAX
Total Goals = SUM(kaka_enriched[Performance_Gls])
Total Assists = SUM(kaka_enriched[Performance_Ast])
Total Minutes = SUM(kaka_enriched[Playing_Time_Min])
Goals Per 90 = AVERAGE(kaka_enriched[Per_90_Minutes_Gls])
Assists Per 90 = AVERAGE(kaka_enriched[Per_90_Minutes_Ast])
Peak Season = IF([Total Goals] + [Total Assists] = MAXX(ALL(kaka_enriched), [Total Goals] + [Total Assists]), "⭐ Peak", "")
```

## Suggested Dashboard Structure

### Page 1: Career Overview
**Title**: "Kaká: The Elegant Playmaker (2001-2014)"

**Visuals**:
1. **Header Card (full width)**
   - Name: Kaká
   - Birth: 1982-04-22, Brasília, Brazil
   - Position: Attacking Midfield
   - Height: 1.86m, Left-footed

2. **Key Stats Cards (4 cards, side by side)**
   - Total Goals: [Total Goals]
   - Total Assists: [Total Assists]
   - Seasons: 17
   - Clubs: Milan, Real Madrid, Brazil NT

3. **Line Chart: Goals & Assists Over Time**
   - X-axis: `season_period`
   - Y-axis: `Performance_Gls` (line), `Performance_Ast` (line)
   - Legend: separate colors
   - Data labels on peaks (2007-08: 15 goals)

4. **Clustered Bar Chart: Career by Club**
   - Y-axis: `team` (or `club_clean`)
   - X-axis: Count of seasons
   - Add Goals + Assists as stacked bars

### Page 2: The Milan Era (2003-2009)
**Title**: "AC Milan Glory Years"

**Filters**: `team` contains "Milan"

**Visuals**:
1. **Table: Season-by-season stats**
   - Columns: Season, MP, Goals, Assists, Minutes
   - Conditional formatting: highlight 2007-08 peak season

2. **Donut Chart: Contribution Split**
   - Values: Goals vs Assists
   - Show percentage breakdown

3. **Card with Image** (if available)
   - Text: "2007: Ballon d'Or & Champions League Winner"
   - Highlight: `meta_honors` mentions

4. **Text Box Narrative**:
   ```
   "At AC Milan, Kaká reached the pinnacle of world football. 
   In 2007, he won the Ballon d'Or and led Milan to Champions League glory.
   His best season (2007-08): 15 goals and 10 assists in Serie A."
   ```

### Page 3: Real Madrid Chapter (2009-2013)
**Title**: "Galáctico Era at Real Madrid"

**Filters**: `team` contains "Real Madrid"

**Visuals**:
1. **Waterfall Chart: Minutes Played Decline**
   - X-axis: Season
   - Y-axis: `Playing_Time_Min`
   - Show injury impact (2010-11: only 802 minutes)

2. **Area Chart: Performance Metrics**
   - X-axis: Season
   - Y-axis: `Per_90_Minutes_Gls` and `Per_90_Minutes_Ast`
   - Highlight 2010-11 spike (0.79 goals/90)

3. **Text Box: The Injury Story**
   ```
   "Despite winning La Liga in 2011-12, Kaká's Madrid stint was marred by injuries.
   After a promising start (8 goals in 2009-10), recurring knee problems limited his impact."
   ```

### Page 4: International Legacy
**Title**: "Brazil's World Cup Winner"

**Filters**: `league` = "INT-World Cup"

**Visuals**:
1. **Map Visual** (if coordinates available)
   - Show tournament locations: 2002 (Japan/Korea), 2006 (Germany), 2010 (South Africa)

2. **Cards**:
   - 2002: World Cup Champion ⭐
   - 2006: 1 goal in 5 matches
   - 2010: 3 red cards (including 1 in tournament)

3. **Text Box: World Cup Journey**
   ```
   "Kaká was part of Brazil's 2002 World Cup winning squad at age 20.
   By 2006, he was a key player. In 2010, despite high expectations,
   Brazil exited in the quarterfinals."
   ```

### Page 5: Honors & Legacy
**Title**: "Awards & Achievements"

**Visuals**:
1. **Ribbon Chart or List Visual: All Honors**
   - Source: `meta_honors` (split by semicolon)
   - Group by type: International, Club, Individual

2. **Timeline Visual** (use custom visual from AppSource)
   - Key milestones:
     - 2001: Copa Libertadores
     - 2002: World Cup
     - 2004: Serie A
     - 2007: Champions League + Ballon d'Or
     - 2012: La Liga

3. **Quote Card**:
   ```
   "One of the best attacking midfielders of his generation.
   Known for his elegance, vision, and ability to score crucial goals."
   ```

## Color Palette Suggestions
- **Milan Red**: #FB090B
- **Real Madrid White/Gold**: #FEBE10
- **Brazil Yellow**: #FFCD00
- **Background**: Dark theme (#1E1E1E) for elegance

## Interactive Elements
- **Slicer**: Season filter (dropdown)
- **Slicer**: Club filter (buttons)
- **Tooltip**: On goals/assists charts, show full season stats
- **Drill-through**: From any season → detailed season breakdown page

## Export & Sharing
1. **Publish to Power BI Service**
2. **Create shareable link** or embed in website
3. **Export to PDF** for presentation

---

## Quick Usage Command

To generate enriched CSV for any player:

```bash
# 1. Create metadata JSON (playerName_metadata.json)
# 2. Run enrichment:
python scripts/enrich_player_manual.py "Player Name" playerName_metadata.json

# 3. Import to Power BI:
#    File: datalake/processed/playername_enriched.csv
```

## Example for Other Players

```bash
# Cristiano Ronaldo
python scripts/enrich_player_manual.py "Cristiano Ronaldo" cr7_metadata.json

# Ronaldinho
python scripts/enrich_player_manual.py "Ronaldinho" ronaldinho_metadata.json
```

Create similar JSON files following `kaka_metadata.json` template.
