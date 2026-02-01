#!/usr/bin/env python3
"""
Script de visualisation des résultats du TP2
Génère des graphiques de performance à partir des données expérimentales
"""

import matplotlib.pyplot as plt
import numpy as np
import os

# Créer le répertoire plots s'il n'existe pas
os.makedirs('plots', exist_ok=True)

# Configuration du style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10

# Données expérimentales (extraites de tp2_results_20260127_110003.txt)
processes = np.array([1, 2, 4, 8])

# Temps de référence séquentiel
t_seq = 1.289

# Mandelbrot - Partition par blocs
block_times = np.array([1.312, 0.708, 0.415, 0.247])
block_speedup = t_seq / block_times
block_efficiency = (block_speedup / processes) * 100

# Mandelbrot - Répartition cyclique
cyclic_times = np.array([1.280, 0.698, 0.362, 0.210])
cyclic_speedup = t_seq / cyclic_times
cyclic_efficiency = (cyclic_speedup / processes) * 100

# Mandelbrot - Maître-Esclave (seulement 2, 4, 8 processus)
ms_processes = np.array([2, 4, 8])
ms_times = np.array([1.269, 0.453, 0.224])
ms_speedup = t_seq / ms_times
ms_efficiency = (ms_speedup / ms_processes) * 100

# Speedup idéal
ideal_speedup = processes

# ============================================================================
# Graphique 1 : Comparaison des Speedups
# ============================================================================
plt.figure(figsize=(10, 6))

plt.plot(processes, ideal_speedup, 'k--', linewidth=2, label='Idéal (linéaire)', alpha=0.7)
plt.plot(processes, block_speedup, 'o-', linewidth=2, markersize=8, label='Block', color='#e74c3c')
plt.plot(processes, cyclic_speedup, 's-', linewidth=2, markersize=8, label='Cyclique', color='#3498db')
plt.plot(ms_processes, ms_speedup, '^-', linewidth=2, markersize=8, label='Maître-Esclave', color='#2ecc71')

plt.xlabel('Nombre de processus', fontweight='bold')
plt.ylabel('Speedup', fontweight='bold')
plt.title('Comparaison des Speedups - Ensemble de Mandelbrot', fontweight='bold', pad=15)
plt.legend(loc='upper left', framealpha=0.9)
plt.grid(True, alpha=0.3)
plt.xlim(0.5, 8.5)
plt.ylim(0, 9)
plt.xticks(processes)

# Annotations pour les valeurs finales
for i, (p, s) in enumerate(zip(processes, block_speedup)):
    if p == 8:
        plt.annotate(f'{s:.2f}×', (p, s), textcoords="offset points", 
                    xytext=(10,-5), fontsize=9, color='#e74c3c')

for i, (p, s) in enumerate(zip(processes, cyclic_speedup)):
    if p == 8:
        plt.annotate(f'{s:.2f}×', (p, s), textcoords="offset points", 
                    xytext=(10,5), fontsize=9, color='#3498db', fontweight='bold')

for i, (p, s) in enumerate(zip(ms_processes, ms_speedup)):
    if p == 8:
        plt.annotate(f'{s:.2f}×', (p, s), textcoords="offset points", 
                    xytext=(10,5), fontsize=9, color='#2ecc71')

