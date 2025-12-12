"""
Complete automated player enrichment pipeline.

This script:
1. Searches for player in local database
2. Extracts their career data
3. Finds player ID on Transfermarkt
4. Scrapes missing seasons from Transfermarkt
5. Merges all data with metadata
6. Generates enriched CSV ready for Power BI

Usage:
    python scripts/enrich_player_complete.py "Player Name"
    
Example:
    python scripts/enrich_player_complete.py "Cristiano Ronaldo"
"""

import sys
import os
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Paths
DB_PATH = 'datalake/processed/players_complete_1995_2025.csv'
ENRICHED_DIR = 'datalake/processed/enriched'
METADATA_DIR = 'datalake/raw/metadata'
TRANSFERMARKT_DIR = 'datalake/raw/transfermarkt'

os.makedirs(ENRICHED_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(TRANSFERMARKT_DIR, exist_ok=True)


def search_player_in_database(player_name, team_filter=None):
    """Search for player in local database."""
    print(f'\n🔍 Searching for "{player_name}" in local database...')
    
    try:
        df = pd.read_csv(DB_PATH, low_memory=False, dtype={'season': str})
        
        # Exact match first
        mask = df['player'].astype(str).str.lower() == player_name.lower()
        result = df[mask].copy()
        
        # If no exact match, try contains
        if len(result) == 0:
            mask = df['player'].astype(str).str.contains(player_name, case=False, na=False, regex=False)
            result = df[mask].copy()
        
        if len(result) == 0:
            print(f'❌ Player "{player_name}" not found in database')
            return None, None
        
        # Get unique player names (in case multiple players match)
        unique_players = result['player'].unique()
        
        if len(unique_players) > 1:
            print(f'\n⚠️ Multiple players found:')
            for i, p in enumerate(unique_players, 1):
                teams = result[result['player'] == p]['team'].unique()[:3]
                nation = result[result['player'] == p]['nation'].iloc[0] if 'nation' in result.columns else 'N/A'
                print(f'   {i}. {p} ({nation}) - played for: {", ".join(teams)}')
            
            choice = input(f'\nSelect player (1-{len(unique_players)}), or enter teams to filter (e.g., "Milan,Real Madrid"): ').strip()
            
            # Check if user entered team filter
            if ',' in choice or (choice and not choice.isdigit()):
                team_filter = [t.strip() for t in choice.split(',')]
                print(f'   Filtering by teams: {team_filter}')
                result = result[result['team'].isin(team_filter)]
                selected_player = result['player'].iloc[0] if len(result) > 0 else None
            else:
                try:
                    idx = int(choice) - 1
                    selected_player = unique_players[idx]
                    result = result[result['player'] == selected_player].copy()
                except:
                    print('❌ Invalid selection')
                    return None, None
        else:
            selected_player = unique_players[0]
        
        if len(result) == 0:
            print('❌ No data after filtering')
            return None, None
        
        teams = result['team'].unique()
        seasons = result['season'].unique()
        
        print(f'✅ Found: {selected_player}')
        print(f'   Seasons in database: {len(result)}')
        print(f'   Teams: {", ".join(teams[:5])}{"..." if len(teams) > 5 else ""}')
        
        return selected_player, result
        
    except Exception as e:
        print(f'❌ Error reading database: {e}')
        return None, None


def search_transfermarkt_id(player_name):
    """Search for player ID on Transfermarkt."""
    print(f'\n🌐 Searching Transfermarkt for "{player_name}"...')
    
    # Clean name for URL
    search_name = player_name.replace(' ', '+')
    url = f'https://www.transfermarkt.com.br/schnellsuche/ergebnis/schnellsuche?query={search_name}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find player links
        links = soup.find_all('a', href=True)
        player_links = []
        
        for link in links:
            href = link.get('href', '')
            if '/profil/spieler/' in href:
                text = link.text.strip()
                if text and len(text) > 0:
                    player_id = href.split('/')[-1]
                    player_links.append((text, player_id, href))
        
        # Remove duplicates
        seen = set()
        unique_links = []
        for text, pid, href in player_links:
            if pid not in seen:
                seen.add(pid)
                unique_links.append((text, pid, href))
        
        if not unique_links:
            print('❌ No players found on Transfermarkt')
            print('   Try entering ID manually')
            return None
        
        if len(unique_links) == 1:
            selected_name, selected_id, _ = unique_links[0]
            print(f'✅ Found: {selected_name} (ID: {selected_id})')
            return selected_id
        
        # Multiple results - let user choose
        print(f'\n⚠️ Multiple results found:')
        for i, (name, pid, _) in enumerate(unique_links[:10], 1):
            print(f'   {i}. {name} (ID: {pid})')
        
        choice = input(f'\nSelect player (1-{min(10, len(unique_links))}), or enter ID manually: ').strip()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(unique_links):
                selected_name, selected_id, _ = unique_links[idx]
                print(f'✅ Selected: {selected_name} (ID: {selected_id})')
                return selected_id
        except:
            # Assume user entered ID manually
            if choice.isdigit():
                print(f'✅ Using manual ID: {choice}')
                return choice
        
        print('❌ Invalid selection')
        return None
        
    except Exception as e:
        print(f'❌ Error searching Transfermarkt: {e}')
        return None


def fetch_transfermarkt_seasons(player_id, player_name):
    """Fetch all seasons from Transfermarkt."""
    print(f'\n📥 Fetching Transfermarkt data for ID {player_id}...')
    
    url_name = player_name.lower().replace('á', 'a').replace('é', 'e').replace(' ', '-')
    url = f'https://www.transfermarkt.com.br/{url_name}/leistungsdatendetails/spieler/{player_id}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        tables = soup.find_all('table', {'class': 'items'})
        
        if not tables:
            print('❌ No data table found')
            return None
        
        seasons_data = []
        table = tables[0]
        rows = table.find_all('tr', {'class': ['odd', 'even']})
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 5:
                continue
            
            try:
                season_text = cells[0].get_text(strip=True)
                
                comp_cell = cells[1]
                comp_img = comp_cell.find('img')
                league = comp_img.get('title', '') if comp_img else comp_cell.get_text(strip=True)
                
                team_text = cells[2].get_text(strip=True)
                if not team_text or team_text.lower() in ['club', 'total', '']:
                    continue
                
                apps = cells[4].get_text(strip=True) if len(cells) > 4 else '0'
                goals = cells[5].get_text(strip=True) if len(cells) > 5 else '0'
                assists = cells[6].get_text(strip=True) if len(cells) > 6 else '0'
                
                apps = apps if apps and apps != '-' else '0'
                goals = goals if goals and goals != '-' else '0'
                assists = assists if assists and assists != '-' else '0'
                
                if 'total' in season_text.lower():
                    continue
                
                seasons_data.append({
                    'season': season_text,
                    'team': team_text,
                    'league': league,
                    'appearances': apps,
                    'goals': goals,
                    'assists': assists
                })
                
            except Exception as e:
                continue
        
        if not seasons_data:
            print('❌ No season data extracted')
            return None
        
        df = pd.DataFrame(seasons_data)
        print(f'✅ Extracted {len(df)} seasons from Transfermarkt')
        
        return df
        
    except Exception as e:
        print(f'❌ Error fetching Transfermarkt: {e}')
        return None


def compare_data_sources(local_df, transfermarkt_df, player_name):
    """Compare local and Transfermarkt data to find missing seasons."""
    print(f'\n📊 Comparing data sources...')
    
    # Get local seasons
    local_seasons = set(local_df['season'].astype(str).unique())
    local_teams = local_df['team'].unique()
    
    print(f'   Local database: {len(local_seasons)} seasons')
    print(f'   Teams: {", ".join(local_teams[:5])}')
    
    # Identify missing leagues
    print(f'   Transfermarkt: {len(transfermarkt_df)} rows (all competitions)')
    
    # Filter Transfermarkt to only league matches (exclude cups)
    cup_keywords = ['Copa', 'Cup', 'Supercopa', 'Sul-Americana', 'Open', 'Liga dos Campeões', 
                    'Champions', 'UEFA', 'Mundial', 'Intercontinental']
    
    tm_leagues_only = transfermarkt_df.copy()
    for keyword in cup_keywords:
        tm_leagues_only = tm_leagues_only[~tm_leagues_only['league'].str.contains(keyword, case=False, na=False)]
    
    print(f'   Transfermarkt leagues only: {len(tm_leagues_only)} seasons')
    
    # Show leagues in Transfermarkt but not in local
    tm_leagues = set(tm_leagues_only['league'].unique())
    local_leagues = set(local_df['league'].unique())
    missing_leagues = tm_leagues - local_leagues
    
    if missing_leagues:
        print(f'\n   ⚠️ Leagues in Transfermarkt but NOT in local database:')
        for league in missing_leagues:
            seasons_count = len(tm_leagues_only[tm_leagues_only['league'] == league])
            print(f'      - {league} ({seasons_count} seasons)')
    
    # Filter missing seasons
    missing = tm_leagues_only[tm_leagues_only['league'].isin(missing_leagues)]
    
    if len(missing) > 0:
        print(f'\n   ✅ Found {len(missing)} missing seasons to add:')
        for _, row in missing.iterrows():
            print(f'      {row["season"]:10} - {row["league"]:40} - {row["goals"]:2} goals, {row["assists"]:2} assists')
    else:
        print(f'\n   ✅ No missing seasons - local database is complete!')
    
    return missing


def create_metadata_template(player_name):
    """Create metadata JSON template for manual completion."""
    safe_name = player_name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e')
    metadata_path = os.path.join(METADATA_DIR, f'{safe_name}_metadata.json')
    
    if os.path.exists(metadata_path):
        print(f'\n📝 Metadata file already exists: {metadata_path}')
        return metadata_path
    
    template = {
        "date_of_birth": "",
        "place_of_birth": "",
        "height": "",
        "nationality": "",
        "position_detail": "",
        "foot": "",
        "honors": [],
        "transfermarkt_url": "",
        "notes": ""
    }
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f'\n📝 Created metadata template: {metadata_path}')
    print(f'   Please fill in player information and re-run this script')
    
    return metadata_path


