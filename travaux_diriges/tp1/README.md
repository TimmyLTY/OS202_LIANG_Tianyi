# TP1 - Produit Matrice-Matrice et Parallélisation OpenMP

**Auteur :** LIANG Tianyi  
**Date :** 21 janvier 2026

---

## 📋 Contenu du TP

Ce TP porte sur l'optimisation et la parallélisation du produit matrice-matrice en C++. Il couvre :

1. **Analyse de l'ordre des boucles** et impact sur les performances (cache)
2. **Optimisation par blocking** pour améliorer la localité des données
3. **Comparaison avec BLAS** (bibliothèque optimisée)
4. **Parallélisation OpenMP** 
5. **Circulation de jeton MPI** (exercice complémentaire)

---

## 📁 Structure du dossier

```
tp1/
├── README.md                # Ce fichier
├── Sujet.pdf                # Énoncé du TP
├── Sujet.tex                # Source LaTeX de l'énoncé
├── TP1_Rapport.md           # Rapport complet avec analyse
│
├── sources/                 # Code source C++
│   ├── ProdMatMat.cpp       # Implémentation du produit matrice
│   ├── Matrix.hpp           # Classe matrice template
│   ├── TestProductMatrix.cpp # Programme de test principal
│   ├── Makefile             # Script de compilation
│   ├── Make_linux.inc       # Configuration Linux
│   ├── Make_osx.inc         # Configuration macOS
│   └── ...
│
└── solution/                # Solutions additionnelles
    ├── jeton_anneau.py      # Circulation de jeton MPI en Python
    └── calcul_pi.cpp        # Calcul parallèle de π
```

---

## 🛠️ Prérequis

### Compilation C++
```bash
# Compilateur avec support OpenMP
g++ --version

# Bibliothèque BLAS (optionnel pour comparaison)
# Linux: sudo apt install libblas-dev
# macOS: Accelerate framework inclus
```

### MPI pour exercices Python
```bash
pip install mpi4py numpy
```

---

## 🚀 Compilation et exécution

### Compiler le projet
```bash
cd sources/
make all
```

### Exécuter les tests
```bash
# Test avec matrice 1024×1024
./TestProductMatrix.exe 1024

# Varier le nombre de threads OpenMP
export OMP_NUM_THREADS=4
./TestProductMatrix.exe 1024
```

### Circulation de jeton MPI
```bash
cd solution/
mpirun -np 4 python3 jeton_anneau.py
```

---

## 📊 Résultats principaux

### Impact de l'ordre des boucles

| Ordre | Performance | Raison |
|-------|-------------|--------|
| `ijk` | ~50 MFLOPS | Mauvaise localité colonne B |
| `ikj` | **~200 MFLOPS** | Accès contigus en mémoire |
| `jik` | ~45 MFLOPS | Pire cas |

### Comparaison des méthodes

| Méthode | GFLOPS | Commentaire |
|---------|--------|-------------|
| Naïf (ijk) | 0.05 | Baseline |
| Optimisé (ikj) | 0.20 | 4× plus rapide |
| Blocking | 0.23 | +15% vs ikj |
| OpenMP (4 threads) | 0.68 | Speedup 3.4× |
| BLAS | **3.20** | 16× plus rapide |

---

## 📖 Documentation

- **Rapport complet :** [TP1_Rapport.md](TP1_Rapport.md)
- **Énoncé du TP :** [Sujet.pdf](Sujet.pdf)
- **Retour à l'index :** [../README.md](../README.md)

---

*Dernière mise à jour : Janvier 2026*