plt.tight_layout()
plt.savefig('plots/mandelbrot_speedup_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: plots/mandelbrot_speedup_comparison.png")
plt.close()

# ============================================================================
# Graphique 2 : Comparaison des Efficacités
# ============================================================================
plt.figure(figsize=(10, 6))

plt.plot(processes, np.ones_like(processes)*100, 'k--', linewidth=2, 
         label='Idéal (100%)', alpha=0.7)
plt.plot(processes, block_efficiency, 'o-', linewidth=2, markersize=8, 
         label='Block', color='#e74c3c')
plt.plot(processes, cyclic_efficiency, 's-', linewidth=2, markersize=8, 
         label='Cyclique', color='#3498db')
plt.plot(ms_processes, ms_efficiency, '^-', linewidth=2, markersize=8, 
         label='Maître-Esclave', color='#2ecc71')

plt.xlabel('Nombre de processus', fontweight='bold')
plt.ylabel('Efficacité (%)', fontweight='bold')
plt.title('Comparaison des Efficacités - Ensemble de Mandelbrot', fontweight='bold', pad=15)
plt.legend(loc='upper right', framealpha=0.9)
plt.grid(True, alpha=0.3)
plt.xlim(0.5, 8.5)
plt.ylim(0, 110)
plt.xticks(processes)

# Annotations
for i, (p, e) in enumerate(zip(processes, cyclic_efficiency)):
    if p == 8:
        plt.annotate(f'{e:.1f}%', (p, e), textcoords="offset points", 
                    xytext=(10,5), fontsize=9, color='#3498db', fontweight='bold')

plt.tight_layout()
plt.savefig('plots/mandelbrot_efficiency_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: plots/mandelbrot_efficiency_comparison.png")
plt.close()

# ============================================================================
# Graphique 3 : Temps d'exécution
# ============================================================================
plt.figure(figsize=(10, 6))

x = np.arange(len(processes))
width = 0.25

plt.bar(x - width, block_times, width, label='Block', color='#e74c3c', alpha=0.8)
plt.bar(x, cyclic_times, width, label='Cyclique', color='#3498db', alpha=0.8)
plt.bar(x[1:] + width, ms_times, width, label='Maître-Esclave', color='#2ecc71', alpha=0.8)

plt.xlabel('Nombre de processus', fontweight='bold')
plt.ylabel('Temps d\'exécution (s)', fontweight='bold')
plt.title('Temps d\'exécution - Ensemble de Mandelbrot', fontweight='bold', pad=15)
plt.xticks(x, processes)
plt.legend(framealpha=0.9)
plt.grid(True, alpha=0.3, axis='y')
plt.yscale('log')

# Annotations des valeurs
for i, (t, p) in enumerate(zip(block_times, processes)):
    plt.text(i - width, t, f'{t:.3f}s', ha='center', va='bottom', fontsize=8)
for i, (t, p) in enumerate(zip(cyclic_times, processes)):
    plt.text(i, t, f'{t:.3f}s', ha='center', va='bottom', fontsize=8, fontweight='bold')
for i, (t, p) in enumerate(zip(ms_times, ms_processes)):
    plt.text(i + 1 + width, t, f'{t:.3f}s', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('plots/mandelbrot_execution_time.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: plots/mandelbrot_execution_time.png")
plt.close()

# ============================================================================
# Graphique 4 : Équilibrage de charge (8 processus)
# ============================================================================
# Données des temps de calcul locaux pour 8 processus
block_8p_times = np.array([0.1796, 0.2466, 0.1723, 0.1624, 0.1615, 0.1974, 0.2084, 0.1807])
cyclic_8p_times = np.array([0.1841, 0.2045, 0.2102, 0.1823, 0.1746, 0.1832, 0.1784, 0.1811])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

processes_8 = np.arange(8)

# Block
ax1.bar(processes_8, block_8p_times, color='#e74c3c', alpha=0.7, edgecolor='black')
ax1.axhline(y=np.mean(block_8p_times), color='blue', linestyle='--', 
            linewidth=2, label=f'Moyenne: {np.mean(block_8p_times):.3f}s')
ax1.axhline(y=np.max(block_8p_times), color='red', linestyle=':', 
            linewidth=2, label=f'Max: {np.max(block_8p_times):.3f}s')
ax1.set_xlabel('Processus', fontweight='bold')
ax1.set_ylabel('Temps de calcul (s)', fontweight='bold')
ax1.set_title('Partition par Blocs', fontweight='bold')
ax1.set_xticks(processes_8)
ax1.set_xticklabels([f'P{i}' for i in range(8)])
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')
ax1.set_ylim(0, 0.27)

# Annotations
for i, t in enumerate(block_8p_times):
    ax1.text(i, t + 0.005, f'{t:.3f}', ha='center', fontsize=8)

# Écart-type
std_block = np.std(block_8p_times)
ax1.text(0.5, 0.25, f'σ = {std_block:.3f}s', fontsize=10, 
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Cyclique
ax2.bar(processes_8, cyclic_8p_times, color='#3498db', alpha=0.7, edgecolor='black')
ax2.axhline(y=np.mean(cyclic_8p_times), color='blue', linestyle='--', 
            linewidth=2, label=f'Moyenne: {np.mean(cyclic_8p_times):.3f}s')
ax2.axhline(y=np.max(cyclic_8p_times), color='red', linestyle=':', 
            linewidth=2, label=f'Max: {np.max(cyclic_8p_times):.3f}s')
ax2.set_xlabel('Processus', fontweight='bold')
ax2.set_ylabel('Temps de calcul (s)', fontweight='bold')
ax2.set_title('Répartition Cyclique', fontweight='bold')
ax2.set_xticks(processes_8)
ax2.set_xticklabels([f'P{i}' for i in range(8)])
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_ylim(0, 0.27)

# Annotations
for i, t in enumerate(cyclic_8p_times):
    ax2.text(i, t + 0.005, f'{t:.3f}', ha='center', fontsize=8)

# Écart-type
std_cyclic = np.std(cyclic_8p_times)
ax2.text(0.5, 0.25, f'σ = {std_cyclic:.3f}s', fontsize=10, 
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))

plt.suptitle('Équilibrage de charge - 8 processus', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('plots/load_balance_comparison_8proc.png', dpi=300, bbox_inches='tight')
print("✓ Graphique sauvegardé: plots/load_balance_comparison_8proc.png")
plt.close()

# ============================================================================
# Résumé des résultats
# ============================================================================
print("\n" + "="*70)
print("RÉSUMÉ DES PERFORMANCES - ENSEMBLE DE MANDELBROT")
print("="*70)

print("\n📊 SPEEDUPS (8 processus):")
print(f"  • Block:         {block_speedup[-1]:.2f}× (efficacité: {block_efficiency[-1]:.1f}%)")
print(f"  • Cyclique:      {cyclic_speedup[-1]:.2f}× (efficacité: {cyclic_efficiency[-1]:.1f}%) ⭐")
print(f"  • Maître-Esclave: {ms_speedup[-1]:.2f}× (efficacité: {ms_efficiency[-1]:.1f}%)")

print("\n⚡ TEMPS D'EXÉCUTION (8 processus):")
print(f"  • Block:         {block_times[-1]:.3f}s")
print(f"  • Cyclique:      {cyclic_times[-1]:.3f}s ⭐ (le plus rapide)")
print(f"  • Maître-Esclave: {ms_times[-1]:.3f}s")

print("\n⚖️  ÉQUILIBRAGE DE CHARGE (écart-type, 8 processus):")
print(f"  • Block:    σ = {std_block:.3f}s")
print(f"  • Cyclique: σ = {std_cyclic:.3f}s ⭐ (réduction de {(1-std_cyclic/std_block)*100:.1f}%)")

print("\n🏆 CONCLUSION:")
print("  La répartition cyclique est la stratégie la plus performante:")
print("  - Meilleur speedup (6.10×)")
print("  - Temps d'exécution le plus court (0.210s)")
print("  - Meilleur équilibrage de charge (σ = 0.012s)")

print("\n✅ Tous les graphiques ont été générés avec succès dans le dossier 'plots/'")
print("="*70)
