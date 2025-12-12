import os
import sys
import pandas as pd
import soccerdata as sd

OUT = os.path.join('datalake', 'processed')
RAW_PLAYERS_DIR = os.path.join('datalake', 'raw', 'players')
os.makedirs(OUT, exist_ok=True)

def make_season_codes(start_year: int, end_year: int):
    return [f"{str(y)[-2:]}{str(y+1)[-2:]}" for y in range(start_year, end_year+1)]

def main(start_year=1995, end_year=2024):
    seasons = make_season_codes(int(start_year), int(end_year))
    print('Generating historical FBref dataset for seasons:', seasons[0], '->', seasons[-1])
    print('Total seasons:', len(seasons))
    try:
        fb = sd.FBref(seasons=seasons)
        df = fb.read_player_season_stats()
        print('Fetched player-season stats via FBref(seasons=...):', df.shape)
    except Exception as e:
        print('FBref(seasons=...) failed:', e)
        fb = sd.FBref()
        try:
            df = fb.read_player_season_stats(seasons=seasons)
            print('Fetched player-season stats via read_player_season_stats(seasons=...):', df.shape)
        except Exception as e2:
            print('read_player_season_stats(seasons=...) failed:', e2)
            print('Falling back to default read_player_season_stats() for available seasons.')
            df = fb.read_player_season_stats()
            print('Fetched player-season stats (default):', df.shape)

    # Flatten columns
    def flatten_col(c):
        if isinstance(c, tuple):
            parts = [str(x).strip() for x in c if x and str(x).strip()]
            return '_'.join(parts) if parts else ''
        return str(c)

    df_flat = df.copy()
    df_flat.columns = [flatten_col(c) for c in df_flat.columns]
    df_flat = df_flat.reset_index()

    players_out = os.path.join(OUT, f'players_historical_{start_year}_{end_year}.csv')
    df_flat.to_csv(players_out, index=False)
    print('Saved players:', players_out, 'rows:', len(df_flat))

    # Detect numeric columns and aggregate teams
    numeric_cols = []
    for col in df_flat.columns:
        if col in ['league', 'season', 'team', 'player']:
            continue
        series = pd.to_numeric(df_flat[col], errors='coerce')
        if series.notna().sum() > 0:
            df_flat[col] = series
            numeric_cols.append(col)

    print('Numeric columns detected (sample):', numeric_cols[:20])
    agg = df_flat.groupby(['league', 'season', 'team'])[numeric_cols].sum().reset_index()
    teams_out = os.path.join(OUT, f'teams_historical_{start_year}_{end_year}.csv')
    agg.to_csv(teams_out, index=False)
    print('Saved teams:', teams_out, 'rows:', len(agg))

    # Save a sample head to raw players
    sample_dir = os.path.join(RAW_PLAYERS_DIR, f'all_players_sample_{start_year}_{end_year}')
    os.makedirs(sample_dir, exist_ok=True)
    df_flat.head(500).to_csv(os.path.join(sample_dir, 'players_sample_head.csv'), index=False)
    print('Saved sample head to', sample_dir)

if __name__ == '__main__':
    start = 1995
    end = 2024
    if len(sys.argv) >= 3:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
    main(start, end)
