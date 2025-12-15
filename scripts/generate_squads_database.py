"""
Generate Squad Database - Batch Processing
===========================================

Script to scrape team squads from multiple leagues and seasons,
creating a comprehensive squad composition database.

Usage:
    python scripts/generate_squads_database.py --seasons "2021,2022,2023,2024"
    python scripts/generate_squads_database.py --leagues "premier-league,la-liga" --seasons "2023"
"""

import sys
import pandas as pd
from pathlib import Path
import time

# Import the fetch_team_squads functions
sys.path.append('scripts')
import fetch_team_squads as fetcher

# Configuration
LEAGUES = [
    'premier-league',
    'la-liga', 
    'bundesliga',
    'serie-a',
    'ligue-1'
]

SEASONS = [2021, 2022, 2023, 2024]  # 2021-22, 2022-23, 2023-24, 2024-25

# Top teams per league (for faster targeted scraping)
TOP_TEAMS = {
    'premier-league': [
        ('Manchester City', 281),
        ('Arsenal', 11),
        ('Liverpool', 31),
    ],
    'la-liga': [
        ('Real Madrid', 418),
        ('Barcelona', 131),
        ('Atlético Madrid', 13),
    ],
    'bundesliga': [
        ('Bayern Munich', 27),
        ('Borussia Dortmund', 16),
        ('RB Leipzig', 23826),
    ],
    'serie-a': [
        ('Inter', 46),
        ('Juventus', 506),
        ('AC Milan', 5),
    ],
    'ligue-1': [
        ('PSG', 583),
        ('Marseille', 244),
        ('Monaco', 162),
    ]
}


def scrape_team_squad(team_name, team_id, season, output_dir):
    """
    Scrape single team squad using direct function call
    """
    print(f"  🔄 {team_name} ({season}-{season+1})...")
    
    try:
        # Get squad data
        squad_df = fetcher.get_team_squad(team_id, season, team_name)
        
        if squad_df.empty:
            print(f"     ❌ No data returned")
            return False
        
        # Clean market values
        squad_df['market_value_millions'] = squad_df['market_value'].apply(fetcher.clean_market_value)
        
        # Save individual file
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        filename = f"{team_name.lower().replace(' ', '_')}_{season}_squad.csv"
        file_path = output_path / filename
        
        squad_df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"     ✓ Success ({len(squad_df)} players)")
        return True
        
    except Exception as e:
        print(f"     ❌ Error: {str(e)[:100]}")
        return False


def scrape_league_top_teams(league, seasons, output_dir):
    """
    Scrape top teams from a league across multiple seasons
    """
    if league not in TOP_TEAMS:
        print(f"❌ League '{league}' not configured")
        return
    
    teams = TOP_TEAMS[league]
    total = len(teams) * len(seasons)
    current = 0
    
    print(f"\n{'='*70}")
    print(f"🏆 {league.upper().replace('-', ' ')}")
    print(f"   Teams: {len(teams)} | Seasons: {len(seasons)} | Total scrapes: {total}")
    print(f"{'='*70}\n")
    
    for season in seasons:
        print(f"\n📅 Season {season}-{season+1}")
        print(f"{'─'*70}")
        
        for team_name, team_id in teams:
            current += 1
            print(f"[{current}/{total}]", end=" ")
            success = scrape_team_squad(team_name, team_id, season, output_dir)
            
            if success:
                time.sleep(3)  # Rate limiting: 3 seconds between requests
            else:
                time.sleep(1)


def consolidate_squads(raw_dir, output_file):
    """
    Consolidate all individual squad CSV files into one master database
    """
    print(f"\n{'='*70}")
    print(f"📦 Consolidating squad data...")
    print(f"{'='*70}\n")
    
    raw_path = Path(raw_dir)
    csv_files = list(raw_path.glob("*_squad.csv"))
    
    if not csv_files:
        print("❌ No squad files found to consolidate")
        return
    
    print(f"   Found {len(csv_files)} squad files")
    
    all_squads = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8')
            all_squads.append(df)
        except Exception as e:
            print(f"   ⚠️  Error reading {csv_file.name}: {e}")
    
    if all_squads:
        final_df = pd.concat(all_squads, ignore_index=True)
        
        # Add league information based on team
        league_mapping = {}
        for league, teams in TOP_TEAMS.items():
            for team_name, _ in teams:
                league_mapping[team_name] = league.replace('-', ' ').title()
        
        final_df['league'] = final_df['team'].map(league_mapping)
        
        # Sort by league, team, season
        final_df = final_df.sort_values(['league', 'team', 'season_year', 'player_name'])
        
        # Save consolidated file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_df.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"\n✅ Consolidated database saved: {output_path}")
        print(f"📊 Statistics:")
        print(f"   • Total records: {len(final_df):,}")
        print(f"   • Unique players: {final_df['player_name'].nunique():,}")
        print(f"   • Teams: {final_df['team'].nunique()}")
        print(f"   • Seasons: {final_df['season'].nunique()}")
        print(f"   • Leagues: {final_df['league'].nunique()}")
        print(f"\n📈 Records per league:")
        print(final_df['league'].value_counts().to_string())
        
    else:
        print("❌ No data to consolidate")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate comprehensive squad database')
    parser.add_argument('--leagues', type=str, default='all', 
                       help='Comma-separated leagues or "all" (default: all)')
    parser.add_argument('--seasons', type=str, default='2023,2024',
                       help='Comma-separated season years (default: 2023,2024)')
    parser.add_argument('--raw-dir', type=str, default='datalake/raw/squads',
                       help='Directory for individual squad files')
    parser.add_argument('--output', type=str, default='datalake/processed/squads_complete.csv',
                       help='Output file for consolidated database')
    
    args = parser.parse_args()
    
    # Parse seasons
    seasons = [int(s.strip()) for s in args.seasons.split(',')]
    
    # Parse leagues
    if args.leagues.lower() == 'all':
        leagues = LEAGUES
    else:
        leagues = [l.strip() for l in args.leagues.split(',')]
    
    print(f"\n{'='*70}")
    print(f"🚀 SQUAD DATABASE GENERATOR")
    print(f"{'='*70}")
    print(f"📅 Seasons: {', '.join(f'{s}-{s+1}' for s in seasons)}")
    print(f"🏆 Leagues: {', '.join(leagues)}")
    print(f"📁 Output: {args.output}")
    print(f"{'='*70}\n")
    
    start_time = time.time()
    
    # Scrape each league
    for league in leagues:
        scrape_league_top_teams(league, seasons, args.raw_dir)
        time.sleep(5)  # Pause between leagues
    
    # Consolidate all data
    consolidate_squads(args.raw_dir, args.output)
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Total time: {elapsed/60:.1f} minutes")
    print(f"✅ Done!\n")


if __name__ == "__main__":
    main()
