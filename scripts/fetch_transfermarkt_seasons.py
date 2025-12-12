"""
Fetch missing player seasons from Transfermarkt.

Usage:
    python scripts/fetch_transfermarkt_seasons.py 3368 "Kaká"
    
Args:
    player_id: Transfermarkt player ID (e.g., 3368 for Kaká)
    player_name: Player name for output file
"""

import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime

def get_transfermarkt_stats(player_id, player_name):
    """
    Scrape player season statistics from Transfermarkt.
    
    Args:
        player_id: Transfermarkt player ID
        player_name: Player name (for URL construction)
        
    Returns:
        DataFrame with season statistics
    """
    # Clean player name for URL (lowercase, no accents)
    url_name = player_name.lower().replace('á', 'a').replace('é', 'e').replace(' ', '-')
    url = f"https://www.transfermarkt.com.br/{url_name}/leistungsdatendetails/spieler/{player_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.transfermarkt.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    print(f'🌐 Fetching Transfermarkt data: {url}')
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        if response.status_code == 403:
            print('❌ Blocked by anti-bot (403 Forbidden)')
            print('   Try accessing the URL manually and copy the HTML')
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the performance data table
        # Transfermarkt uses table with class 'items'
        tables = soup.find_all('table', {'class': 'items'})
        
        if not tables:
            print('❌ No performance table found')
            print(f'   Page title: {soup.title.string if soup.title else "N/A"}')
            return None
        
        print(f'✅ Found {len(tables)} tables, parsing...')
        
        # First table contains all season stats
        seasons_data = []
        table = tables[0]
        rows = table.find_all('tr', {'class': ['odd', 'even']})
        
        print(f'   Processing {len(rows)} season rows...')
        
        for row in rows:
            cells = row.find_all('td')
            
            if len(cells) < 5:  # Need minimum columns
                continue
            
            try:
                # Column 0: Season
                season_text = cells[0].get_text(strip=True)
                
                # Column 1: Competition/League (get title from img or text)
                comp_cell = cells[1]
                comp_img = comp_cell.find('img')
                league = comp_img.get('title', '') if comp_img else comp_cell.get_text(strip=True)
                
                # Column 2: Team (skip if empty/header row)
                team_text = cells[2].get_text(strip=True)
                if not team_text or team_text.lower() in ['club', 'total', '']:
                    continue
                
                # Columns 3+: blank, apps, goals, assists, cards
                # Index 3 is usually blank (squad number)
                # Index 4: appearances
                # Index 5: goals  
                # Index 6: assists
                apps = cells[4].get_text(strip=True) if len(cells) > 4 else '0'
                goals = cells[5].get_text(strip=True) if len(cells) > 5 else '0'
                assists = cells[6].get_text(strip=True) if len(cells) > 6 else '0'
                
                # Clean values (remove '-')
                apps = apps if apps and apps != '-' else '0'
                goals = goals if goals and goals != '-' else '0'
                assists = assists if assists and assists != '-' else '0'
                
                # Skip totals row
                if 'total' in season_text.lower():
                    continue
                
                season_data = {
                    'season': season_text,
                    'team': team_text,
                    'league': league,
                    'appearances': apps,
                    'goals': goals,
                    'assists': assists
                }
                
                seasons_data.append(season_data)
                
            except Exception as e:
                print(f'   ⚠️ Error parsing row: {e}')
                continue
        
        if not seasons_data:
            print('❌ No season data extracted')
            return None
        
        df = pd.DataFrame(seasons_data)
        print(f'✅ Extracted {len(df)} seasons')
        
        return df
        
    except requests.RequestException as e:
        print(f'❌ Request error: {e}')
        return None
    except Exception as e:
        print(f'❌ Parsing error: {e}')
        return None


def format_season_code(season_text):
    """
    Convert season text to numeric code format.
    Examples: '2015/2016' -> '1516', '2001/2002' -> '0102'
    """
    # Extract years
    match = re.search(r'(\d{4})[/\-](\d{2,4})', season_text)
    if match:
        year1 = match.group(1)
        year2 = match.group(2)
        
        # Handle 2-digit or 4-digit second year
        if len(year2) == 2:
            code = year1[-2:] + year2
        else:
            code = year1[-2:] + year2[-2:]
        
        return code
    
    # Single year format (e.g., '2015')
    match = re.search(r'(\d{4})', season_text)
    if match:
        year = match.group(1)
        return year[-2:] + year[-2:]
    
    return season_text


def filter_missing_seasons(df, missing_leagues=['Major League Soccer', 'Série A', 'Campeonato Brasileiro']):
    """
    Filter DataFrame to only include seasons from missing leagues.
    For Kaká: MLS (Orlando City) and Série A (São Paulo)
    """
    mask = df['league'].str.contains('|'.join(missing_leagues), case=False, na=False, regex=True)
    filtered = df[mask].copy()
    
    # Exclude cups (only league matches)
    cup_keywords = ['Copa', 'Cup', 'Supercopa', 'Sul-Americana', 'Open']
    for keyword in cup_keywords:
        filtered = filtered[~filtered['league'].str.contains(keyword, case=False, na=False)]
    
    print(f'\n🔍 Filtered to missing leagues')
    print(f'   Found {len(filtered)} seasons (excluding cups)')
    
    if len(filtered) > 0:
        print('\nSeasons found:')
        for _, row in filtered.iterrows():
            print(f"   {row['season']:10} - {row['league']:40} - {row['goals']:2} goals, {row['assists']:2} assists")
    
    return filtered


def save_to_csv(df, player_name):
    """Save scraped data to CSV."""
    safe_name = player_name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e')
    output_file = f'datalake/raw/transfermarkt/{safe_name}_missing_seasons.csv'
    
    import os
    os.makedirs('datalake/raw/transfermarkt', exist_ok=True)
    
    df.to_csv(output_file, index=False)
    print(f'\n✅ Saved to: {output_file}')
    return output_file


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print('\nExample: python scripts/fetch_transfermarkt_seasons.py 3368 "Kaká"')
        sys.exit(1)
    
    player_id = sys.argv[1]
    player_name = sys.argv[2]
    
    print(f'\n{"="*60}')
    print(f'Fetching Transfermarkt data for {player_name} (ID: {player_id})')
    print(f'{"="*60}\n')
    
    # Fetch data
    df = get_transfermarkt_stats(player_id, player_name)
    
    if df is None:
        print('\n❌ Failed to fetch data')
        sys.exit(1)
    
    # Show all seasons
    print('\n📊 All seasons found:')
    print(df[['season', 'team', 'league', 'appearances', 'goals', 'assists']].to_string(index=False))
    
    # Filter to missing seasons (São Paulo + Orlando City)
    filtered = filter_missing_seasons(df)
    
    if len(filtered) == 0:
        print('\n⚠️ No missing seasons found in the data')
        print('   Check if team names match (São Paulo, Orlando City)')
    else:
        # Save to CSV
        output_file = save_to_csv(filtered, player_name)
        
        print('\n📝 Next steps:')
        print(f'   1. Review the data in: {output_file}')
        print(f'   2. Use scripts/merge_missing_seasons.py to combine with existing data')
    
    print(f'\n{"="*60}\n')


if __name__ == '__main__':
    main()
