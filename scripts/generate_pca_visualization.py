"""
Generate 2D PCA projections for cluster visualization in Power BI
Creates scatter plot coordinates for players and teams
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

print("🎨 Generating PCA coordinates for cluster visualization...\n")

# ========================================
# 1. LOAD DATA
# ========================================
players_complete = pd.read_csv('datalake/processed/players_complete_1995_2025.csv')
players_clustered = pd.read_csv('datalake/processed/enriched/players_clustered.csv')
squads = pd.read_csv('datalake/processed/squads_complete.csv')
teams_complete = pd.read_csv('datalake/processed/teams_complete_1995_2025.csv')

print(f"✅ Loaded {len(players_complete):,} player records")
print(f"✅ Loaded {len(squads):,} squad records")
print(f"✅ Loaded {len(teams_complete):,} team records\n")

# ========================================
# 2. PLAYER PCA (2D)
# ========================================
print("📊 Calculating Player PCA...")

# Select available features from dataset
player_features = [
    'Performance_Gls', 'Performance_Ast', 'Performance_G+A',
    'Expected_xG', 'Expected_npxG', 'Expected_xAG', 'Expected_npxG+xAG',
    'Per_90_Minutes_Gls', 'Per_90_Minutes_Ast', 'Per_90_Minutes_G+A',
    'Per_90_Minutes_xG', 'Per_90_Minutes_xAG', 'Per_90_Minutes_xG+xAG',
    'Per_90_Minutes_npxG', 'Per_90_Minutes_npxG+xAG',
    'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR',
    'Playing_Time_MP', 'Playing_Time_Starts', 'Playing_Time_90s'
]

# Filter and prepare data
player_data = players_complete[['player', 'Club', 'pos', 'age'] + player_features].copy()
player_data = player_data.dropna(subset=player_features)

# Normalize
scaler = StandardScaler()
player_scaled = scaler.fit_transform(player_data[player_features])

# PCA to 2D
pca_player = PCA(n_components=2)
player_pca = pca_player.fit_transform(player_scaled)

# Normalize PCA values to 0-100 scale for easier interpretation
pca_x_min_p, pca_x_max_p = player_pca[:, 0].min(), player_pca[:, 0].max()
pca_y_min_p, pca_y_max_p = player_pca[:, 1].min(), player_pca[:, 1].max()

pca_x_normalized_p = 100 * (player_pca[:, 0] - pca_x_min_p) / (pca_x_max_p - pca_x_min_p)
pca_y_normalized_p = 100 * (player_pca[:, 1] - pca_y_min_p) / (pca_y_max_p - pca_y_min_p)

# Create output dataframe
player_viz = pd.DataFrame({
    'player': player_data['player'].values,
    'Club': player_data['Club'].values,
    'pos': player_data['pos'].values,
    'age': player_data['age'].values,
    'pca_x': pca_x_normalized_p,
    'pca_y': pca_y_normalized_p,
    'goals': player_data['Performance_Gls'].values,
    'assists': player_data['Performance_Ast'].values
})

# Merge with cluster assignments
player_viz = player_viz.merge(
    players_clustered[['player', 'player_cluster']], 
    on='player', 
    how='left'
)

print(f"✅ Player PCA: {len(player_viz):,} players")
print(f"   Explained variance: {pca_player.explained_variance_ratio_.sum():.2%}\n")

# ========================================
# 3. TEAM PCA (2D)
# ========================================
print("📊 Calculating Team PCA...")

# Team features - using available columns
team_features = [
    'Performance_Gls', 'Performance_Ast', 'Performance_G+A',
    'Expected_xG', 'Expected_npxG', 'Expected_xAG',
    'Progression_PrgC', 'Progression_PrgP', 'Progression_PrgR',
    'Per_90_Minutes_Gls', 'Per_90_Minutes_xG'
]

# Get latest season data per team
teams_2025 = teams_complete[teams_complete['season_period'] == '2025-2026'].copy()

print(f"   Found {len(teams_2025)} teams for 2025-2026 season")

# If no 2025-2026, try latest available
if len(teams_2025) == 0:
    print("   No 2025-2026 data, using latest season...")
    latest_season = teams_complete['season_period'].max()
    teams_2025 = teams_complete[teams_complete['season_period'] == latest_season].copy()
    print(f"   Using {latest_season}: {len(teams_2025)} teams")

team_data = teams_2025[['team'] + team_features].copy()
team_data = team_data.dropna(subset=team_features)

# Normalize
scaler_team = StandardScaler()
team_scaled = scaler_team.fit_transform(team_data[team_features])

# PCA to 2D
pca_team = PCA(n_components=2)
team_pca = pca_team.fit_transform(team_scaled)

# Normalize PCA values to 0-100 scale for easier interpretation
pca_x_min, pca_x_max = team_pca[:, 0].min(), team_pca[:, 0].max()
pca_y_min, pca_y_max = team_pca[:, 1].min(), team_pca[:, 1].max()

pca_x_normalized = 100 * (team_pca[:, 0] - pca_x_min) / (pca_x_max - pca_x_min)
pca_y_normalized = 100 * (team_pca[:, 1] - pca_y_min) / (pca_y_max - pca_y_min)

# Create output dataframe
team_viz = pd.DataFrame({
    'team': team_data['team'].values,
    'pca_x': pca_x_normalized,
    'pca_y': pca_y_normalized,
    'avg_goals': team_data['Performance_Gls'].values,
    'avg_xG': team_data['Expected_xG'].values,
    'progression_total': (team_data['Progression_PrgC'].values + 
                         team_data['Progression_PrgP'].values + 
                         team_data['Progression_PrgR'].values)
})

print(f"✅ Team PCA: {len(team_viz):,} teams")
print(f"   Explained variance: {pca_team.explained_variance_ratio_.sum():.2%}")
print(f"   PCA values normalized to 0-100 scale\n")

# ========================================
# 4. CALCULATE TEAM CLUSTERS
# ========================================
print("🎯 Assigning team clusters...")

from sklearn.cluster import KMeans

# Cluster teams by style
kmeans_team = KMeans(n_clusters=4, random_state=42, n_init=10)
team_viz['team_cluster'] = kmeans_team.fit_predict(team_scaled)

# Define cluster names based on characteristics
cluster_names = {
    0: "Posse e Controle",
    1: "Pressão Alta",
    2: "Transição Rápida", 
    3: "Equilíbrio Tático"
}

team_viz['cluster_name'] = team_viz['team_cluster'].map(cluster_names)

print(f"✅ Teams clustered into {len(cluster_names)} tactical styles\n")

# ========================================
# 5. SAVE OUTPUTS
# ========================================
print("💾 Saving visualization files...")

# Save player PCA
player_viz.to_csv('datalake/processed/enriched/players_pca_viz.csv', index=False)
print(f"✅ Saved: players_pca_viz.csv ({len(player_viz):,} records)")

# Save team PCA
team_viz.to_csv('datalake/processed/enriched/teams_pca_viz.csv', index=False)
print(f"✅ Saved: teams_pca_viz.csv ({len(team_viz):,} records)")

print("\n" + "="*60)
print("🎨 POWER BI VISUALIZATION GUIDE")
print("="*60)

print("""
📊 SCATTER PLOT DE TIMES (PASSO A PASSO):

