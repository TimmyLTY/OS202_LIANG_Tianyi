"""
Produit matrice-vecteur parallèle - Découpage par lignes
v = A @ u

TP2 - Question 2.b
"""
from mpi4py import MPI
import numpy as np
from time import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Dimension du problème (doit être divisible par size)
dim = 1200

# Vérification
if dim % size != 0:
    if rank == 0:
        print(f"ERREUR: dim ({dim}) doit être divisible par size ({size})")
    MPI.Finalize()
    exit(1)

N_loc = dim // size  # Nombre de lignes par processus

# Calcul des indices de lignes locales
start_row = rank * N_loc
end_row = start_row + N_loc

if rank == 0:
    print(f"=== Produit Matrice-Vecteur par Lignes ===")
    print(f"Dimension: {dim}, Processus: {size}, Lignes par processus: {N_loc}")

# Construction de la partie locale de la matrice (N_loc lignes, toutes les colonnes)
A_local = np.array([[(i+j) % dim + 1. for j in range(dim)] 
                    for i in range(start_row, end_row)], dtype=np.double)

# Vecteur u complet (tous les processus en ont besoin)
u = np.array([j+1. for j in range(dim)], dtype=np.double)

# Calcul du produit partiel: A_local @ u donne N_loc éléments du résultat
deb = time()
v_local = A_local @ u  # Produit de (N_loc x dim) par (dim,) = (N_loc,)
fin = time()

local_time = fin - deb

# Rassemblement du résultat complet sur tous les processus
v = np.zeros(dim, dtype=np.double)
comm.Allgather(v_local, v)

# Collecte du temps maximum
max_time = comm.reduce(local_time, op=MPI.MAX, root=0)

if rank == 0:
    print(f"\n=== Résultats ({size} processus, découpage par lignes) ===")
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
