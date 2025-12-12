"""
Preenche idades faltantes (NaN) no dataset de CR7.

Para temporadas onde age está vazio, calcula a idade baseado em:
- Data de nascimento: 05/02/1985
- Temporada: converte código (ex: "0203" = 2002-2003)
- Idade aproximada: ano da temporada - ano de nascimento
"""

import pandas as pd
from datetime import datetime

# Carregar dados
df = pd.read_csv('datalake/processed/enriched/cristiano_ronaldo_enriched.csv', dtype={'season': str})

print(f'Total linhas: {len(df)}')
print(f'Linhas com age nulo: {df["age"].isna().sum()}')

if df["age"].isna().sum() > 0:
    print('\n=== Linhas com age nulo ===')
    print(df[df['age'].isna()][['season', 'team', 'league', 'Playing_Time_MP']])

# Data de nascimento do CR7
birth_year = 1985
birth_month = 2  # Fevereiro

def calculate_age(season_code):
    """Calcula idade aproximada baseado no código da temporada."""
    if pd.isna(season_code) or len(season_code) < 4:
        return None
    
    # Converter código: "0203" -> 2002 (primeiro ano da temporada)
    year_str = season_code[:2]
    
    # Se começa com 0, é 2000s, senão é 1900s
    if year_str[0] == '0':
        year = 2000 + int(year_str)
    else:
        year = 1900 + int(year_str)
    
    # Idade aproximada (temporada começa em agosto, ele nasce em fevereiro)
    # Então na maior parte da temporada ele já fez aniversário
    age = year - birth_year
    
    return float(age)

# Preencher idades faltantes
df['age_filled'] = df.apply(
    lambda row: row['age'] if pd.notna(row['age']) else calculate_age(row['season']),
    axis=1
)

print('\n=== Após preencher ===')
print(f'Linhas com age_filled nulo: {df["age_filled"].isna().sum()}')

# Atualizar coluna age
df['age'] = df['age_filled']
df = df.drop(columns=['age_filled'])

# Salvar
df.to_csv('datalake/processed/enriched/cristiano_ronaldo_enriched.csv', index=False)

print('\n✅ Arquivo atualizado!')
print('\nIdades preenchidas:')
print(df[['season', 'team', 'age']].head(5))
