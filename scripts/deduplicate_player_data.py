"""
Remove duplicate rows from enriched player datasets.

This script:
1. Identifies duplicate season+team+league rows
2. Keeps only the first occurrence
3. Saves deduplicated CSV

Usage:
    python scripts/deduplicate_player_data.py player_name
    
Example:
    python scripts/deduplicate_player_data.py "Cristiano Ronaldo"
"""

import sys
import pandas as pd
import os

def deduplicate_player_data(player_name):
    """Remove duplicate rows from player enriched CSV."""
    
    safe_name = player_name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e')
    file_path = f'datalake/processed/enriched/{safe_name}_enriched.csv'
    
    if not os.path.exists(file_path):
        print(f'❌ File not found: {file_path}')
        return
    
    print(f'\n🔍 Loading {file_path}...')
    df = pd.read_csv(file_path, dtype={'season': str})
    
    original_count = len(df)
    original_goals = df['Performance_Gls'].sum()
    
    print(f'   Original rows: {original_count}')
    print(f'   Original goals total: {original_goals}')
    
    # Check for duplicates
    print(f'\n🔍 Checking for duplicates...')
    
    # Method 1: Check duplicates by season+league (same season, same league, same stats)
    # This catches rows where team="Premier League" vs team="Manchester Utd" for same season
    dup_mask = df.duplicated(subset=['season', 'league', 'Performance_Gls', 'Playing_Time_MP'], keep=False)
    duplicates = df[dup_mask].sort_values(['season', 'league'])
    
    if len(duplicates) > 0:
        print(f'   ⚠️ Found {len(duplicates)} rows with duplicate season+league+stats')
        print(f'\n   Sample duplicates (same season, same league, same stats):')
        print(duplicates[['season', 'team', 'league', 'Performance_Gls', 'Playing_Time_MP']].head(20))
    else:
        print(f'   ✅ No duplicates found')
        return
    
    # Remove duplicates - keep rows where team is NOT the league name
    # Logic: keep rows where team column doesn't match a known league name
    print(f'\n🧹 Removing duplicates...')
    
    # Identify league-named rows to remove
    league_keywords = ['Premier League', 'LaLiga', 'Liga', 'Serie A', 'Bundesliga', 'Ligue 1']
    
    def is_league_team_name(team):
        """Check if team column contains a league name instead of actual team."""
        if pd.isna(team):
            return False
        team_str = str(team)
        return any(keyword in team_str for keyword in league_keywords)
    
    # Mark rows to remove
    df['is_league_name'] = df['team'].apply(is_league_team_name)
    
    print(f'   Found {df["is_league_name"].sum()} rows with league names in team column')
    
    # Keep only rows where team is NOT a league name
    df_clean = df[~df['is_league_name']].copy()
    df_clean = df_clean.drop(columns=['is_league_name'])
    
    new_count = len(df_clean)
    new_goals = df_clean['Performance_Gls'].sum()
    removed = original_count - new_count
    
    print(f'   ✅ Removed {removed} duplicate rows')
    print(f'   New row count: {new_count}')
    print(f'   New goals total: {new_goals}')
    print(f'   Goals difference: {original_goals - new_goals}')
    
    # Save cleaned file
    df_clean.to_csv(file_path, index=False)
    
    print(f'\n✅ Saved cleaned data: {file_path}')
    print(f'\n📊 Summary:')
    print(f'   Rows: {original_count} → {new_count} (-{removed})')
    print(f'   Goals: {original_goals:.0f} → {new_goals:.0f} (-{original_goals - new_goals:.0f})')
    print(f'\n   Import this cleaned file into Power BI to get correct totals!\n')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print('\nExample: python scripts/deduplicate_player_data.py "Cristiano Ronaldo"')
        sys.exit(1)
    
    player_name = sys.argv[1]
    deduplicate_player_data(player_name)


if __name__ == '__main__':
    main()
