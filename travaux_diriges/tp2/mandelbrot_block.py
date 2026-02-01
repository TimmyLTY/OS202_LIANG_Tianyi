"""
Ensemble de Mandelbrot - Partition par blocs de lignes
Chaque processus calcule un bloc contigu de lignes

TP2 - Question 1.1
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
        # Vérification des zones de convergence connues
        if c.real*c.real+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real > -0.75) and (c.real < 0.5):
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2, 1.E-14)):
                return self.max_iterations
        # Itération
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

# Calcul de la répartition des lignes (gestion du reste)
rows_per_process = height // size
remainder = height % size

if rank < remainder:
    local_height = rows_per_process + 1
    start_y = rank * local_height
else:
    local_height = rows_per_process
    start_y = remainder * (rows_per_process + 1) + (rank - remainder) * rows_per_process

end_y = start_y + local_height

# Affichage de la répartition
print(f"Processus {rank}/{size}: lignes {start_y} à {end_y-1} ({local_height} lignes)")

# Calcul local
local_convergence = np.empty((width, local_height), dtype=np.double)

deb = time()
for y_local in range(local_height):
    y = start_y + y_local
    for x in range(width):
        c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
        local_convergence[x, y_local] = mandelbrot_set.convergence(c, smooth=True)
fin = time()

local_time = fin - deb
print(f"Processus {rank}: temps de calcul local = {local_time:.4f}s")

# Rassemblement avec Gatherv (tailles différentes possibles)
# Transposer pour avoir des données contiguës
local_convergence_T = local_convergence.T.copy()

if rank == 0:
    recvbuf_T = np.empty((height, width), dtype=np.double)
    counts = np.array([rows_per_process + 1 if i < remainder else rows_per_process 
                       for i in range(size)]) * width
    displacements = np.array([0] + list(np.cumsum(counts)[:-1]))
else:
    recvbuf_T = None
    counts = None
    displacements = None

comm.Gatherv(sendbuf=local_convergence_T, 
             recvbuf=[recvbuf_T, counts, displacements, MPI.DOUBLE], 
             root=0)

# Collecte du temps maximum
max_time = comm.reduce(local_time, op=MPI.MAX, root=0)

if rank == 0:
    final_convergence = recvbuf_T.T
    
    print(f"\n=== Résultats ({size} processus) ===")
    print(f"Temps de calcul maximum: {max_time:.4f}s")
    
    # Création de l'image
    deb_img = time()
    image = Image.fromarray(np.uint8(final_convergence.T * 255))
    fin_img = time()
    print(f"Temps de constitution de l'image: {fin_img-deb_img:.4f}s")
    image.save(f"mandelbrot_block_{size}p.png")
    print(f"Image sauvegardée: mandelbrot_block_{size}p.png")