def convert_season_code(season_text):
    """
    Convert Transfermarkt season format to FBref format.
    Examples: '2017' → '1617', '13/14' → '1314', '2002' → '0102'
    """
    import re
    
    # Format: 13/14 or 13-14
    match = re.match(r'^(\d{2})[/-](\d{2})$', season_text)
    if match:
        return match.group(1) + match.group(2)
    
    # Format: 2017 (single year - assume season spans to next year)
    match = re.match(r'^(\d{4})$', season_text)
    if match:
        year = int(match.group(1))
        # Assume it's the first year of season
        next_year = year + 1
        return f'{str(year)[-2:]}{str(next_year)[-2:]}'
    
    return season_text


def convert_transfermarkt_to_fbref_format(tm_df, player_name, nation=''):
    """
    Convert Transfermarkt data to FBref schema format.
    
    Args:
        tm_df: DataFrame with Transfermarkt data
        player_name: Player name
        nation: Player's nation code (e.g., 'POR', 'BRA')
    
    Returns:
        DataFrame in FBref format
    """
    print(f'\n🔄 Converting Transfermarkt data to FBref format...')
    
    converted_rows = []
    
    for _, row in tm_df.iterrows():
        # Convert season code
        season_code = convert_season_code(row['season'])
        
        # Determine league code
        league_name = row['league']
        if 'LaLiga' in league_name or 'La Liga' in league_name:
            league = 'ESP-La Liga'
        elif 'Serie A' in league_name and 'Brasileiro' not in league_name:
            league = 'ITA-Serie A'
        elif 'Premier League' in league_name:
            league = 'ENG-Premier League'
        elif 'Bundesliga' in league_name:
            league = 'GER-Bundesliga'
        elif 'Ligue 1' in league_name:
            league = 'FRA-Ligue 1'
        elif 'Major League Soccer' in league_name or 'MLS' in league_name:
            league = 'USA-MLS'
        elif 'Brasileiro' in league_name or 'Série A' in league_name:
            league = 'BRA-Serie A'
        elif 'Liga Portugal' in league_name:
            league = 'POR-Primeira Liga'
        elif 'Saudi Pro League' in league_name:
            league = 'SAU-Pro League'
        else:
            league = league_name
        
        # Calculate season_period
        try:
            year1 = int(season_code[:2])
            year2 = int(season_code[2:])
            
            # Handle century
            if year1 >= 90:
                full_year1 = 1900 + year1
            else:
                full_year1 = 2000 + year1
            
            if year2 <= year1:
                full_year2 = full_year1 + 1
            else:
                if year2 >= 90:
                    full_year2 = 1900 + year2
                else:
                    full_year2 = 2000 + year2
            
            season_period = f'{full_year1}-{full_year2}'
        except:
            season_period = season_code
        
        # Parse goals and assists (handle numeric conversion)
        try:
            goals = float(row['goals']) if row['goals'] and row['goals'] != '-' else 0.0
        except:
            goals = 0.0
        
        try:
            assists = float(row['assists']) if row['assists'] and row['assists'] != '-' else 0.0
        except:
            assists = 0.0
        
        try:
            appearances = int(row['appearances']) if row['appearances'] and row['appearances'] != '-' else 0
        except:
            appearances = 0
        
        # Estimate minutes (avg 90 min per appearance)
        minutes = appearances * 90
        mins_90s = round(minutes / 90, 1)
        
        # Calculate per-90 stats
        gls_per_90 = round(goals / mins_90s, 2) if mins_90s > 0 else 0.0
        ast_per_90 = round(assists / mins_90s, 2) if mins_90s > 0 else 0.0
        ga_per_90 = round((goals + assists) / mins_90s, 2) if mins_90s > 0 else 0.0
        
        converted_row = {
            'league': league,
            'season': season_code,
            'team': row['team'],
            'player': player_name,
            'nation': nation,
            'pos': 'FW',  # Default, adjust if needed
            'age': None,
            'Club': None,
            'Playing_Time_born': None,
            'Playing_Time_MP': appearances,
            'Playing_Time_Starts': appearances,  # Assume all starts
            'Playing_Time_Min': minutes,
            'Playing_Time_90s': mins_90s,
            'Performance_Gls': goals,
            'Performance_Ast': assists,
            'Performance_G+A': goals + assists,
            'Performance_G-PK': goals,  # Assume no penalties
            'Performance_PK': 0,
            'Performance_PKatt': 0,
            'Performance_CrdY': 0,
            'Performance_CrdR': 0,
            'Expected_xG': None,
            'Expected_npxG': None,
            'Expected_xAG': None,
            'Expected_npxG+xAG': None,
            'Progression_PrgC': None,
            'Progression_PrgP': None,
            'Progression_PrgR': None,
            'Per_90_Minutes_Gls': gls_per_90,
            'Per_90_Minutes_Ast': ast_per_90,
            'Per_90_Minutes_G+A': ga_per_90,
            'Per_90_Minutes_G-PK': gls_per_90,
            'Per_90_Minutes_G+A-PK': ga_per_90,
            'Per_90_Minutes_xG': None,
            'Per_90_Minutes_xAG': None,
            'Per_90_Minutes_xG+xAG': None,
            'Per_90_Minutes_npxG': None,
            'Per_90_Minutes_npxG+xAG': None,
            'season_period': season_period
        }
        
        converted_rows.append(converted_row)
    
    converted_df = pd.DataFrame(converted_rows)
    print(f'   ✅ Converted {len(converted_df)} seasons')
    
    return converted_df


