"""
Merge missing seasons with enriched player data.

Usage:
    python scripts/merge_missing_seasons.py kaka kaka_missing_seasons.csv
    
This script:
1. Loads existing enriched CSV (e.g., kaka_enriched.csv)
2. Loads missing seasons CSV from raw/transfermarkt/
3. Merges and sorts by season
4. Saves updated enriched CSV
"""

import sys
import pandas as pd
import os

def merge_missing_seasons(player_name, missing_csv):
    """
    Merge missing seasons into enriched player data.
    
    Args:
        player_name: Player name (e.g., 'kaka')
        missing_csv: Filename of missing seasons CSV in raw/transfermarkt/
    """
    # Paths
    enriched_path = f'datalake/processed/enriched/{player_name}_enriched.csv'
    missing_path = f'datalake/raw/transfermarkt/{missing_csv}'
    output_path = enriched_path  # Overwrite existing
    
    print(f'\n📂 Loading files...')
    print(f'   Enriched: {enriched_path}')
    print(f'   Missing:  {missing_path}')
    
    # Load existing enriched data
    try:
        df_enriched = pd.read_csv(enriched_path, dtype={'season': str})
        print(f'✅ Loaded {len(df_enriched)} existing seasons')
    except Exception as e:
        print(f'❌ Error loading enriched file: {e}')
        return
    
    # Load missing seasons
    try:
        df_missing = pd.read_csv(missing_path, dtype={'season': str})
        print(f'✅ Loaded {len(df_missing)} missing seasons')
    except Exception as e:
        print(f'❌ Error loading missing file: {e}')
        return
    
    # Show what's being added
    print(f'\n📊 Missing seasons to add:')
    for _, row in df_missing.iterrows():
        print(f'   {row["season_period"]} - {row["team"]} - {row["Performance_Gls"]} goals, {row["Performance_Ast"]} assists')
    
    # Get metadata columns from enriched data (meta_* columns)
    meta_cols = [col for col in df_enriched.columns if col.startswith('meta_')]
    
    if meta_cols:
        print(f'\n🔄 Adding metadata to missing seasons ({len(meta_cols)} columns)...')
        # Copy metadata from first row of enriched (assumes all rows have same metadata)
        for col in meta_cols:
            df_missing[col] = df_enriched[col].iloc[0]
    
    # Combine datasets
    df_combined = pd.concat([df_enriched, df_missing], ignore_index=True)
    
    # Sort by season code
    df_combined = df_combined.sort_values('season')
    
    # Remove duplicates (if any)
    before_dedup = len(df_combined)
    df_combined = df_combined.drop_duplicates(subset=['season', 'team', 'league'], keep='first')
    after_dedup = len(df_combined)
    
    if before_dedup != after_dedup:
        print(f'\n⚠️ Removed {before_dedup - after_dedup} duplicate rows')
    
    # Save
    df_combined.to_csv(output_path, index=False)
    
    print(f'\n✅ Saved merged data: {output_path}')
    print(f'   Total seasons: {len(df_combined)}')
    print(f'   Columns: {len(df_combined.columns)}')
    
    # Show timeline
    print(f'\n📅 Complete timeline:')
    timeline = df_combined[['season', 'season_period', 'team', 'league', 'Performance_Gls', 'Performance_Ast']].copy()
    timeline = timeline.sort_values('season')
    print(timeline.to_string(index=False))
    
    print(f'\n✅ Merge complete! Updated file: {output_path}\n')


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print('\nExample: python scripts/merge_missing_seasons.py kaka kaka_missing_seasons.csv')
        sys.exit(1)
    
    player_name = sys.argv[1]
    missing_csv = sys.argv[2]
    
    merge_missing_seasons(player_name, missing_csv)


if __name__ == '__main__':
    main()
