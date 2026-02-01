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

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c: complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c, smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) -> int | float:
        z:    complex
        iter: int

        # On vérifie dans un premier temps si le complexe
        # n'appartient pas à une zone de convergence connue :
        #   1. Appartenance aux disques  C0{(0,0),1/4} et C1{(-1,0),1/4}
        if c.real*c.real+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        #  2.  Appartenance à la cardioïde {(1/4,0),1/2(1-cos(theta))}
        if (c.real > -0.75) and (c.real < 0.5):
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2, 1.E-14)):
                return self.max_iterations
        # Sinon on itère
        z = 0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
width, height = 1024, 1024

scaleX = 3./width
scaleY = 2.25/height

# Calculate local range
rows_per_process = height // size
remainder = height % size

# Distribute remainder to first 'remainder' ranks
if rank < remainder:
    local_height = rows_per_process + 1
    start_y = rank * local_height
else:
    local_height = rows_per_process
    start_y = remainder * (rows_per_process + 1) + (rank - remainder) * rows_per_process

local_convergence = np.empty((width, local_height), dtype=np.double)

# Calculation
deb = time()
for y_local in range(local_height):
    y = start_y + y_local
    for x in range(width):
        c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
        local_convergence[x, y_local] = mandelbrot_set.convergence(c, smooth=True)
fin = time()

# Gather
# Since sizes can be different, use Gatherv
# Prepare counts and displacements on root
counts = None
displacements = None
recvbuf = None

if rank == 0:
    counts = np.array([rows_per_process + 1 if i < remainder else rows_per_process for i in range(size)]) * width
    displacements = np.array([0] + list(np.cumsum(counts)[:-1]))
    recvbuf = np.empty((width, height), dtype=np.double)
    # Important: The gather will flatten the arrays, but since we are gathering column-major chunks effectively (if we view it as rows of pixels but array is width x height)
    # Wait, original code was: convergence[x, y]
    # So it is Width x Height array.
    # The loop iterates y then x.
    # So we are computing rows of pixels.
    # But storing them in columns of the array (since y is the second index).
    # local_convergence is width x local_height.
    # This corresponds to a vertical slice of the array if visualized as a matrix, but semantically these are rows of the image.
    
    # Let's adjust for Gather.
    # local_convergence is (width, local_height).
    # We want to gather into (width, height).
    # If we use Gather, it will stack them. But numpy arrays are row-major by default.
    # local_convergence is stored as [x, y].
    # So in memory: x varies fastest.
    # This means one "column" (fixed x, varying y) is NOT contiguous.
    # Actually, one "row" (fixed y, varying x) IS contiguous if shape is (height, width).
    # But shape is (width, height).
    # So y is the second dimension.
    # This means [x, y] and [x+1, y] are adjacent.
    # [x, y] and [x, y+1] are NOT adjacent (stride is width*itemsize).
    
    # This makes Gatherv tricky if we just pass the buffer.
    # It would be better to transpose so that we are splitting along the first dimension.
    pass

# Transpose to (local_height, width) so we split along the first dimension (contiguous chunks)
local_convergence_T = local_convergence.T.copy() # shape (local_height, width)

if rank == 0:
    recvbuf_T = np.empty((height, width), dtype=np.double)
    counts = np.array([rows_per_process + 1 if i < remainder else rows_per_process for i in range(size)]) * width
    displacements = np.array([0] + list(np.cumsum(counts)[:-1]))
else:
    recvbuf_T = None
    counts = None
    displacements = None

comm.Gatherv(sendbuf=local_convergence_T, recvbuf=[recvbuf_T, counts, displacements, MPI.DOUBLE], root=0)

if rank == 0:
    # Transpose back to (width, height)
    final_convergence = recvbuf_T.T
    
    print(f"Temps du calcul de l'ensemble de Mandelbrot ({size} process): {fin-deb}")
    
    # Image creation
    deb_img = time()
    image = Image.fromarray(np.uint8(final_convergence.T * 255))
    fin_img = time()
    print(f"Temps de constitution de l'image : {fin_img-deb_img}")
    image.save(f"mandelbrot_{size}.png")