def enrich_and_save(player_name, local_df, missing_df=None, metadata_path=None):
    """Combine local data, missing seasons, and metadata into enriched CSV."""
    print(f'\n🔧 Creating enriched dataset...')
    
    # Load metadata if provided
    metadata = {}
    if metadata_path and os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            print(f'   ✅ Loaded metadata from {metadata_path}')
        except Exception as e:
            print(f'   ⚠️ Could not load metadata: {e}')
    
    # Combine local and missing
    if missing_df is not None and len(missing_df) > 0:
        print(f'\n   🔄 Converting and merging {len(missing_df)} missing seasons...')
        
        # Get nation from local data
        nation = local_df['nation'].iloc[0] if 'nation' in local_df.columns and len(local_df) > 0 else ''
        
        # Convert Transfermarkt format to FBref format
        converted_missing = convert_transfermarkt_to_fbref_format(missing_df, player_name, nation)
        
        # Combine with local data
        combined = pd.concat([local_df, converted_missing], ignore_index=True)
        
        # Remove duplicates by season + team + league
        before = len(combined)
        combined = combined.drop_duplicates(subset=['season', 'team', 'league'], keep='first')
        after = len(combined)
        
        if before != after:
            print(f'   ℹ️ Removed {before - after} duplicate seasons')
        
        # Sort by season
        combined = combined.sort_values('season')
        
        print(f'   ✅ Combined dataset: {len(combined)} total seasons')
    else:
        combined = local_df.copy()
        print(f'   ℹ️ No missing seasons to add')
    
    # Add metadata columns
    if metadata:
        combined['meta_date_of_birth'] = metadata.get('date_of_birth', '')
        combined['meta_place_of_birth'] = metadata.get('place_of_birth', '')
        combined['meta_height'] = metadata.get('height', '')
        combined['meta_nationality'] = metadata.get('nationality', '')
        combined['meta_position_detail'] = metadata.get('position_detail', '')
        combined['meta_foot'] = metadata.get('foot', '')
        combined['meta_transfermarkt_url'] = metadata.get('transfermarkt_url', '')
        combined['meta_notes'] = metadata.get('notes', '')
        combined['meta_missing_seasons'] = metadata.get('missing_seasons', '')
        
        if 'honors' in metadata and metadata['honors']:
            combined['meta_honors'] = '; '.join(metadata['honors'])
        else:
            combined['meta_honors'] = ''
    
    # Save enriched file
    safe_name = player_name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e')
    output_file = os.path.join(ENRICHED_DIR, f'{safe_name}_enriched.csv')
    
    combined.to_csv(output_file, index=False)
    
    print(f'\n✅ Saved enriched data: {output_file}')
    print(f'   Rows: {len(combined)}')
    print(f'   Columns: {len(combined.columns)}')
    
    return output_file


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print('\nExample: python scripts/enrich_player_complete.py "Cristiano Ronaldo"')
        sys.exit(1)
    
    player_name = sys.argv[1]
    
    print(f'\n{"="*70}')
    print(f'AUTOMATED PLAYER ENRICHMENT PIPELINE')
    print(f'Player: {player_name}')
    print(f'{"="*70}')
    
    # Step 1: Search local database
    selected_player, local_df = search_player_in_database(player_name)
    
    if selected_player is None:
        print('\n❌ Cannot proceed without player data')
        sys.exit(1)
    
    # Step 2: Search Transfermarkt
    transfermarkt_id = search_transfermarkt_id(selected_player)
    
    if transfermarkt_id is None:
        print('\n⚠️ Skipping Transfermarkt data')
        tm_df = None
        missing_df = None
    else:
        # Step 3: Fetch Transfermarkt data
        tm_df = fetch_transfermarkt_seasons(transfermarkt_id, selected_player)
        
        if tm_df is not None:
            # Step 4: Compare and find missing seasons
            missing_df = compare_data_sources(local_df, tm_df, selected_player)
        else:
            missing_df = None
    
    # Step 5: Create/check metadata
    metadata_path = create_metadata_template(selected_player)
    
    # Step 6: Create enriched dataset
    output_file = enrich_and_save(selected_player, local_df, missing_df, metadata_path)
    
    print(f'\n{"="*70}')
    print(f'✅ PIPELINE COMPLETE')
    print(f'{"="*70}')
    print(f'\n📂 Output file: {output_file}')
    print(f'\n📝 Next steps:')
    if not os.path.exists(metadata_path) or os.path.getsize(metadata_path) < 100:
        print(f'   1. Fill metadata in: {metadata_path}')
        print(f'   2. Re-run script to add metadata')
    else:
        print(f'   1. ✅ Metadata already included')
    print(f'   2. Import {output_file} into Power BI for analysis')
    print(f'\n{"="*70}\n')


if __name__ == '__main__':
    main()
