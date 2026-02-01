"""
Ensemble de Mandelbrot - Stratégie Maître-Esclave
Le processus 0 distribue dynamiquement les lignes aux esclaves

TP2 - Question 1.3
"""
from mpi4py import MPI
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius:  float = 2.0

    def convergence(self, c: complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c, smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex, smooth=False) -> int | float:
        if c.real*c.real+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real > -0.75) and (c.real < 0.5):
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2, 1.E-14)):
                return self.max_iterations
        z = 0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

# Tags pour les messages
TAG_TASK = 1      # Envoi d'une tâche (numéro de ligne)
TAG_RESULT = 2    # Envoi du résultat
TAG_TERMINATE = 3 # Signal de terminaison

# Initialisation MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if size < 2:
    if rank == 0:
        print("ERREUR: Cette stratégie nécessite au moins 2 processus!")
        print("Usage: mpirun -np N python3 mandelbrot_master_slave.py (N >= 2)")
    MPI.Finalize()
    exit(1)

# Paramètres
mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
width, height = 1024, 1024
scaleX = 3./width
scaleY = 2.25/height

def compute_row(y):
    """Calcule une ligne de l'image"""
    row = np.empty(width, dtype=np.double)
    for x in range(width):
        c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
        row[x] = mandelbrot_set.convergence(c, smooth=True)
    return row

if rank == 0:
    # === PROCESSUS MAÎTRE ===
    convergence = np.empty((width, height), dtype=np.double)
    next_row = 0
    completed_rows = 0
    num_workers = size - 1
    active_workers = 0
    
    deb = time()
    
    # Envoi initial : une ligne à chaque esclave
    for worker in range(1, size):
        if next_row < height:
            comm.send(next_row, dest=worker, tag=TAG_TASK)
            next_row += 1
            active_workers += 1
    
    # Boucle principale : recevoir résultats et envoyer nouvelles tâches
    while completed_rows < height:
        # Recevoir un résultat de n'importe quel esclave
        status = MPI.Status()
        result = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_RESULT, status=status)
        worker = status.Get_source()
        
        row_idx, row_data = result
        convergence[:, row_idx] = row_data
        completed_rows += 1
        
        # Envoyer une nouvelle tâche ou signal de terminaison
        if next_row < height:
            comm.send(next_row, dest=worker, tag=TAG_TASK)
            next_row += 1
        else:
            comm.send(-1, dest=worker, tag=TAG_TERMINATE)
            active_workers -= 1
    
    fin = time()
    
    print(f"\n=== Résultats Maître-Esclave ({size} processus, {num_workers} esclaves) ===")
    print(f"Temps de calcul total: {fin-deb:.4f}s")
    
    # Création de l'image
    deb_img = time()
    image = Image.fromarray(np.uint8(convergence.T * 255))
    fin_img = time()
    print(f"Temps de constitution de l'image: {fin_img-deb_img:.4f}s")
    image.save(f"mandelbrot_master_slave_{size}p.png")
    print(f"Image sauvegardée: mandelbrot_master_slave_{size}p.png")

else:
    # === PROCESSUS ESCLAVE ===
    rows_computed = 0
    
    while True:
        # Recevoir une tâche
        status = MPI.Status()
        row_idx = comm.recv(source=0, tag=MPI.ANY_TAG, status=status)
        
        if status.Get_tag() == TAG_TERMINATE:
            break
        
        # Calculer la ligne
        row_data = compute_row(row_idx)
        rows_computed += 1
        
        # Envoyer le résultat
        comm.send((row_idx, row_data), dest=0, tag=TAG_RESULT)
    
    print(f"Esclave {rank}: {rows_computed} lignes calculées")
