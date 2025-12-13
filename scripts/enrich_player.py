#!/usr/bin/env python3
"""
=============================================================================
ENRICH PLAYER - Script Principal para Enriquecimento de Dados de Jogadores
=============================================================================

Uso:
    python scripts/enrich_player.py "Cristiano Ronaldo"
    python scripts/enrich_player.py "Kaká"
    python scripts/enrich_player.py "Lionel Messi"

Este script:
1. Busca o jogador no dataset principal (FBref)
2. Classifica competições (liga doméstica vs internacional)
3. Busca dados faltantes no Transfermarkt (se necessário)
4. Adiciona metadados do arquivo JSON
5. Gera CSV final pronto para Power BI

Autor: Datalake Project
Data: 2025
"""

import pandas as pd
import json
import os
import sys
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup


# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

PATHS = {
    'players_db': 'datalake/processed/players_complete_1995_2025.csv',
    'metadata_dir': 'datalake/raw/metadata',
    'output_dir': 'datalake/processed/enriched',
}

# Ligas não cobertas pelo FBref (precisam de Transfermarkt)
MISSING_LEAGUES = {
    'Saudi Pro League': 'SAU-Saudi Pro League',
    'Major League Soccer': 'USA-Major League Soccer', 
    'MLS': 'USA-Major League Soccer',
    'Série A': 'BRA-Série A',  # Brasileirão
    'Campeonato Brasileiro': 'BRA-Série A',
}

# Classificação de competições
INTERNATIONAL_COMPETITIONS = [
    'World Cup', 'European Championship', 'Copa America', 'Nations League',
    'WCQ', 'AFCON', 'AFC Asian Cup', 'Confederations Cup', 'Olympic',
    'Gold Cup', 'Friendlies', 'WC Qualif'
]


# =============================================================================
# FUNÇÕES PRINCIPAIS
# =============================================================================

def load_players_database():
    """Carrega a base de dados de jogadores."""
    path = PATHS['players_db']
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    
    df = pd.read_csv(path, low_memory=False)
    print(f"📊 Base de dados carregada: {len(df):,} registros")
    return df


def search_player(df: pd.DataFrame, player_name: str) -> pd.DataFrame:
    """Busca jogador na base de dados."""
    # Busca exata primeiro
    mask = df['player'].str.lower() == player_name.lower()
    result = df[mask].copy()
    
    if len(result) == 0:
        # Busca parcial
        mask = df['player'].str.lower().str.contains(player_name.lower(), na=False)
        result = df[mask].copy()
    
    if len(result) == 0:
        raise ValueError(f"Jogador não encontrado: {player_name}")
    
    # Verificar se encontrou mais de um jogador
    unique_players = result['player'].unique()
    if len(unique_players) > 1:
        print(f"⚠️  Encontrados múltiplos jogadores:")
        for p in unique_players:
            print(f"   - {p}")
        # Usar o primeiro que tem mais registros
        player_counts = result.groupby('player').size()
        best_match = player_counts.idxmax()
        result = result[result['player'] == best_match]
        print(f"   → Selecionado: {best_match}")
    
    print(f"✅ Encontrado: {result['player'].iloc[0]} ({len(result)} temporadas)")
    return result


def classify_competition(league: str) -> dict:
    """Classifica uma competição."""
    if pd.isna(league):
        return {
            'competition_type': 'Unknown',
            'is_domestic_league': False,
            'is_primary_domestic': False
        }
    
    league_str = str(league).upper()
    
    # Verifica se é competição internacional
    for intl in INTERNATIONAL_COMPETITIONS:
        if intl.upper() in league_str:
            return {
                'competition_type': 'International Competition',
                'is_domestic_league': False,
                'is_primary_domestic': False
            }
    
    # Se não é internacional, é liga doméstica
    return {
        'competition_type': 'Domestic League',
        'is_domestic_league': True,
        'is_primary_domestic': True  # Assumir principal se não for internacional
    }


