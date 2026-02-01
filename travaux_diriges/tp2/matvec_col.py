"""
Produit matrice-vecteur parallèle - Découpage par colonnes
v = A @ u

TP2 - Question 2.a
"""
from mpi4py import MPI
import numpy as np
from time import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Dimension du problème (doit être divisible par size)
dim = 1200  # Augmenté pour mieux mesurer le temps

# Vérification
if dim % size != 0:
    if rank == 0:
        print(f"ERREUR: dim ({dim}) doit être divisible par size ({size})")
    MPI.Finalize()
    exit(1)

N_loc = dim // size  # Nombre de colonnes par processus

# Calcul des indices de colonnes locales
start_col = rank * N_loc
end_col = start_col + N_loc

if rank == 0:
    print(f"=== Produit Matrice-Vecteur par Colonnes ===")
    print(f"Dimension: {dim}, Processus: {size}, Colonnes par processus: {N_loc}")

# Construction de la partie locale de la matrice (toutes les lignes, N_loc colonnes)
# A[i,j] = (i+j) % dim + 1
A_local = np.array([[(i+j) % dim + 1. for j in range(start_col, end_col)] 
                    for i in range(dim)], dtype=np.double)

# Portion locale du vecteur u
u_local = np.array([j+1. for j in range(start_col, end_col)], dtype=np.double)

# Calcul du produit partiel: A_local @ u_local donne un vecteur de taille dim
deb = time()
v_partial = A_local @ u_local  # Produit de (dim x N_loc) par (N_loc,) = (dim,)
fin = time()

local_time = fin - deb

# Réduction pour sommer toutes les contributions partielles
# Chaque processus a une somme partielle, on les additionne
v = np.zeros(dim, dtype=np.double)
comm.Allreduce(v_partial, v, op=MPI.SUM)

# Collecte du temps maximum
max_time = comm.reduce(local_time, op=MPI.MAX, root=0)

if rank == 0:
    print(f"\n=== Résultats ({size} processus, découpage par colonnes) ===")
    print(f"Temps de calcul maximum: {max_time:.6f}s")
    print(f"Premiers éléments de v: {v[:5]}")
    print(f"Derniers éléments de v: {v[-5:]}")
    
    # Vérification avec calcul séquentiel
    A_full = np.array([[(i+j) % dim + 1. for j in range(dim)] for i in range(dim)])
    u_full = np.array([j+1. for j in range(dim)])
    v_ref = A_full @ u_full
    
    error = np.max(np.abs(v - v_ref))
    print(f"Erreur maximale vs séquentiel: {error}")
    if error < 1e-10:
        print("✓ Résultat correct!")
    else:
        print("✗ Erreur dans le calcul!")

# Vérification que tous les processus ont le bon résultat
local_sum = np.sum(v)
all_sums = comm.gather(local_sum, root=0)
if rank == 0:
    if len(set([round(s, 6) for s in all_sums])) == 1:
        print("✓ Tous les processus ont le même résultat")
    else:
        print("✗ Incohérence entre processus!")
