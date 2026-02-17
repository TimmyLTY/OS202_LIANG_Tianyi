"""
Benchmark headless du Jeu de la Vie — Version adaptée au code du cours
========================================================================
Compare les performances du calcul pour différents nombres de processus MPI,
SANS affichage pygame (mode headless).

Usage :
    # Série (1 processus de calcul)
    mpirun -np 2 python3 benchmark_headless.py --steps 500 --pattern glider_gun

    # Parallèle (3 processus de calcul = 1 controller + 3 workers)
    mpirun -np 4 python3 benchmark_headless.py --steps 500 --pattern glider_gun

    # Tous les tests (lance automatiquement np=2,3,4,5,9)
    python3 benchmark_headless.py --run-all --steps 500 --pattern glider_gun

Note : le processus de rang 0 est toujours le contrôleur (pas de calcul),
donc np=2 → 1 worker, np=3 → 2 workers, np=5 → 4 workers, np=9 → 8 workers.
"""
import numpy as np
from mpi4py import MPI
import time
import sys
import argparse
import subprocess
import csv
import os


class GrilleHeadless:
    """
    Version headless de la Grille (sans pygame).
    Identique au code du cours mais sans dépendance pygame.
    """
    def __init__(self, rank: int, nbp: int, dim, init_pattern=None):
        self.dimensions = dim
        self.dimensions_loc = (dim[0]//nbp + (1 if rank < dim[0]%nbp else 0), dim[1])
        self.start_loc = rank * self.dimensions_loc[0] + (dim[0]%nbp if rank >= dim[0]%nbp else 0)

        if init_pattern is not None:
            self.cells = np.zeros((self.dimensions_loc[0]+2, self.dimensions_loc[1]), dtype=np.uint8)
            indices_i = [v[0]-self.start_loc+1 for v in init_pattern
                         if v[0] >= self.start_loc and v[0] < self.start_loc+self.dimensions_loc[0]]
            indices_j = [v[1] for v in init_pattern
                         if v[0] >= self.start_loc and v[0] < self.start_loc+self.dimensions_loc[0]]
            if len(indices_i) > 0:
                self.cells[indices_i, indices_j] = 1
        else:
            self.cells = np.random.randint(2, size=(self.dimensions_loc[0]+2, dim[1]), dtype=np.uint8)

    def compute_next_iteration(self):
        """Calcule la prochaine génération (identique au code du cours)."""
        neighbours_count = sum(
            np.roll(np.roll(self.cells, i, 0), j, 1)
            for i in (-1, 0, 1) for j in (-1, 0, 1) if (i != 0 or j != 0)
        )
        next_cells = (neighbours_count == 3) | (self.cells & (neighbours_count == 2))
        self.cells = next_cells
        return None

    def update_ghost_cells(self, comm):
        """Met à jour les cellules fantômes (identique au code du cours)."""
        req1 = comm.Irecv(self.cells[-1, :], source=(comm.rank+1) % comm.size, tag=101)
        req2 = comm.Irecv(self.cells[0, :], source=(comm.rank+comm.size-1) % comm.size, tag=102)
        comm.Send(self.cells[-2, :], dest=(comm.rank+1) % comm.size, tag=102)
        comm.Send(self.cells[1, :], dest=(comm.rank+comm.size-1) % comm.size, tag=101)
        req1.Wait()
        req2.Wait()


class GrilleSerial:
    """
    Version série complète (1 seul processus, pas de ghost cells).
    Pour la comparaison de référence.
    """
    def __init__(self, dim, init_pattern=None):
        self.dimensions = dim
        if init_pattern is not None:
            self.cells = np.zeros(dim, dtype=np.uint8)
            indices_i = [v[0] for v in init_pattern]
            indices_j = [v[1] for v in init_pattern]
            self.cells[indices_i, indices_j] = 1
        else:
            self.cells = np.random.randint(2, size=dim, dtype=np.uint8)

    def compute_next_iteration(self):
        neighbours_count = sum(
            np.roll(np.roll(self.cells, i, 0), j, 1)
            for i in (-1, 0, 1) for j in (-1, 0, 1) if (i != 0 or j != 0)
        )
        next_cells = (neighbours_count == 3) | (self.cells & (neighbours_count == 2))
        self.cells = next_cells


# Patterns disponibles
dico_patterns = {
    'blinker':  ((5, 5), [(2, 1), (2, 2), (2, 3)]),
    'toad':     ((6, 6), [(2, 2), (2, 3), (2, 4), (3, 3), (3, 4), (3, 5)]),
    "acorn":    ((100, 100), [(51, 52), (52, 54), (53, 51), (53, 52), (53, 55), (53, 56), (53, 57)]),
    "glider":   ((100, 90), [(1, 1), (2, 2), (2, 3), (3, 1), (3, 2)]),
    "glider_gun": ((200, 100), [
        (51, 76), (52, 74), (52, 76), (53, 64), (53, 65), (53, 72), (53, 73),
        (53, 86), (53, 87), (54, 63), (54, 67), (54, 72), (54, 73), (54, 86),
        (54, 87), (55, 52), (55, 53), (55, 62), (55, 68), (55, 72), (55, 73),
        (56, 52), (56, 53), (56, 62), (56, 66), (56, 68), (56, 69), (56, 74),
        (56, 76), (57, 62), (57, 68), (57, 76), (58, 63), (58, 67), (59, 64),
        (59, 65)]),
    "block_switch_engine": ((400, 400), [
        (201, 202), (201, 203), (202, 202), (202, 203), (211, 203), (212, 204),
        (212, 202), (214, 204), (214, 201), (215, 201), (215, 202), (216, 201)]),
    "flat": ((200, 400), [
        (80, 200), (81, 200), (82, 200), (83, 200), (84, 200), (85, 200),
        (86, 200), (87, 200), (89, 200), (90, 200), (91, 200), (92, 200),
        (93, 200), (97, 200), (98, 200), (99, 200), (106, 200), (107, 200),
        (108, 200), (109, 200), (110, 200), (111, 200), (112, 200), (114, 200),
        (115, 200), (116, 200), (117, 200), (118, 200)])
}


def run_serial_benchmark(pattern_name, steps):
    """Benchmark série (référence)."""
    dim, pattern = dico_patterns[pattern_name]
    grid = GrilleSerial(dim, pattern)
    # Warm-up
    for _ in range(10):
        grid.compute_next_iteration()
    t_start = time.time()
    for _ in range(steps):
        grid.compute_next_iteration()
    t_end = time.time()
    return t_end - t_start


def run_parallel_benchmark(pattern_name, steps, comm):
    """Benchmark parallèle (mode headless, tous les rangs calculent)."""
    rank = comm.Get_rank()
    size = comm.Get_size()
    dim, pattern = dico_patterns[pattern_name]

    grid = GrilleHeadless(rank, size, dim, pattern)
    grid.update_ghost_cells(comm)

    # Préparer Gatherv
    grid_glob = None
    if rank == 0:
        grid_glob = np.zeros(dim, dtype=np.uint8)
    sendcounts = np.array(comm.gather(grid.cells[1:-1, :].size, root=0))

    # Warm-up
    for _ in range(10):
        grid.compute_next_iteration()
        grid.update_ghost_cells(comm)
    comm.Barrier()

    # --- Benchmark : calcul + communication ghost ---
    t_calc_total = 0.0
    t_ghost_total = 0.0
    t_gather_total = 0.0

    comm.Barrier()
    t_start = time.time()
    for _ in range(steps):
        tc1 = time.time()
        grid.compute_next_iteration()
        tc2 = time.time()
        grid.update_ghost_cells(comm)
        tc3 = time.time()
        comm.Gatherv(grid.cells[1:-1, :], [grid_glob, sendcounts], root=0)
        tc4 = time.time()
        t_calc_total += (tc2 - tc1)
        t_ghost_total += (tc3 - tc2)
        t_gather_total += (tc4 - tc3)
    comm.Barrier()
    t_end = time.time()

    t_total = t_end - t_start
    return t_calc_total, t_ghost_total, t_gather_total, t_total


def run_all_benchmarks(pattern_name, steps, mpirun_path):
    """Lance automatiquement les benchmarks pour différents np."""
    script_path = os.path.abspath(__file__)
    results = []

    # np_values: total MPI processes
    # Architecture du cours: rank 0 = controller, ranks 1+ = workers
    # Mais en mode headless on fait travailler tous les rangs
    np_values = [1, 2, 4, 8]

    for np_val in np_values:
        print(f"\n{'='*60}")
        print(f"  Running with {np_val} worker(s)...")
        print(f"{'='*60}")
        cmd = [
            mpirun_path, "--oversubscribe", "-np", str(np_val),
            sys.executable, script_path,
            "--steps", str(steps), "--pattern", pattern_name
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            print(result.stdout)
            if result.stderr:
                # Filter out MPI warnings
                for line in result.stderr.split('\n'):
                    if line.strip() and 'mpi' not in line.lower() and 'warning' not in line.lower():
                        print(f"  STDERR: {line}")
            # Parse output
            for line in result.stdout.split('\n'):
                if line.startswith("CSV:"):
                    parts = line[4:].split(',')
                    results.append(parts)
        except subprocess.TimeoutExpired:
            print(f"  TIMEOUT for np={np_val}")

    # Save results to CSV
    csv_path = os.path.join(os.path.dirname(script_path), "benchmark_results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["pattern", "grid_size", "steps", "nb_workers", "t_calc", "t_ghost", "t_gather", "t_total", "t_serial", "speedup", "efficiency"])
        for row in results:
            writer.writerow(row)
    print(f"\n\nResults saved to: {csv_path}")
    return csv_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmark Game of Life (headless)")
    parser.add_argument('--steps', type=int, default=500, help='Number of iterations')
    parser.add_argument('--pattern', type=str, default='glider_gun', help='Pattern name')
    parser.add_argument('--run-all', action='store_true', help='Run all configurations automatically')
    args = parser.parse_args()

    if args.run_all:
        # Find mpirun
        mpirun_path = "/opt/homebrew/Caskroom/miniconda/base/bin/mpirun"
        if not os.path.exists(mpirun_path):
            import shutil
            mpirun_path = shutil.which("mpirun")
        if mpirun_path is None:
            print("ERROR: mpirun not found")
            sys.exit(1)

        # Also run serial benchmark first
        print("=" * 60)
        print(f"  Serial benchmark ({args.pattern}, {args.steps} steps)")
        print("=" * 60)
        t_serial = run_serial_benchmark(args.pattern, args.steps)
        dim = dico_patterns[args.pattern][0]
        print(f"  Serial time: {t_serial:.4f}s ({t_serial/args.steps*1000:.2f} ms/iter)")
        print(f"  Grid: {dim[0]}×{dim[1]}")

        # Save serial result for reference
        serial_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "serial_time.txt")
        with open(serial_file, 'w') as f:
            f.write(f"{t_serial}")

        run_all_benchmarks(args.pattern, args.steps, mpirun_path)
    else:
        # Single MPI run — all processes compute
        comm = MPI.COMM_WORLD
        rank = comm.Get_rank()
        size = comm.Get_size()

        dim, pattern = dico_patterns[args.pattern]

        # Run serial on rank 0 for comparison
        t_serial = 0
        if rank == 0:
            t_serial = run_serial_benchmark(args.pattern, args.steps)

        # Run parallel
        t_calc, t_ghost, t_gather, t_total = run_parallel_benchmark(
            args.pattern, args.steps, comm)

        if rank == 0:
            speedup = t_serial / t_total if t_total > 0 else 0
            efficiency = speedup / size * 100

            print(f"\n{'='*65}")
            print(f"  Benchmark : {args.pattern} ({dim[0]}×{dim[1]}), {args.steps} itérations, {size} workers")
            print(f"{'='*65}")
            print(f"  {'Série (référence)':<30}: {t_serial:.4f}s ({t_serial/args.steps*1000:.2f} ms/iter)")
            print(f"  {'Parallèle (total)':<30}: {t_total:.4f}s ({t_total/args.steps*1000:.2f} ms/iter)")
            print(f"    {'- Calcul':<28}: {t_calc:.4f}s ({t_calc/t_total*100:.1f}%)")
            print(f"    {'- Ghost exchange':<28}: {t_ghost:.4f}s ({t_ghost/t_total*100:.1f}%)")
            print(f"    {'- Gatherv':<28}: {t_gather:.4f}s ({t_gather/t_total*100:.1f}%)")
            print(f"  {'Speedup':<30}: {speedup:.2f}×")
            print(f"  {'Efficacité':<30}: {efficiency:.1f}%")
            print(f"{'='*65}")

            # CSV output for automated collection
            print(f"CSV:{args.pattern},{dim[0]}x{dim[1]},{args.steps},{size},"
                  f"{t_calc:.6f},{t_ghost:.6f},{t_gather:.6f},{t_total:.6f},"
                  f"{t_serial:.6f},{speedup:.4f},{efficiency:.1f}")
