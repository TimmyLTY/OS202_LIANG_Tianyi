#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TP1 - Graphiques de Speedup OpenMP
Génère des courbes de speedup pour différentes tailles de matrices
"""

import matplotlib.pyplot as plt
import numpy as np

# Données expérimentales
threads = np.array([1, 2, 3, 4, 5, 6, 7, 8])

# MFlops pour chaque taille de matrice
mflops_512 = np.array([4303.01, 7338.71, 12415.8, 16402.8, 20640.7, 24440.9, 27324.3, 30475.0])
mflops_1024 = np.array([4411.2, 8534.45, 10867.4, 14496.3, 21850.9, 26111.3, 30062.7, 34578.8])
mflops_2048 = np.array([4469.36, 8907.64, 12737.1, 14034.6, 18038.0, 20166.0, 21330.5, 23072.9])

# Calcul du Speedup
speedup_512 = mflops_512 / mflops_512[0]
speedup_1024 = mflops_1024 / mflops_1024[0]
speedup_2048 = mflops_2048 / mflops_2048[0]

# Speedup idéal
speedup_ideal = threads

# ============================================================================
# Figure 1: Courbes de Speedup
# ============================================================================
plt.figure(figsize=(10, 7))

plt.plot(threads, speedup_ideal, 'k--', linewidth=2, label='Speedup idéal', alpha=0.7)
plt.plot(threads, speedup_512, 'bo-', linewidth=2, markersize=8, label='n=512')
plt.plot(threads, speedup_1024, 'gs-', linewidth=2, markersize=8, label='n=1024')
plt.plot(threads, speedup_2048, 'r^-', linewidth=2, markersize=8, label='n=2048')

plt.xlabel('Nombre de threads (OMP_NUM_THREADS)', fontsize=12)
plt.ylabel('Speedup', fontsize=12)
plt.title('Speedup OpenMP pour le produit matrice-matrice\n(Ordre de boucles optimal: j,k,i)', fontsize=14)
plt.legend(loc='upper left', fontsize=11)
plt.grid(True, alpha=0.3)
plt.xticks(threads)
plt.xlim(0.5, 8.5)
plt.ylim(0, 9)

# Annotations
plt.annotate(f'7.84×', xy=(8, speedup_1024[-1]), xytext=(7.3, speedup_1024[-1]+0.5),
             fontsize=10, color='green', fontweight='bold')
plt.annotate(f'7.08×', xy=(8, speedup_512[-1]), xytext=(7.3, speedup_512[-1]-0.7),
             fontsize=10, color='blue', fontweight='bold')
plt.annotate(f'5.16×', xy=(8, speedup_2048[-1]), xytext=(7.3, speedup_2048[-1]-0.7),
             fontsize=10, color='red', fontweight='bold')

plt.tight_layout()
plt.savefig('speedup_omp.png', dpi=150, bbox_inches='tight')
plt.savefig('speedup_omp.pdf', bbox_inches='tight')
print("Figure sauvegardée: speedup_omp.png / speedup_omp.pdf")

# ============================================================================
# Figure 2: Efficacité parallèle
# ============================================================================
plt.figure(figsize=(10, 7))

efficiency_512 = speedup_512 / threads * 100
efficiency_1024 = speedup_1024 / threads * 100
efficiency_2048 = speedup_2048 / threads * 100

plt.plot(threads, efficiency_512, 'bo-', linewidth=2, markersize=8, label='n=512')
plt.plot(threads, efficiency_1024, 'gs-', linewidth=2, markersize=8, label='n=1024')
plt.plot(threads, efficiency_2048, 'r^-', linewidth=2, markersize=8, label='n=2048')
plt.axhline(y=100, color='k', linestyle='--', linewidth=2, alpha=0.7, label='Efficacité idéale (100%)')

plt.xlabel('Nombre de threads (OMP_NUM_THREADS)', fontsize=12)
plt.ylabel('Efficacité parallèle (%)', fontsize=12)
plt.title('Efficacité parallèle OpenMP\n(Efficacité = Speedup / N_threads × 100%)', fontsize=14)
plt.legend(loc='upper right', fontsize=11)
plt.grid(True, alpha=0.3)
plt.xticks(threads)
plt.xlim(0.5, 8.5)
plt.ylim(0, 120)

plt.tight_layout()
plt.savefig('efficiency_omp.png', dpi=150, bbox_inches='tight')
plt.savefig('efficiency_omp.pdf', bbox_inches='tight')
print("Figure sauvegardée: efficiency_omp.png / efficiency_omp.pdf")

# ============================================================================
# Figure 3: Performance absolue (MFlops)
# ============================================================================
plt.figure(figsize=(10, 7))

plt.plot(threads, mflops_512/1000, 'bo-', linewidth=2, markersize=8, label='n=512')
plt.plot(threads, mflops_1024/1000, 'gs-', linewidth=2, markersize=8, label='n=1024')
plt.plot(threads, mflops_2048/1000, 'r^-', linewidth=2, markersize=8, label='n=2048')

plt.xlabel('Nombre de threads (OMP_NUM_THREADS)', fontsize=12)
plt.ylabel('Performance (GFlops)', fontsize=12)
plt.title('Performance absolue du produit matrice-matrice\n(Ordre de boucles optimal: j,k,i)', fontsize=14)
plt.legend(loc='upper left', fontsize=11)
plt.grid(True, alpha=0.3)
plt.xticks(threads)
plt.xlim(0.5, 8.5)

# Annotation pour le max
plt.annotate(f'34.6 GFlops', xy=(8, mflops_1024[-1]/1000), 
             xytext=(6.5, mflops_1024[-1]/1000 + 2),
             fontsize=10, color='green', fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='green', lw=1.5))

plt.tight_layout()
plt.savefig('performance_omp.png', dpi=150, bbox_inches='tight')
plt.savefig('performance_omp.pdf', bbox_inches='tight')
print("Figure sauvegardée: performance_omp.png / performance_omp.pdf")

# ============================================================================
# Affichage des tableaux de données
# ============================================================================
print("\n" + "="*60)
print("Tableau des Speedup:")
print("="*60)
print(f"{'Threads':<10} {'n=512':<12} {'n=1024':<12} {'n=2048':<12}")
print("-"*50)
for i, t in enumerate(threads):
    print(f"{t:<10} {speedup_512[i]:<12.2f} {speedup_1024[i]:<12.2f} {speedup_2048[i]:<12.2f}")

print("\n" + "="*60)
print("Tableau des Efficacités (%):")
print("="*60)
print(f"{'Threads':<10} {'n=512':<12} {'n=1024':<12} {'n=2048':<12}")
print("-"*50)
for i, t in enumerate(threads):
    print(f"{t:<10} {efficiency_512[i]:<12.1f} {efficiency_1024[i]:<12.1f} {efficiency_2048[i]:<12.1f}")

plt.show()
