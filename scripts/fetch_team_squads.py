"""
Football Team Squad Scraper - Transfermarkt
============================================

Scrapes team squad compositions (players, positions, market values) from Transfermarkt
for historical seasons across major leagues.

Output: CSV with columns:
- team, season, player_name, position, shirt_number, age, nationality, 
  market_value, joined_date, contract_until, league

Usage:
    python scripts/fetch_team_squads.py --team "Manchester United" --season 2023
    python scripts/fetch_team_squads.py --league "premier-league" --season 2023
    python scripts/fetch_team_squads.py --all-seasons  # Scrape all available data
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse
import json
from pathlib import Path
from datetime import datetime
import re

# Constants
BASE_URL = "https://www.transfermarkt.com"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# League mapping (Transfermarkt URLs)
LEAGUE_MAP = {
    'premier-league': {'id': 'GB1', 'name': 'Premier League'},
    'la-liga': {'id': 'ES1', 'name': 'LaLiga'},
    'bundesliga': {'id': 'L1', 'name': 'Bundesliga'},
    'serie-a': {'id': 'IT1', 'name': 'Serie A'},
    'ligue-1': {'id': 'FR1', 'name': 'Ligue 1'},
    'eredivisie': {'id': 'NL1', 'name': 'Eredivisie'},
    'primeira-liga': {'id': 'PO1', 'name': 'Liga Portugal'},
    'championship': {'id': 'GB2', 'name': 'Championship'},
    'saudi-pro-league': {'id': 'SA1', 'name': 'Saudi Pro League'},
    'mls': {'id': 'MLS1', 'name': 'MLS'}
}


def search_team_transfermarkt(team_name):
    """
    Search for a team on Transfermarkt and return team ID and URL
    """
    # Hardcoded team IDs for common teams (faster and more reliable)
    TEAM_IDS = {
        'manchester united': '985',
        'real madrid': '418',
        'barcelona': '131',
        'bayern munich': '27',
        'liverpool': '31',
        'chelsea': '631',
        'arsenal': '11',
        'manchester city': '281',
        'psg': '583',
        'juventus': '506',
        'inter': '46',
        'ac milan': '5',
        'ajax': '610',
        'benfica': '294',
        'porto': '720',
        'al-nassr': '3732',
        'inter miami': '69220'
    }
    
    team_lower = team_name.lower()
    if team_lower in TEAM_IDS:
        team_id = TEAM_IDS[team_lower]
        print(f"✓ Found team: {team_name} (ID: {team_id})")
        return {'id': team_id, 'name': team_name}
    
    # Fallback to search
    search_url = f"{BASE_URL}/schnellsuche/ergebnis/schnellsuche"
    params = {'query': team_name}
    
    try:
        print(f"🔍 Searching for '{team_name}'...")
        response = requests.get(search_url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find first club result
        club_box = soup.find('div', {'id': 'yw1'})
        if club_box:
            team_link = club_box.find('a', href=re.compile(r'/verein/'))
            if team_link:
                team_url = team_link['href']
                team_id = team_url.split('/')[-1]
                team_display_name = team_link.find('img')['alt'] if team_link.find('img') else team_name
                print(f"✓ Found team: {team_display_name} (ID: {team_id})")
                return {'id': team_id, 'name': team_display_name}
        
        print(f"❌ Team '{team_name}' not found")
        
    except Exception as e:
        print(f"❌ Error searching team: {e}")
    
    return None


def get_team_squad(team_id, season, team_name="Unknown"):
    """
    Fetch squad composition for a specific team and season
    
    Args:
        team_id: Transfermarkt team ID
        season: Season year (e.g., 2023 for 2023-24 season)
        team_name: Team name for output
    
    Returns:
        DataFrame with squad data
    """
    squad_url = f"{BASE_URL}/{team_name.lower().replace(' ', '-')}/kader/verein/{team_id}/saison_id/{season}/plus/1"
    
    try:
        print(f"📥 Fetching {team_name} squad for {season}-{season+1}...")
        print(f"   URL: {squad_url}")
        response = requests.get(squad_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find squad table - try multiple selectors
        squad_table = soup.find('table', {'class': 'items'})
        
        if not squad_table:
            # Try alternative selector
            squad_table = soup.find('div', {'id': 'yw1'})
            if squad_table:
                squad_table = squad_table.find('table')
        
        if not squad_table:
            print(f"⚠️  No squad table found for {season}")
            # Debug: save HTML to file
            debug_file = Path('debug_squad.html')
            debug_file.write_text(soup.prettify(), encoding='utf-8')
            print(f"   💾 Saved HTML to {debug_file} for debugging")
            return pd.DataFrame()
        
        players_data = []
        tbody = squad_table.find('tbody')
        
        if not tbody:
            print("⚠️  No tbody found in table")
            return pd.DataFrame()
        
        rows = tbody.find_all('tr', class_=lambda x: x and ('odd' in x or 'even' in x))
        
        if not rows:
            # Try without class filter
            rows = tbody.find_all('tr')
        
        print(f"   Found {len(rows)} table rows")
        
        for idx, row in enumerate(rows):
            try:
                # Skip header rows
                if row.find('th'):
                    continue
                
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue
                
                # Extract data from cells
                # Cell 0: Shirt number
                shirt_number = cells[0].text.strip() if cells[0] else ''
                
                # Cell 1: Player name and image
                player_cell = cells[1]
                player_link = player_cell.find('a', href=re.compile(r'/profil/spieler/'))
                player_name = player_link.text.strip() if player_link else ''
                player_url = BASE_URL + player_link['href'] if player_link else ''
                
                if not player_name:
                    continue
                
                # Cell 2: Position
                position = cells[2].text.strip() if len(cells) > 2 else ''
                
                # Cell 3: Date of birth / Age
                age_cell = cells[3].text.strip() if len(cells) > 3 else ''
                age_match = re.search(r'\((\d+)\)', age_cell)
                age = age_match.group(1) if age_match else ''
                
                # Cell 4: Nationality
                nat_imgs = cells[4].find_all('img') if len(cells) > 4 else []
                nationalities = [img.get('title', '') for img in nat_imgs]
                nationality = ', '.join(nationalities) if nationalities else ''
                
                # Market value - usually last or second-to-last cell
                market_value = ''
                for cell in reversed(cells):
                    if '€' in cell.text or 'k' in cell.text or 'm' in cell.text:
                        market_value = cell.text.strip()
                        break
                
                players_data.append({
                    'team': team_name,
                    'season': f"{season}-{season+1}",
                    'season_year': season,
                    'player_name': player_name,
                    'position': position,
                    'shirt_number': shirt_number,
                    'age': age,
                    'nationality': nationality,
                    'market_value': market_value,
                    'player_url': player_url,
                    'scraped_date': datetime.now().strftime('%Y-%m-%d')
                })
                
            except Exception as e:
                print(f"  ⚠️  Error parsing row {idx}: {e}")
                continue
        
        print(f"  ✓ Extracted {len(players_data)} players")
        time.sleep(2)  # Rate limiting
        
        return pd.DataFrame(players_data)
        
    except Exception as e:
        print(f"❌ Error fetching squad: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def get_league_teams(league_code, season):
    """
    Get all teams in a league for a specific season
    
    Args:
        league_code: League code (e.g., 'GB1' for Premier League)
        season: Season year
    
    Returns:
        List of team dictionaries
    """
    league_url = f"{BASE_URL}/wettbewerb/startseite/wettbewerb/{league_code}/saison_id/{season}"
    
    try:
        print(f"🏆 Fetching teams from {league_code} ({season})...")
        response = requests.get(league_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        teams = []
        
        # Find teams table
        team_table = soup.find('table', {'class': 'items'})
        if not team_table:
            return teams
        
        rows = team_table.find_all('tr')
        for row in rows:
            team_link = row.find('a', {'class': 'vereinprofil_tooltip'})
            if team_link:
                team_name = team_link.text.strip()
                team_url = team_link['href']
                team_id = team_url.split('/')[-1]
                teams.append({'name': team_name, 'id': team_id})
        
        print(f"  ✓ Found {len(teams)} teams")
        time.sleep(2)
        return teams
        
    except Exception as e:
        print(f"❌ Error fetching league teams: {e}")
        return []


def scrape_league_squads(league_name, seasons):
    """
    Scrape all team squads from a league across multiple seasons
    
    Args:
        league_name: League name from LEAGUE_MAP
        seasons: List of season years
    
    Returns:
        DataFrame with all squads
    """
    if league_name not in LEAGUE_MAP:
        print(f"❌ League '{league_name}' not found. Available: {list(LEAGUE_MAP.keys())}")
        return pd.DataFrame()
    
    league_info = LEAGUE_MAP[league_name]
    league_code = league_info['id']
    all_squads = []
    
    for season in seasons:
        print(f"\n{'='*60}")
        print(f"📅 Season {season}-{season+1} - {league_info['name']}")
        print(f"{'='*60}\n")
        
        # Get teams in league
        teams = get_league_teams(league_code, season)
        
        if not teams:
            print(f"⚠️  No teams found for {season}")
            continue
        
        # Fetch squad for each team
        for i, team in enumerate(teams, 1):
            print(f"[{i}/{len(teams)}] ", end="")
            squad_df = get_team_squad(team['id'], season, team['name'])
            
            if not squad_df.empty:
                squad_df['league'] = league_info['name']
                all_squads.append(squad_df)
            
            time.sleep(3)  # Rate limiting between teams
    
    if all_squads:
        final_df = pd.concat(all_squads, ignore_index=True)
        print(f"\n✅ Total players scraped: {len(final_df)}")
        return final_df
    else:
        return pd.DataFrame()


def clean_market_value(value_str):
    """
    Convert market value string to numeric (in millions)
    
    Examples:
        '€50.00m' -> 50.0
        '€1.50m' -> 1.5
        '€750k' -> 0.75
    """
    if not value_str or value_str == '-':
        return 0.0
    
    try:
        # Remove currency symbol
        value_str = value_str.replace('€', '').replace('$', '').strip()
        
        if 'm' in value_str.lower():
            return float(value_str.lower().replace('m', ''))
        elif 'k' in value_str.lower():
            return float(value_str.lower().replace('k', '')) / 1000
        else:
            return 0.0
    except:
        return 0.0


def main():
    parser = argparse.ArgumentParser(description='Scrape football team squad data from Transfermarkt')
    parser.add_argument('--team', type=str, help='Team name to search')
    parser.add_argument('--season', type=int, help='Season year (e.g., 2023 for 2023-24)')
    parser.add_argument('--league', type=str, choices=list(LEAGUE_MAP.keys()), help='League to scrape')
    parser.add_argument('--seasons', type=str, help='Comma-separated seasons (e.g., "2021,2022,2023")')
    parser.add_argument('--output', type=str, default='datalake/raw/squads', help='Output directory')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    squads_df = pd.DataFrame()
    
    # Single team mode
    if args.team and args.season:
        team_info = search_team_transfermarkt(args.team)
        if team_info:
            squads_df = get_team_squad(team_info['id'], args.season, team_info['name'])
            output_file = output_dir / f"{args.team.replace(' ', '_').lower()}_{args.season}_squad.csv"
    
    # League mode
    elif args.league and args.seasons:
        seasons = [int(s.strip()) for s in args.seasons.split(',')]
        squads_df = scrape_league_squads(args.league, seasons)
        output_file = output_dir / f"{args.league}_squads_{min(seasons)}_{max(seasons)}.csv"
    
    else:
        print("❌ Please provide either:")
        print("   --team 'Team Name' --season 2023")
        print("   OR")
        print("   --league premier-league --seasons '2021,2022,2023'")
        return
    
    # Save results
    if not squads_df.empty:
        # Clean market values
        squads_df['market_value_millions'] = squads_df['market_value'].apply(clean_market_value)
        
        # Save to CSV
        squads_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n✅ Saved to: {output_file}")
        print(f"📊 Total records: {len(squads_df)}")
        print(f"👥 Unique players: {squads_df['player_name'].nunique()}")
        print(f"⚽ Teams: {squads_df['team'].nunique()}")
    else:
        print("\n❌ No data scraped")


if __name__ == "__main__":
    main()