1. Novo Visual → Scatter Chart
2. Arraste os campos:
   - X Axis: pca_x (0-100 scale)
   - Y Axis: pca_y (0-100 scale)
   - Legend: cluster_name
   - Details: team
   - Size: avg_goals ou progression_total
   - Tooltips: team, cluster_name, avg_goals, avg_xG

3. ⭐ ATIVAR DATA LABELS (importante!):
   - Vá em "Format visual" (pincel)
   - Expanda "Data labels"
   - Ative o switch ON
   - Em "Values", selecione "team"
   - Ajuste tamanho da fonte (10-12pt)

4. Melhorar visualização:
   - Em "Legend", posicione direita ou topo
   - Em "X axis", defina Min=0, Max=100
   - Em "Y axis", defina Min=0, Max=100
   - Em "Markers", aumente o tamanho base

Resultado: Times com NOMES VISÍVEIS separados por estilo!

---

📊 SCATTER PLOT DE JOGADORES:

1. Novo Visual → Scatter Chart
2. Eixos:
   - X Axis: pca_x (0-100)
   - Y Axis: pca_y (0-100)
   - Legend: player_cluster
   - Details: player
   - Size: goals (bolhas = mais goleadores)
   - Tooltips: player, Club, pos, age, goals, assists

3. ⭐ DATA LABELS (opcional - pode ficar poluído):
   - Filtre top 20 jogadores (slicer por goals)
   - Ative data labels só pra esses

---

💡 INTERPRETAÇÃO DOS EIXOS (0-100):

PCA_X e PCA_Y são agora escala 0-100 (normalizada):
- 0 = mínimo valor no componente principal
- 100 = máximo valor no componente principal

Valores representam combinação de múltiplas estatísticas:
- Gols, assistências, xG
- Progressão (carrinho, passe, recepção)
- Eficiência per 90

Times/jogadores próximos = perfis estatísticos similares
Times/jogadores distantes = perfis muito diferentes

---

🎯 CLUSTERS DE TIMES:

🔵 Posse e Controle - Times dominadores
🟣 Pressão Alta - Times agressivos
🟠 Transição Rápida - Times contra-ataque
🔴 Equilíbrio Tático - Times balanceados
""")

print("\n✅ Arquivos prontos para importar no Power BI!")
