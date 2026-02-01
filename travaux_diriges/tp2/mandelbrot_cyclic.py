"""
Ensemble de Mandelbrot - Répartition cyclique (entrelacée)
Le processus i calcule les lignes i, i+nbp, i+2*nbp, ...

TP2 - Question 1.2
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

# Initialisation MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Paramètres
mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
width, height = 1024, 1024
scaleX = 3./width
scaleY = 2.25/height

# Répartition cyclique: le processus rank calcule les lignes rank, rank+size, rank+2*size, ...
my_rows = list(range(rank, height, size))
local_height = len(my_rows)

print(f"Processus {rank}/{size}: {local_height} lignes (première: {my_rows[0]}, dernière: {my_rows[-1]})")

# Calcul local
local_indices = np.array(my_rows, dtype=np.int32)
local_data = np.empty((local_height, width), dtype=np.double)

deb = time()
for idx, y in enumerate(my_rows):
    for x in range(width):
        c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
        local_data[idx, x] = mandelbrot_set.convergence(c, smooth=True)
fin = time()

local_time = fin - deb
print(f"Processus {rank}: temps de calcul local = {local_time:.4f}s")

# Rassemblement: collecter les nombres de lignes par processus
local_count = np.array([local_height], dtype=np.int32)
all_counts = None
if rank == 0:
    all_counts = np.empty(size, dtype=np.int32)
comm.Gather(local_count, all_counts, root=0)

# Gatherv pour les indices
if rank == 0:
    all_indices = np.empty(height, dtype=np.int32)
    indices_displ = np.array([0] + list(np.cumsum(all_counts)[:-1]))
else:
    all_indices = None
    indices_displ = None

comm.Gatherv(local_indices, [all_indices, all_counts, indices_displ, MPI.INT], root=0)

# Gatherv pour les données
local_data_flat = local_data.flatten()
if rank == 0:
    all_data = np.empty(height * width, dtype=np.double)
    data_counts = all_counts * width
    data_displ = np.array([0] + list(np.cumsum(data_counts)[:-1]))
else:
    all_data = None
    data_counts = None
    data_displ = None

comm.Gatherv(local_data_flat, [all_data, data_counts, data_displ, MPI.DOUBLE], root=0)

# Collecte du temps maximum
max_time = comm.reduce(local_time, op=MPI.MAX, root=0)

if rank == 0:
    # Reconstruction de l'image
    convergence = np.empty((width, height), dtype=np.double)
    
    for i in range(height):
        y = all_indices[i]
        row_data = all_data[i * width:(i + 1) * width]
        convergence[:, y] = row_data
    
    print(f"\n=== Résultats Cyclique ({size} processus) ===")
    print(f"Temps de calcul maximum: {max_time:.4f}s")
    
    # Création de l'image
    deb_img = time()
    image = Image.fromarray(np.uint8(convergence.T * 255))
    fin_img = time()
    print(f"Temps de constitution de l'image: {fin_img-deb_img:.4f}s")
    image.save(f"mandelbrot_cyclic_{size}p.png")
    print(f"Image sauvegardée: mandelbrot_cyclic_{size}p.png")
