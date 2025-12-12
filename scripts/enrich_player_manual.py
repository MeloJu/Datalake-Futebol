"""
Simple player enrichment: add manual metadata to player CSV.

Usage:
    1. Create a JSON file with player metadata, e.g. kaka_metadata.json:
    {
        "date_of_birth": "1982-04-22",
        "place_of_birth": "Brasília, Brazil",
        "height": "1.86m",
        "nationality": "Brazil",
        "position_detail": "Attacking Midfield",
        "foot": "Left",
        "honors": [
            "FIFA World Cup: 2002",
            "Ballon d'Or: 2007",
            "UEFA Champions League: 2006-07",
            "Serie A: 2003-04",
            "La Liga: 2011-12"
        ],
        "transfermarkt_url": "https://www.transfermarkt.com/kaka/profil/spieler/3368",
        "notes": "One of the best attacking midfielders of his generation"
    }
    
    2. Run this script:
    python scripts/enrich_player_manual.py "Kaká" kaka_metadata.json
"""

import sys
import os
import json
import pandas as pd

OUT = os.path.join('datalake', 'processed')
os.makedirs(OUT, exist_ok=True)

def load_player_stats(player_name, csv_path='datalake/processed/players_complete_1995_2025.csv', team_filter=None):
    """
    Load player stats from local CSV.
    
    Args:
        player_name: Player name to search
        csv_path: Path to complete players CSV
        team_filter: Optional list of teams to filter by (helps with disambiguation)
    """
    try:
        df = pd.read_csv(csv_path, low_memory=False, dtype={'season': str})
        
        # Exact match first (case-insensitive)
        mask = df['player'].astype(str).str.lower() == player_name.lower()
        player_df = df[mask].copy()
        
        # If no exact match, try contains
        if len(player_df) == 0:
            mask = df['player'].astype(str).str.contains(player_name, case=False, na=False, regex=False)
            player_df = df[mask].copy()
        
        # Apply team filter if provided (useful for players with common names)
        if team_filter and len(player_df) > 0:
            player_df = player_df[player_df['team'].isin(team_filter)]
            print(f'Filtered to teams: {team_filter}')
        
        if len(player_df) == 0:
            print(f'No stats found for "{player_name}" in local CSV')
            return None
        
        print(f'Found {len(player_df)} season records for {player_name}')
        print(f'Teams: {sorted(player_df["team"].unique())}')
        return player_df
    except Exception as e:
        print(f'Error loading CSV: {e}')
        return None

def enrich_with_metadata(player_stats, metadata):
    """Add metadata columns to player dataframe."""
    player_stats['meta_date_of_birth'] = metadata.get('date_of_birth', '')
    player_stats['meta_place_of_birth'] = metadata.get('place_of_birth', '')
    player_stats['meta_height'] = metadata.get('height', '')
    player_stats['meta_nationality'] = metadata.get('nationality', '')
    player_stats['meta_position_detail'] = metadata.get('position_detail', '')
    player_stats['meta_foot'] = metadata.get('foot', '')
    player_stats['meta_transfermarkt_url'] = metadata.get('transfermarkt_url', '')
    player_stats['meta_notes'] = metadata.get('notes', '')
    player_stats['meta_missing_seasons'] = metadata.get('missing_seasons', '')
    
    if 'honors' in metadata and metadata['honors']:
        player_stats['meta_honors'] = '; '.join(metadata['honors'])
    else:
        player_stats['meta_honors'] = ''
    
    return player_stats

def main(player_name, metadata_file, team_filter=None):
    """
    Enrich player data with manual metadata.
    
    Args:
        player_name: Name of the player
        metadata_file: Path to JSON metadata file
        team_filter: Optional list of teams to filter by (for disambiguation)
    """
    print(f'\n=== Enriching {player_name} with manual metadata ===\n')
    
    # Load player stats
    player_stats = load_player_stats(player_name, team_filter=team_filter)
    if player_stats is None:
        return
    
    # Load metadata JSON
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        print(f'Loaded metadata from {metadata_file}')
    except Exception as e:
        print(f'Error loading metadata file: {e}')
        return
    
    # Enrich
    enriched = enrich_with_metadata(player_stats, metadata)
    
    # Save to enriched/ subdirectory
    enriched_dir = os.path.join(OUT, 'enriched')
    os.makedirs(enriched_dir, exist_ok=True)
    
    safe_name = player_name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e')
    output_file = os.path.join(enriched_dir, f'{safe_name}_enriched.csv')
    enriched.to_csv(output_file, index=False)
    
    print(f'\n✅ Saved enriched data: {output_file}')
    print(f'   Rows: {len(enriched)}')
    print(f'   Columns: {len(enriched.columns)}')
    
    # Print summary
    print('\n=== Metadata Summary ===')
    for key, value in metadata.items():
        if key == 'honors' and isinstance(value, list):
            print(f'{key}: {len(value)} awards')
            for h in value[:5]:
                print(f'  - {h}')
        elif isinstance(value, str) and len(value) > 60:
            print(f'{key}: {value[:60]}...')
        else:
            print(f'{key}: {value}')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    player_name = sys.argv[1]
    metadata_file = sys.argv[2]
    main(player_name, metadata_file)
