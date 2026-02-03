#!/usr/bin/env python3
"""
Script de génération de graphiques - TP3 Bucket Sort
Génère les graphiques de performance à partir des résultats CSV
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Configuration
RESULTS_DIR = '../results'
PLOTS_DIR = '../plots'
os.makedirs(PLOTS_DIR, exist_ok=True)

# Style - use a compatible style
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('ggplot')

colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']

# ============================================================
# Chargement des données
# ============================================================
print("Chargement des données...")

seq_df = pd.read_csv(f'{RESULTS_DIR}/sequential_results.csv')
par_df = pd.read_csv(f'{RESULTS_DIR}/parallel_results.csv')

print(f"  ✓ {len(seq_df)} résultats séquentiels")
print(f"  ✓ {len(par_df)} résultats parallèles")

sizes = par_df['N'].unique()
procs = par_df['Processus'].unique()

# ============================================================
# Graphique 1: Temps d'exécution total (échelle log)
# ============================================================
print("\nGénération du graphique 1: Temps d'exécution...")
fig, ax = plt.subplots(figsize=(10, 6))

# Temps séquentiel
ax.plot(seq_df['N'], seq_df['Temps_Total'], 'o-', linewidth=2, markersize=8,
        label='Séquentiel', color='black')

# Temps parallèles
for i, p in enumerate(procs):
    data = par_df[par_df['Processus'] == p]
    ax.plot(data['N'], data['Temps_Total'], 'o-', linewidth=2, markersize=8,
            label=f'{p} processus', color=colors[i])

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Nombre d\'éléments (N)', fontsize=12)
ax.set_ylabel('Temps d\'exécution (s)', fontsize=12)
ax.set_title('TP3 - Temps d\'exécution Bucket Sort', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{PLOTS_DIR}/execution_time.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Graphique sauvegardé: {PLOTS_DIR}/execution_time.png")
plt.close()

# ============================================================
# Graphique 2: Speedup (utilise P=1 comme baseline)
# ============================================================
print("\nGénération du graphique 2: Speedup...")
fig, ax = plt.subplots(figsize=(10, 6))

for i, size in enumerate(sizes):
    # Utiliser P=1 comme baseline pour un speedup plus réaliste
    baseline_time = par_df[(par_df['N'] == size) & (par_df['Processus'] == 1)]['Temps_Total'].values[0]
    par_times = par_df[par_df['N'] == size].sort_values('Processus')
    
    speedups = baseline_time / par_times['Temps_Total'].values
    
    ax.plot(par_times['Processus'].values, speedups, 'o-', linewidth=2, markersize=8,
            label=f'N = {size:,}', color=colors[i])

# Speedup idéal
ax.plot(procs, procs, 'k--', linewidth=2, alpha=0.5, label='Speedup idéal')

ax.set_xlabel('Nombre de processus', fontsize=12)
ax.set_ylabel('Speedup (S = T₁/Tₚ)', fontsize=12)
ax.set_title('TP3 - Speedup du Bucket Sort Parallèle', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xticks(procs)
ax.set_ylim([0, max(procs) + 1])

plt.tight_layout()
plt.savefig(f'{PLOTS_DIR}/speedup.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Graphique sauvegardé: {PLOTS_DIR}/speedup.png")
plt.close()

# ============================================================
# Graphique 3: Efficacité
# ============================================================
print("\nGénération du graphique 3: Efficacité...")
fig, ax = plt.subplots(figsize=(10, 6))

for i, size in enumerate(sizes):
    # Utiliser P=1 comme baseline
    baseline_time = par_df[(par_df['N'] == size) & (par_df['Processus'] == 1)]['Temps_Total'].values[0]
    par_times = par_df[par_df['N'] == size].sort_values('Processus')
    
    speedups = baseline_time / par_times['Temps_Total'].values
    efficiency = (speedups / par_times['Processus'].values) * 100
    
    ax.plot(par_times['Processus'].values, efficiency, 'o-', linewidth=2, markersize=8,
            label=f'N = {size:,}', color=colors[i])

# Efficacité idéale (100%)
ax.axhline(y=100, color='k', linestyle='--', linewidth=2, alpha=0.5, label='Efficacité idéale')

ax.set_xlabel('Nombre de processus', fontsize=12)
ax.set_ylabel('Efficacité (%)', fontsize=12)
ax.set_title('TP3 - Efficacité Parallèle (E = S/p × 100%)', fontsize=14, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
ax.set_xticks(procs)
ax.set_ylim([0, 120])

plt.tight_layout()
plt.savefig(f'{PLOTS_DIR}/efficiency.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Graphique sauvegardé: {PLOTS_DIR}/efficiency.png")
plt.close()

# ============================================================
# Graphique 4: Décomposition du temps (N=1000000)
# ============================================================
print("\nGénération du graphique 4: Décomposition du temps...")
N_TARGET = 1000000
data_target = par_df[par_df['N'] == N_TARGET].sort_values('Processus')

fig, ax = plt.subplots(figsize=(10, 6))

# Composantes du temps
components = ['Temps_Scatter', 'Temps_LocalSort', 'Temps_Sample', 
              'Temps_AlltoAll', 'Temps_Merge', 'Temps_Gather']
labels = ['Scatter', 'Tri local', 'Échantillonnage', 
          'All-to-All', 'Merge', 'Gather']

x = np.arange(len(data_target))
width = 0.12

for i, (comp, label) in enumerate(zip(components, labels)):
    times = data_target[comp].values
    ax.bar(x + i*width, times, width, label=label, color=colors[i])

ax.set_xlabel('Nombre de processus', fontsize=12)
ax.set_ylabel('Temps (s)', fontsize=12)
ax.set_title(f'TP3 - Décomposition du temps (N = {N_TARGET:,})', 
             fontsize=14, fontweight='bold')
ax.set_xticks(x + width * 2.5)
ax.set_xticklabels(data_target['Processus'].values)
ax.legend(fontsize=9, loc='upper right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(f'{PLOTS_DIR}/time_breakdown.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Graphique sauvegardé: {PLOTS_DIR}/time_breakdown.png")
plt.close()

# ============================================================
# Graphique 5: Scalabilité forte (N=10000000)
# ============================================================
print("\nGénération du graphique 5: Scalabilité forte...")
N_STRONG = 10000000
data_strong = par_df[par_df['N'] == N_STRONG].sort_values('Processus')
# Utiliser P=1 parallèle comme baseline
baseline_strong = data_strong[data_strong['Processus'] == 1]['Temps_Total'].values[0]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Temps d'exécution
ax1.plot(data_strong['Processus'], data_strong['Temps_Total'], 
         'o-', linewidth=2, markersize=8, color=colors[0], label='Temps mesuré')
ax1.axhline(y=baseline_strong, color='gray', linestyle=':', linewidth=2, 
            alpha=0.7, label=f'Baseline P=1 ({baseline_strong:.4f}s)')
ax1.set_xlabel('Nombre de processus', fontsize=12)
ax1.set_ylabel('Temps d\'exécution (s)', fontsize=12)
ax1.set_title('Temps d\'exécution vs Processus', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xticks(data_strong['Processus'])

# Speedup
speedups_strong = baseline_strong / data_strong['Temps_Total'].values
ax2.plot(data_strong['Processus'], speedups_strong, 
         'o-', linewidth=2, markersize=8, color=colors[1], label='Speedup mesuré')
ax2.plot(data_strong['Processus'], data_strong['Processus'], 
         'k--', linewidth=2, alpha=0.5, label='Speedup idéal')
ax2.set_xlabel('Nombre de processus', fontsize=12)
ax2.set_ylabel('Speedup', fontsize=12)
ax2.set_title(f'Speedup (N = {N_STRONG:,})', fontsize=12, fontweight='bold')
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3)
ax2.set_xticks(data_strong['Processus'])

plt.suptitle('TP3 - Analyse de Scalabilité Forte', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(f'{PLOTS_DIR}/strong_scaling.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Graphique sauvegardé: {PLOTS_DIR}/strong_scaling.png")
plt.close()

# ============================================================
# Affichage du résumé des speedups
# ============================================================
print("\n" + "="*60)
print("RÉSUMÉ DES PERFORMANCES")
print("="*60)

for size in sizes:
    baseline = par_df[(par_df['N'] == size) & (par_df['Processus'] == 1)]['Temps_Total'].values[0]
    print(f"\nN = {size:,}:")
    for p in procs:
        t = par_df[(par_df['N'] == size) & (par_df['Processus'] == p)]['Temps_Total'].values[0]
        speedup = baseline / t
        efficiency = (speedup / p) * 100
        print(f"  P={p}: {t:.4f}s, Speedup={speedup:.2f}×, Efficacité={efficiency:.1f}%")

print("\n" + "="*60)
print("Génération terminée!")
print(f"Tous les graphiques sont sauvegardés dans: {PLOTS_DIR}/")
print("="*60)
