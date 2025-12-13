#!/usr/bin/env python3
"""
Validação da estrutura do datalake.
Verifica se todos os arquivos necessários estão presentes e válidos.
"""

import os
import sys
from pathlib import Path
import pandas as pd

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_file(path, name):
    """Verifica se um arquivo existe."""
    if os.path.exists(path):
        size = os.path.getsize(path)
        size_mb = size / (1024 * 1024)
        print(f"  {Colors.GREEN}✓{Colors.END} {name} ({size_mb:.2f} MB)")
        return True
    else:
        print(f"  {Colors.RED}✗{Colors.END} {name} - FALTANDO")
        return False

def check_csv(path, name, min_rows=0):
    """Verifica CSV e conta linhas."""
    if not os.path.exists(path):
        print(f"  {Colors.RED}✗{Colors.END} {name} - FALTANDO")
        return False
    
    try:
        df = pd.read_csv(path, nrows=10, encoding='utf-8', low_memory=False)  # Ler apenas primeiras linhas
        total_rows = sum(1 for _ in open(path, encoding='utf-8', errors='ignore')) - 1  # Contar linhas
        cols = len(df.columns)
        
        if total_rows >= min_rows:
            print(f"  {Colors.GREEN}✓{Colors.END} {name} ({total_rows:,} linhas, {cols} colunas)")
            return True
        else:
            print(f"  {Colors.YELLOW}⚠{Colors.END} {name} ({total_rows} linhas - esperado >={min_rows})")
            return True
    except Exception as e:
        print(f"  {Colors.RED}✗{Colors.END} {name} - ERRO: {e}")
        return False

def main():
    print("\n" + "="*60)
    print(f"{Colors.BLUE}🔍 VALIDAÇÃO DO DATALAKE{Colors.END}")
    print("="*60 + "\n")
    
    base_path = Path(__file__).parent.parent
    os.chdir(base_path)
    
    all_ok = True
    
    # 1. Estrutura de diretórios
    print(f"{Colors.BLUE}📁 Estrutura de Diretórios{Colors.END}")
    dirs = [
        'datalake',
        'datalake/raw',
        'datalake/raw/metadata',
        'datalake/raw/matches',
        'datalake/raw/transfermarkt',
        'datalake/processed',
        'datalake/processed/enriched',
        'scripts',
        'docs',
    ]
    
    for d in dirs:
        if os.path.isdir(d):
            print(f"  {Colors.GREEN}✓{Colors.END} {d}/")
        else:
            print(f"  {Colors.RED}✗{Colors.END} {d}/ - FALTANDO")
            all_ok = False
    
    # 2. Arquivos principais
    print(f"\n{Colors.BLUE}📄 Arquivos Principais{Colors.END}")
    files = {
        'README.md': 'README.md',
        'requirements.txt': 'requirements.txt',
        'LICENSE': 'LICENSE',
        '.gitignore': '.gitignore',
    }
    
    for name, path in files.items():
        if not check_file(path, name):
            all_ok = False
    
    # 3. Scripts
    print(f"\n{Colors.BLUE}🔧 Scripts{Colors.END}")
    scripts = {
        'enrich_player.py': 'scripts/enrich_player.py',
        'deduplicate_player_data.py': 'scripts/deduplicate_player_data.py',
        'generate_players_teams_historical.py': 'scripts/generate_players_teams_historical.py',
    }
    
    for name, path in scripts.items():
        if not check_file(path, name):
            all_ok = False
    
    # 4. Datasets principais
    print(f"\n{Colors.BLUE}📊 Datasets Principais{Colors.END}")
    datasets = {
        'players_complete_1995_2025.csv': ('datalake/processed/players_complete_1995_2025.csv', 10000),
        'teams_complete_1995_2025.csv': ('datalake/processed/teams_complete_1995_2025.csv', 100),
        'cristiano_ronaldo_enriched.csv': ('datalake/processed/enriched/cristiano_ronaldo_enriched.csv', 30),
    }
    
    for name, (path, min_rows) in datasets.items():
        if not check_csv(path, name, min_rows):
            all_ok = False
    
    # 5. Documentação
    print(f"\n{Colors.BLUE}📚 Documentação{Colors.END}")
    docs = {
        'DATA_SOURCES.md': 'docs/DATA_SOURCES.md',
        'POWERBI_GUIDE.md': 'docs/POWERBI_GUIDE.md',
        'EXAMPLES.md': 'docs/EXAMPLES.md',
        'LINKEDIN_SHOWCASE.md': 'docs/LINKEDIN_SHOWCASE.md',
    }
    
    for name, path in docs.items():
        if not check_file(path, name):
            all_ok = False
    
    # 6. Validação de dados (sample)
    print(f"\n{Colors.BLUE}🔬 Validação de Dados{Colors.END}")
    
    try:
        df = pd.read_csv('datalake/processed/enriched/cristiano_ronaldo_enriched.csv')
        
        # Verificar colunas obrigatórias
        required_cols = ['season_period', 'team', 'league', 'Performance_Gls', 
                        'Per_90_Minutes_Gls', 'is_domestic_league']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            print(f"  {Colors.RED}✗{Colors.END} Colunas faltando: {missing_cols}")
            all_ok = False
        else:
            print(f"  {Colors.GREEN}✓{Colors.END} Todas as colunas obrigatórias presentes")
        
        # Verificar tipos de dados
        if df['Performance_Gls'].dtype in ['int64', 'float64']:
            print(f"  {Colors.GREEN}✓{Colors.END} Performance_Gls tem tipo numérico")
        else:
            print(f"  {Colors.RED}✗{Colors.END} Performance_Gls deveria ser numérico")
            all_ok = False
        
        # Verificar valores razoáveis
        max_goals = df['Performance_Gls'].max()
        if 0 <= max_goals <= 100:
            print(f"  {Colors.GREEN}✓{Colors.END} Gols máximos razoáveis ({max_goals})")
        else:
            print(f"  {Colors.YELLOW}⚠{Colors.END} Gols máximos suspeitos ({max_goals})")
        
        # Verificar Per_90_Minutes
        max_per90 = df['Per_90_Minutes_Gls'].max()
        if 0 <= max_per90 <= 3:
            print(f"  {Colors.GREEN}✓{Colors.END} Gols/90 razoáveis (max: {max_per90:.2f})")
        else:
            print(f"  {Colors.RED}✗{Colors.END} Gols/90 suspeitos (max: {max_per90:.2f})")
            all_ok = False
            
    except Exception as e:
        print(f"  {Colors.RED}✗{Colors.END} Erro ao validar dados: {e}")
        all_ok = False
    
    # Resumo final
    print("\n" + "="*60)
    if all_ok:
        print(f"{Colors.GREEN}✅ TUDO OK! Datalake pronto para produção.{Colors.END}")
        print("="*60 + "\n")
        return 0
    else:
        print(f"{Colors.RED}❌ Alguns problemas encontrados.{Colors.END}")
        print(f"{Colors.YELLOW}Revise os itens marcados acima.{Colors.END}")
        print("="*60 + "\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
