import os
import pandas as pd

OUT_DIR = os.path.join('datalake', 'processed')
os.makedirs(OUT_DIR, exist_ok=True)

def season_to_period(code):
    s = str(code)
    if len(s) == 4 and s.isdigit():
        start = int(s[:2])
        end = int(s[2:])
        if start >= 90:
            start_year = 1900 + start
        else:
            start_year = 2000 + start if start <= 50 else 1900 + start
        if end < start:
            end_year = start_year + 1
        else:
            end_year = (start_year // 100) * 100 + end
        return f"{start_year}-{end_year}"
    return s

def flatten_columns(df):
    new_cols = {c: c.strip().replace(' ', '_').replace('/', '_') for c in df.columns}
    df = df.rename(columns=new_cols)
    return df

def normalize_players(path):
    print('Loading players from', path)
    # read season as string to preserve leading zeros like '0001' or '9596'
    try:
        df = pd.read_csv(path, low_memory=False, dtype={'season': str})
    except Exception:
        df = pd.read_csv(path, low_memory=False)
    if 'season' in df.columns:
        df['season_period'] = df['season'].astype(str).apply(season_to_period)
    df = flatten_columns(df)
    return df

def normalize_teams(path):
    print('Loading teams from', path)
    try:
        df = pd.read_csv(path, low_memory=False, dtype={'season': str})
    except Exception:
        df = pd.read_csv(path, low_memory=False)
    if 'season' in df.columns:
        df['season_period'] = df['season'].astype(str).apply(season_to_period)
    df = flatten_columns(df)
    return df

def main():
    players_hist = os.path.join(OUT_DIR, 'players_historical_1995_2024.csv')
    teams_hist = os.path.join(OUT_DIR, 'teams_historical_1995_2024.csv')
    players_curr = os.path.join(OUT_DIR, 'players.csv')
    teams_curr = os.path.join(OUT_DIR, 'teams.csv')

    p_hist = normalize_players(players_hist)
    p_curr = normalize_players(players_curr)

    # concat and drop duplicates
    combined_players = pd.concat([p_hist, p_curr], ignore_index=True, sort=False)
    before = len(combined_players)
    combined_players.drop_duplicates(subset=['league','season','team','player'], keep='last', inplace=True)
    after = len(combined_players)
    print(f'Players combined: {before} -> deduplicated {after}')

    players_out = os.path.join(OUT_DIR, 'players_complete_1995_2025.csv')
    combined_players.to_csv(players_out, index=False)
    print('Saved', players_out)

    # Teams
    t_hist = normalize_teams(teams_hist)
    t_curr = normalize_teams(teams_curr)
    combined_teams = pd.concat([t_hist, t_curr], ignore_index=True, sort=False)
    before_t = len(combined_teams)
    combined_teams.drop_duplicates(subset=['league','season','team'], keep='last', inplace=True)
    after_t = len(combined_teams)
    print(f'Teams combined: {before_t} -> deduplicated {after_t}')
    teams_out = os.path.join(OUT_DIR, 'teams_complete_1995_2025.csv')
    combined_teams.to_csv(teams_out, index=False)
    print('Saved', teams_out)

if __name__ == '__main__':
    main()
