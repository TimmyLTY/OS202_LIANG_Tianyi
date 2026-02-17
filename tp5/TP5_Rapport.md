# TP5 — Calcul GPU avec PyCUDA

**LIANG Tianyi**
**Environnement** : Google Colab (Tesla T4)

---

## Objectif

Implémenter des kernels CUDA en Python via PyCUDA pour comparer les performances CPU (NumPy) et GPU sur trois exercices : addition de vecteurs, addition de matrices et calcul de l'ensemble de Mandelbrot.

---

## Exercice 1 : Addition vectorielle

**Kernel** : chaque thread calcule `c[idx] = a[idx] + b[idx]` avec `idx = threadIdx.x + blockIdx.x * blockDim.x`.

- Bloc de 256 threads ; nombre de blocs = `(N + 255) // 256`
- Vérification : `np.allclose` → True pour N ∈ {256, 1000, 10000, 100000, 1000000}

**Benchmark (N = 10 000 000)** :

| Méthode | Temps | Speedup |
|---------|-------|---------|
| CPU (NumPy) | 15.460 ms | — |
| GPU (kernel) | 0.460 ms | **33.64×** |

---

## Exercice 2 : Addition matricielle

**Kernel** : blocs et grilles 2D (16×16). Indices : `col = threadIdx.x + blockIdx.x * blockDim.x`, `row = threadIdx.y + blockIdx.y * blockDim.y`, `idx = col + row * dim_x`.

| Dimension | Grille | Correct |
|-----------|--------|---------|
| 16×16 | (1, 1) | ✓ |
| 64×64 | (4, 4) | ✓ |
| 256×256 | (16, 16) | ✓ |
| 512×512 | (32, 32) | ✓ |
| 1024×1024 | (64, 64) | ✓ |
| 2048×2048 | (128, 128) | ✓ |

---

## Exercice 3 : Ensemble de Mandelbrot

Chaque thread calcule un pixel : itération de $z_{n+1} = z_n^2 + c$ jusqu'à divergence ($|z| > 2$) ou `loop` itérations.

**Résultat (1000×1000, 100 itérations)** :

| Méthode | Temps | Speedup |
|---------|-------|---------|
| CPU (NumPy) | 877.880 ms | — |
| GPU (CUDA) | 0.168 ms | **5235×** |

**Benchmark multi-résolution (200 itérations)** :

| Résolution | CPU (ms) | GPU (ms) | Speedup |
|------------|----------|----------|---------|
| 500×500 | 299.3 | 0.08 | 3 612× |
| 1000×1000 | 2 386.0 | 0.24 | 10 043× |
| 2000×2000 | 9 783.3 | 0.85 | 11 573× |
| 4000×4000 | 44 216.9 | 3.28 | **13 497×** |

Le speedup augmente avec la résolution car le volume de calcul croît en O(n²), réparti efficacement sur les milliers de cœurs GPU.

---

## Conclusion

1. L'addition vectorielle/matricielle illustre les bases de la programmation CUDA : indexation globale, grilles 2D, gestion des limites.
2. Le calcul de Mandelbrot est un cas *embarrassingly parallel* idéal pour le GPU.
3. Le speedup GPU/CPU est d'autant plus élevé que la charge de calcul est grande (paradigme SIMT).
4. Le surcoût de transfert mémoire Host ↔ Device est amorti lorsque le volume de calcul est suffisant.
