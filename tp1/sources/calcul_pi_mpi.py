#!/usr/bin/env python3
"""
TP1 - Section 2.2 : Calcul approché de π - Version mpi4py

Parallélisation en mémoire distribuée avec mpi4py

Installation : pip install mpi4py numpy
Exécution    : mpirun -np 4 python3 calcul_pi_mpi.py [nombre_de_points]
"""

import numpy as np
from mpi4py import MPI
import sys
import time

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    nbp = comm.Get_size()
    
    # Nombre de points par défaut
    nbSamples = 100_000_000  # 10^8
    
    if len(sys.argv) > 1:
        nbSamples = int(sys.argv[1])
    
    # Chaque processus traite sa portion
    samples_per_proc = nbSamples // nbp
    my_start = rank * samples_per_proc
    my_end = nbSamples if rank == nbp - 1 else my_start + samples_per_proc
    my_samples = my_end - my_start
    
    # Graine unique pour chaque processus (modulo 2^32 pour éviter l'overflow)
    seed = (int(time.time()) + rank * 12345) % (2**32)
    np.random.seed(seed)
    
    # Synchronisation avant le début de la mesure
    comm.Barrier()
    start_time = MPI.Wtime()
    
    # Génération des points et comptage
    x = np.random.uniform(-1.0, 1.0, my_samples)
    y = np.random.uniform(-1.0, 1.0, my_samples)
    local_darts = np.sum(x*x + y*y <= 1.0)
    
    # Réduction : somme de tous les compteurs locaux
    total_darts = comm.reduce(local_darts, op=MPI.SUM, root=0)
    
    # Synchronisation à la fin
    comm.Barrier()
    end_time = MPI.Wtime()
    elapsed = end_time - start_time
    
    # Le processus 0 affiche le résultat
    if rank == 0:
        pi = 4.0 * total_darts / nbSamples
        error = abs(pi - np.pi) / np.pi * 100.0
        
        print("=== Calcul de π - Version mpi4py ===")
        print(f"Nombre de points     : {nbSamples}")
        print(f"Nombre de processus  : {nbp}")
        print(f"π calculé  : {pi:.10f}")
        print(f"π réel     : {np.pi:.10f}")
        print(f"Erreur     : {error:.6f} %")
        print(f"Temps      : {elapsed:.6f} secondes")

if __name__ == "__main__":
    main()
