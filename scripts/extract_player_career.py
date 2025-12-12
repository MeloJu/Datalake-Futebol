import sys
import os
import pandas as pd

OUT = os.path.join('datalake','processed')
os.makedirs(OUT, exist_ok=True)

def extract(name_pattern, infile='datalake/processed/players_complete_1995_2025.csv', outfile=None, team_filter=None):
    """
    Extract player career data.
    
    Args:
        name_pattern: Player name to search
        infile: Input CSV path
        outfile: Output CSV path (auto-generated if None)
        team_filter: List of teams to filter by (helps distinguish players with same name)
    """
    df = pd.read_csv(infile, low_memory=False, dtype={'season': str})
    mask = df['player'].astype(str).str.contains(name_pattern, case=False, na=False)
    res = df[mask].copy()
    
    # Apply team filter if provided (useful for disambiguating common names)
    if team_filter:
        res = res[res['team'].isin(team_filter)]
    
    if outfile is None:
        safe = name_pattern.lower().replace(' ','_')
        outfile = os.path.join(OUT, f'{safe}_career.csv')
    res.to_csv(outfile, index=False)
    print('Saved', outfile, 'rows:', len(res))
    print('Teams:', res['team'].unique().tolist())
    return outfile, len(res)

if __name__ == '__main__':
    name = 'Kaká' if len(sys.argv) == 1 else sys.argv[1]
    extract(name)