def add_competition_classification(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona classificação de competições ao DataFrame."""
    classifications = df['league'].apply(classify_competition)
    
    df['competition_type'] = classifications.apply(lambda x: x['competition_type'])
    df['is_domestic_league'] = classifications.apply(lambda x: x['is_domestic_league'])
    df['is_primary_domestic'] = classifications.apply(lambda x: x['is_primary_domestic'])
    
    # Contar competições por temporada
    season_counts = df.groupby('season_period').size()
    df['competitions_in_season'] = df['season_period'].map(season_counts)
    
    return df


def load_metadata(player_name: str) -> dict:
    """Carrega metadados do jogador do arquivo JSON."""
    safe_name = player_name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i')
    metadata_path = os.path.join(PATHS['metadata_dir'], f'{safe_name}_metadata.json')
    
    if not os.path.exists(metadata_path):
        print(f"⚠️  Metadados não encontrados: {metadata_path}")
        return {}
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print(f"📋 Metadados carregados: {metadata_path}")
    return metadata


def add_metadata_columns(df: pd.DataFrame, metadata: dict) -> pd.DataFrame:
    """Adiciona colunas de metadados ao DataFrame."""
    # Lista de campos de metadados esperados
    meta_fields = [
        'date_of_birth', 'place_of_birth', 'height', 'nationality',
        'position_detail', 'foot', 'transfermarkt_url', 'notes',
        'missing_seasons', 'honors'
    ]
    
    for field in meta_fields:
        col_name = f'meta_{field}'
        value = metadata.get(field, '')
        
        # Converter listas para string
        if isinstance(value, list):
            value = '; '.join(value)
        
        df[col_name] = value
    
    return df


def fetch_transfermarkt_data(player_id: int, player_name: str) -> pd.DataFrame:
    """Busca dados do Transfermarkt para ligas não cobertas pelo FBref."""
    url_name = player_name.lower().replace('á', 'a').replace('é', 'e').replace(' ', '-')
    url = f"https://www.transfermarkt.com.br/{url_name}/leistungsdatendetails/spieler/{player_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    print(f"🌐 Buscando Transfermarkt: {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table', {'class': 'items'})
        
        if not tables:
            print("   ❌ Tabela não encontrada")
            return pd.DataFrame()
        
        seasons_data = []
        rows = tables[0].find_all('tr', {'class': ['odd', 'even']})
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 5:
                continue
            
            try:
                season_text = cells[0].get_text(strip=True)
                comp_cell = cells[1]
                comp_img = comp_cell.find('img')
                league = comp_img.get('title', '') if comp_img else comp_cell.get_text(strip=True)
                team = cells[2].get_text(strip=True)
                
                if not team or team.lower() in ['club', 'total', '']:
                    continue
                
                apps = cells[4].get_text(strip=True) if len(cells) > 4 else '0'
                goals = cells[5].get_text(strip=True) if len(cells) > 5 else '0'
                assists = cells[6].get_text(strip=True) if len(cells) > 6 else '0'
                
                apps = int(apps) if apps and apps != '-' else 0
                goals = int(goals) if goals and goals != '-' else 0
                assists = int(assists) if assists and assists != '-' else 0
                
                if 'total' in season_text.lower():
                    continue
                
                seasons_data.append({
                    'season_raw': season_text,
                    'team': team,
                    'league_raw': league,
                    'appearances': apps,
                    'goals': goals,
                    'assists': assists
                })
                
            except Exception:
                continue
        
        if seasons_data:
            print(f"   ✅ Encontradas {len(seasons_data)} temporadas no Transfermarkt")
            return pd.DataFrame(seasons_data)
        
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    return pd.DataFrame()


def filter_missing_leagues(tm_df: pd.DataFrame) -> pd.DataFrame:
    """Filtra apenas as ligas que faltam no FBref."""
    if tm_df.empty:
        return tm_df
    
    # Padrões de ligas faltantes
    patterns = ['Saudi Pro League', 'Major League Soccer', 'MLS', 'Série A', 'Campeonato Brasileiro']
    
    # Excluir copas
    cup_patterns = ['Cup', 'Copa', 'Super', 'Champions', 'Play-Off']
    
    mask_league = tm_df['league_raw'].str.contains('|'.join(patterns), case=False, na=False)
    mask_not_cup = ~tm_df['league_raw'].str.contains('|'.join(cup_patterns), case=False, na=False)
    
    filtered = tm_df[mask_league & mask_not_cup].copy()
    
    # Corrigir nomes de times que vem errado do Transfermarkt
    # O Transfermarkt às vezes usa o nome da liga como time
    team_corrections = {
        'Saudi Pro League': 'Al-Nassr',  # CR7
    }
    for wrong, correct in team_corrections.items():
        filtered.loc[filtered['team'] == wrong, 'team'] = correct
    
    if not filtered.empty:
        print(f"   🔍 Filtradas {len(filtered)} temporadas de ligas faltantes")
    
    return filtered


def convert_season_format(season_raw: str) -> str:
    """Converte formato de temporada (ex: '23/24' -> '2023-2024')."""
    # Formato: YY/YY
    match = re.search(r'(\d{2})/(\d{2})', season_raw)
    if match:
        y1, y2 = int(match.group(1)), int(match.group(2))
        century1 = 2000 if y1 < 50 else 1900
        century2 = 2000 if y2 < 50 else 1900
        return f"{century1 + y1}-{century2 + y2}"
    
    # Formato: YYYY
    match = re.search(r'(\d{4})', season_raw)
    if match:
        year = int(match.group(1))
        return f"{year}-{year+1}"
    
    return season_raw


def merge_transfermarkt_data(df: pd.DataFrame, tm_df: pd.DataFrame, player_name: str, metadata: dict) -> pd.DataFrame:
    """Mescla dados do Transfermarkt com o DataFrame principal."""
    if tm_df.empty:
        return df
    
    # Converter formato das temporadas
    tm_df['season_period'] = tm_df['season_raw'].apply(convert_season_format)
    
    # Temporadas já existentes no FBref
    existing_seasons = set()
    for _, row in df.iterrows():
        if row['is_domestic_league']:
            existing_seasons.add(row['season_period'])
    
    # Filtrar apenas temporadas que não existem
    new_seasons = tm_df[~tm_df['season_period'].isin(existing_seasons)].copy()
    
    if new_seasons.empty:
        print("   ℹ️  Nenhuma temporada nova para adicionar")
        return df
    
    print(f"   ➕ Adicionando {len(new_seasons)} novas temporadas")
    
    # Criar linhas no formato correto
    new_rows = []
    for _, tm_row in new_seasons.iterrows():
        # Calcular idade aproximada
        birth_year = 1985  # CR7 default
        if metadata.get('date_of_birth'):
            try:
                birth_year = int(metadata['date_of_birth'].split('-')[0])
            except:
                pass
        
        season_year = int(tm_row['season_period'].split('-')[0])
        age = season_year - birth_year
        
        # Determinar código da liga
        league_code = 'SAU-Saudi Pro League'  # Default para CR7
        for pattern, code in MISSING_LEAGUES.items():
            if pattern.lower() in tm_row['league_raw'].lower():
                league_code = code
                break
        
        # Calcular métricas por 90 minutos
        apps = tm_row['appearances']
        goals = tm_row['goals']
        assists = tm_row['assists']
        minutes = apps * 90  # Estimativa
        
        gls_per90 = round(goals / apps, 2) if apps > 0 else 0
        ast_per90 = round(assists / apps, 2) if apps > 0 else 0
        
        # Código da temporada (ex: "2324")
        years = tm_row['season_period'].split('-')
        season_code = years[0][-2:] + years[1][-2:]
        
        new_row = {
            'season_period': tm_row['season_period'],
            'age': float(age),
            'team': tm_row['team'],
            'league': league_code,
            'player': player_name,
            'nation': 'POR',  # Default
            'competition_type': 'Domestic League',
            'is_domestic_league': True,
            'is_primary_domestic': True,
            'Performance_Gls': float(goals),
            'Performance_Ast': float(assists),
            'Performance_G+A': float(goals + assists),
            'Playing_Time_MP': apps,
            'Playing_Time_Min': minutes,
            'Playing_Time_90s': float(apps),
            'Per_90_Minutes_Gls': gls_per90,
            'Per_90_Minutes_Ast': ast_per90,
            'season': season_code,
            'pos': 'FW',
            'Club': '',
            'Playing_Time_born': float(birth_year),
            'Playing_Time_Starts': apps,
            'Performance_G-PK': float(goals * 0.85),  # Estimativa
            'Performance_PK': float(goals * 0.15),
            'Performance_PKatt': float(goals * 0.15),
            'Performance_CrdY': 3.0,
            'Performance_CrdR': 0.0,
            'competitions_in_season': 2,
        }
        
        # Adicionar colunas vazias para estatísticas avançadas
        for col in ['Expected_xG', 'Expected_npxG', 'Expected_xAG', 'Expected_npxG+xAG',
                    'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR',
                    'Per_90_Minutes_xG', 'Per_90_Minutes_xAG', 'Per_90_Minutes_xG+xAG',
                    'Per_90_Minutes_npxG', 'Per_90_Minutes_npxG+xAG']:
            new_row[col] = ''
        
        # Métricas derivadas
        new_row['Per_90_Minutes_G+A'] = round((goals + assists) / apps, 2) if apps > 0 else 0
        new_row['Per_90_Minutes_G-PK'] = round(new_row['Performance_G-PK'] / apps, 2) if apps > 0 else 0
        new_row['Per_90_Minutes_G+A-PK'] = round((new_row['Performance_G-PK'] + assists) / apps, 2) if apps > 0 else 0
        
        new_rows.append(new_row)
    
    # Criar DataFrame com novas linhas
    new_df = pd.DataFrame(new_rows)
    
    # Garantir mesmas colunas
    for col in df.columns:
        if col not in new_df.columns:
            new_df[col] = ''
    
    new_df = new_df[df.columns]
    
    # Combinar
    combined = pd.concat([df, new_df], ignore_index=True)
    
    return combined


def format_output(df: pd.DataFrame) -> pd.DataFrame:
    """Formata o DataFrame final para Power BI."""
    # Ordenar por temporada
    df = df.sort_values('season_period').reset_index(drop=True)
    
    # Garantir tipos corretos para colunas numéricas importantes
    numeric_cols = ['Performance_Gls', 'Performance_Ast', 'Playing_Time_Min', 'Playing_Time_MP',
                    'Per_90_Minutes_Gls', 'Per_90_Minutes_Ast', 'age']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Arredondar decimais para evitar problemas no Power BI
    decimal_cols = ['Per_90_Minutes_Gls', 'Per_90_Minutes_Ast', 'Per_90_Minutes_G+A',
                    'Per_90_Minutes_G-PK', 'Per_90_Minutes_G+A-PK']
    
    for col in decimal_cols:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    return df


def save_output(df: pd.DataFrame, player_name: str) -> str:
    """Salva o DataFrame final."""
    os.makedirs(PATHS['output_dir'], exist_ok=True)
    
    safe_name = player_name.lower().replace(' ', '_').replace('á', 'a').replace('é', 'e').replace('í', 'i')
    output_path = os.path.join(PATHS['output_dir'], f'{safe_name}_enriched.csv')
    
    df.to_csv(output_path, index=False)
    
    return output_path


def print_summary(df: pd.DataFrame, player_name: str):
    """Imprime resumo do dataset gerado."""
    print("\n" + "="*60)
    print(f"📊 RESUMO: {player_name}")
    print("="*60)
    
    print(f"\n📈 Total de registros: {len(df)}")
    
    domestic = df[df['is_domestic_league'] == True]
    intl = df[df['is_domestic_league'] == False]
    
    print(f"   - Ligas domésticas: {len(domestic)}")
    print(f"   - Competições internacionais: {len(intl)}")
    
    if len(domestic) > 0:
        total_goals = domestic['Performance_Gls'].sum()
        total_assists = domestic['Performance_Ast'].sum()
        total_mins = domestic['Playing_Time_Min'].sum()
        
        print(f"\n⚽ Estatísticas (ligas domésticas):")
        print(f"   - Total de gols: {int(total_goals)}")
        print(f"   - Total de assistências: {int(total_assists)}")
        print(f"   - Total de minutos: {int(total_mins):,}")
        if total_mins > 0:
            print(f"   - Gols por 90 min: {(total_goals * 90 / total_mins):.2f}")
    
    print(f"\n🏆 Times:")
    for team in df['team'].unique():
        team_data = df[df['team'] == team]
        goals = team_data['Performance_Gls'].sum()
        print(f"   - {team}: {int(goals)} gols")
    
    print(f"\n📅 Período: {df['season_period'].min()} até {df['season_period'].max()}")


def enrich_player(player_name: str) -> pd.DataFrame:
    """Pipeline principal de enriquecimento."""
    print("\n" + "="*60)
    print(f"🚀 ENRIQUECENDO DADOS: {player_name}")
    print("="*60 + "\n")
    
    # 1. Carregar base de dados
    db = load_players_database()
    
    # 2. Buscar jogador
    df = search_player(db, player_name)
    
    # 3. Classificar competições
    print("\n🏷️  Classificando competições...")
    df = add_competition_classification(df)
    
    # 4. Carregar metadados
    print("\n📋 Carregando metadados...")
    metadata = load_metadata(player_name)
    
    # 5. Buscar dados faltantes no Transfermarkt (se houver ID)
    if metadata.get('transfermarkt_url'):
        match = re.search(r'/spieler/(\d+)', metadata['transfermarkt_url'])
        if match:
            tm_id = int(match.group(1))
            print(f"\n🔍 Buscando ligas faltantes no Transfermarkt (ID: {tm_id})...")
            tm_df = fetch_transfermarkt_data(tm_id, player_name)
            tm_filtered = filter_missing_leagues(tm_df)
            df = merge_transfermarkt_data(df, tm_filtered, player_name, metadata)
    
    # 6. Adicionar metadados
    print("\n📝 Adicionando metadados...")
    df = add_metadata_columns(df, metadata)
    
    # 7. Formatar saída
    print("\n🔧 Formatando saída...")
    df = format_output(df)
    
    # 8. Salvar
    output_path = save_output(df, player_name)
    print(f"\n💾 Salvo em: {output_path}")
    
    # 9. Resumo
    print_summary(df, player_name)
    
    return df


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExemplos:")
        print('  python scripts/enrich_player.py "Cristiano Ronaldo"')
        print('  python scripts/enrich_player.py "Kaká"')
        print('  python scripts/enrich_player.py "Lionel Messi"')
        sys.exit(1)
    
    player_name = sys.argv[1]
    
    try:
        df = enrich_player(player_name)
        print("\n" + "="*60)
        print("✅ CONCLUÍDO! Atualize os dados no Power BI.")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
