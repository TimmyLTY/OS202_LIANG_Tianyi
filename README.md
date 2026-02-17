# Travaux Dirigés - OS02 Parallélisme

**Auteur :** LIANG Tianyi  
**Cours :** OS02 - Calcul Parallèle et Distribué  
**Établissement :** ENSTA Paris  
**Année :** 2025-2026

---

## 📋 Table des matières

| TP | Thème | Technologies | Rapport |
|:--:|-------|--------------|---------|
| [TP1](tp1/) | Produit matrice-matrice & Parallélisation OpenMP | C++, OpenMP, BLAS | [TP1_Rapport.md](tp1/TP1_Rapport.md) |
| [TP2](tp2/) | Parallélisation MPI : Mandelbrot & Produit matrice-vecteur | Python, MPI, mpi4py | [TP2_Rapport.md](tp2/TP2_Rapport.md) |
| [TP3](tp3/) | Bucket Sort Parallèle avec MPI | C++, MPI | [TP3_Rapport.md](tp3/TP3_Rapport.md) |
| [TP4](tp4/) | Jeu de la Vie — Parallélisation MPI | Python, MPI, mpi4py, pygame | [TP4_Rapport.md](tp4/TP4_Rapport.md) |
| [TP5](tp5/) | Calcul GPU avec PyCUDA | Python, PyCUDA, CUDA, Google Colab | [TP5_Rapport.md](tp5/TP5_Rapport.md) |

---

## 📁 Structure des dossiers

```
travaux_diriges/
├── README.md                    # Ce fichier (index principal)
├── tp1/
│   ├── TP1_Rapport.md          # Rapport complet TP1
│   ├── Sujet.pdf               # Énoncé du TP1
│   ├── sources/                # Code source C++
│   │   ├── ProdMatMat.cpp      # Produit matrice-matrice optimisé
│   │   ├── Matrix.hpp          # Classe matrice
│   │   ├── TestProductMatrix.cpp
│   │   └── ...
│   └── solution/               # Solutions additionnelles
│       ├── jeton_anneau.py     # Circulation de jeton MPI
│       └── calcul_pi.cpp       # Calcul de π parallèle
│
├── tp2/
│   ├── TP2_Rapport.md          # Rapport complet TP2
│   ├── Readme.md               # Énoncé du TP2
│   ├── mandelbrot_block.py     # Stratégie partition par blocs
│   ├── mandelbrot_cyclic.py    # Stratégie répartition cyclique
│   ├── mandelbrot_master_slave.py # Stratégie maître-esclave
│   ├── matvec_col.py           # Produit matrice-vecteur par colonnes
│   ├── matvec_row.py           # Produit matrice-vecteur par lignes
│   ├── plot_results.py         # Génération des graphiques
│   ├── run_all_tp2_experiments.sh # Script d'automatisation
│   ├── images/                 # Images Mandelbrot générées
│   ├── plots/                  # Graphiques de performance
│   └── results/                # Résultats expérimentaux
│
├── tp3/
│   ├── TP3_Rapport.md          # Rapport complet TP3
│   ├── README.md               # Énoncé et instructions
│   ├── sources/                # Code source C++
│   │   ├── bucket_sort_seq.cpp     # Version séquentielle
│   │   ├── bucket_sort_mpi.cpp     # Version parallèle MPI
│   │   ├── Makefile                # Compilation
│   │   └── run_experiments.sh      # Script d'automatisation
│   ├── results/                # Résultats expérimentaux
│   └── images/                 # Illustrations du cours
│
├── tp4/
│   ├── TP4_Rapport.md          # Rapport complet TP4
│   ├── game_of_life.py         # Jeu de la Vie parallèle (MPI)
│   ├── game_of_life_parallel.py # Copie identique
│   ├── benchmark_headless.py   # Benchmark sans affichage
│   └── benchmark_results.csv   # Résultats expérimentaux
│
└── tp5/
    ├── TP5_Rapport.md          # Rapport complet TP5
    ├── TP5_LIANG_Tianyi.ipynb   # Notebook Colab exécuté
    ├── TP_numero_cinq.ipynb     # Notebook original du cours
    └── test_numba/              # Exemples Numba (préparation exam)
```

---

## 📖 Résumé des TPs

### TP1 : Produit Matrice-Matrice et OpenMP

**Objectifs :**
- Comprendre l'impact de l'ordre des boucles sur les performances (cache)
- Optimiser avec la technique de blocking
- Comparer avec la bibliothèque BLAS optimisée
- Paralléliser avec OpenMP

**Résultats clés :**
- L'ordre `ikj` est optimal (accès mémoire contigus)
- Le blocking améliore les performances de ~15%
- OpenMP atteint une efficacité de ~85% sur 4 threads
- BLAS surpasse toutes les implémentations manuelles (3200 GFLOPS vs 200 GFLOPS)

### TP2 : Parallélisation MPI

**Objectifs :**
- Paralléliser le calcul de l'ensemble de Mandelbrot avec 3 stratégies
- Implémenter le produit matrice-vecteur distribué
- Analyser les lois d'Amdahl et Gustafson

**Résultats clés :**
- **Partition par blocs** : Speedup 5.31× avec 8 processus (efficacité 66%)
- **Répartition cyclique** : Speedup 6.10× (efficacité 76%) - meilleur équilibrage
- **Maître-esclave** : Efficacité 82% - meilleure adaptation à la charge
- Le déséquilibre de charge vient de la complexité variable du calcul Mandelbrot

### TP3 : Bucket Sort Parallèle

**Objectifs :**
- Implémenter l'algorithme Bucket Sort parallèle avec MPI
- Utiliser l'approche Sample Sort pour l'équilibrage de charge
- Maîtriser les communications All-to-All

**Points clés :**
- **Sample Sort** : Échantillonnage pour définir des frontières de buckets équilibrées
- Utilisation de `MPI_Scatterv`, `MPI_Alltoallv`, `MPI_Gatherv`
- **Merge k-way** avec heap pour fusionner les listes triées
- Analyse de performance et scalabilité

### TP4 : Jeu de la Vie — Parallélisation MPI

**Objectifs :**
- Paralléliser l'automate cellulaire « Game of Life » sur grille torique
- Implémenter la décomposition de domaine par bandes horizontales
- Gérer l'échange de cellules fantômes (ghost cells) entre processus
- Séparer contrôleur (affichage) et workers (calcul)

**Résultats clés :**
- Vectorisation (`np.roll`) vs boucles Python : **accélération ~137×**
- Parallèle (grille 400×400, 5000 itérations) : speedup max **1.61×** avec 4 workers
- Communication (ghost + Gatherv) domine à 8 workers (54% du temps total)
- Le ratio calcul/communication limite l'efficacité sur petites grilles

### TP5 : Calcul GPU avec PyCUDA

**Objectifs :**
- Programmer des kernels CUDA en Python via PyCUDA sur Google Colab (Tesla T4)
- Comprendre l'indexation des threads et blocs CUDA (1D et 2D)
- Comparer les performances CPU (NumPy) vs GPU (CUDA)

**Résultats clés :**
- Addition vectorielle (N=10M) : **speedup 33.64×**
- Mandelbrot (1000×1000, 100 itérations) : **speedup 5235×**
- Mandelbrot haute résolution (4000×4000, 200 itérations) : **speedup 13 497×**
- Le speedup GPU/CPU augmente avec la taille du problème (paradigme SIMT)

---

## 🛠️ Environnement de développement

### TP1 (C++/OpenMP)
```bash
# Compilation
make all

# Exécution
./TestProductMatrix.exe 1024
```

### TP2 (Python/MPI)
```bash
# Installation des dépendances
pip install numpy mpi4py pillow matplotlib

# Exécution MPI
mpirun -np 4 python3 mandelbrot_block.py
```

### TP3 (C++/MPI)
```bash
cd tp3/sources

# Compilation
make all

# Exécution
./bucket_sort_seq.exe 1000000                    # Version séquentielle
mpirun -np 4 ./bucket_sort_mpi.exe 1000000       # Version parallèle
```

### TP4 (Python/MPI/pygame)
```bash
# Simulation avec affichage (1 controller + 3 workers)
mpirun -np 4 python3 tp4/game_of_life.py glider_gun

# Benchmark headless
mpirun -np 4 python3 tp4/benchmark_headless.py --steps 5000 --pattern block_switch_engine
```

### TP5 (Python/PyCUDA — Google Colab)
```bash
# Exécuter le notebook TP5_LIANG_Tianyi.ipynb sur Google Colab
# Prérequis : activer le runtime GPU (Tesla T4)
# Le notebook installe PyCUDA automatiquement via pip
```

---

## 📊 Résultats expérimentaux

Les résultats détaillés sont disponibles dans chaque rapport :
- [Résultats TP1](tp1/TP1_Rapport.md#résultats)
- [Résultats TP2](tp2/TP2_Rapport.md#résultats-expérimentaux)
- [Résultats TP3](tp3/TP3_Rapport.md#résultats-expérimentaux)
- [Résultats TP4](tp4/TP4_Rapport.md#3-résultats-expérimentaux)
- [Résultats TP5](tp5/TP5_Rapport.md)

---

## 📚 Références

- Support de cours : [transparents/](../transparents/)
- Exemples MPI : [Exemples/MPI/](../Exemples/MPI/)
- Documentation MPI : https://mpi4py.readthedocs.io/

---

*Dernière mise à jour : Février 2026*
