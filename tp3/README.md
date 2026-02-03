# TD n°3 - Parallélisation du Bucket Sort

**Auteur :** LIANG Tianyi  
**Cours :** OS02 - Calcul Parallèle et Distribué  
**Langage :** C++ avec MPI

---

## 📋 Description

Ce TP implémente l'algorithme **Bucket Sort parallèle** avec MPI, basé sur l'approche **Sample Sort** décrite dans le cours.

L'algorithme se déroule en 6 étapes :
1. Le process 0 génère un tableau de nombres aléatoires
2. Distribution initiale des données (Scatterv)
3. Tri local sur chaque processus
4. Échantillonnage et calcul des frontières de buckets
5. Redistribution All-to-All selon les buckets
6. Rassemblement du tableau trié sur le process 0

---

## 📁 Structure du répertoire

```
tp3/
├── README.md              # Ce fichier
├── TP3_Rapport.md         # Rapport d'expérimentation
├── sources/               # Code source
│   ├── Makefile           # Compilation
│   ├── Make_linux.inc     # Configuration Linux
│   ├── bucket_sort_seq.cpp    # Version séquentielle
│   ├── bucket_sort_mpi.cpp    # Version parallèle MPI
│   └── run_experiments.sh     # Script d'automatisation
├── results/               # Résultats expérimentaux
└── images/                # Illustrations du cours
    ├── tp3_1.png
    └── tp3_2.png
```

---

## 🛠️ Prérequis (Ubuntu 22.04)

```bash
# Mise à jour du système
sudo apt update

# Outils de compilation
sudo apt install -y build-essential g++ make

# MPI
sudo apt install -y openmpi-bin libopenmpi-dev
```

---

## 🔧 Compilation

```bash
cd sources
make all
```

Cela produit :
- `bucket_sort_seq.exe` : version séquentielle (référence)
- `bucket_sort_mpi.exe` : version parallèle MPI

---

## 🚀 Exécution

### Version séquentielle

```bash
./bucket_sort_seq.exe <N> [num_buckets] [seed]

# Exemple avec 1 million d'éléments
./bucket_sort_seq.exe 1000000
```

### Version parallèle MPI

```bash
mpirun -np <P> ./bucket_sort_mpi.exe <N> [seed]

# Exemples
mpirun -np 2 ./bucket_sort_mpi.exe 1000000
mpirun -np 4 ./bucket_sort_mpi.exe 1000000
mpirun -np 8 ./bucket_sort_mpi.exe 1000000
```

### Exécution automatisée

```bash
chmod +x run_experiments.sh
./run_experiments.sh
```

---

## 📊 Exemple de sortie

```
=== Bucket Sort Parallèle MPI ===
N = 1000000 éléments
Processus = 4
Seed = 42

Temps de génération      : 0.0234 s

=== Temps par étape ===
Scatter (distribution)   : 0.0045 s
Tri local                : 0.0567 s
Échantillonnage          : 0.0012 s
All-to-All               : 0.0234 s
Tri fusion               : 0.0123 s
Gather (rassemblement)   : 0.0034 s

Temps total parallèle    : 0.1015 s

Vérification : ✓ Tableau trié correctement

Premiers éléments : 0.0000 0.0000 0.0001 0.0001 0.0002 
Derniers éléments : 0.9999 0.9999 0.9999 1.0000 1.0000 
```

---

## 📈 Métriques de performance

| Métrique | Formule |
|----------|---------|
| Speedup | $S(p) = \frac{T_{seq}}{T_{par}(p)}$ |
| Efficacité | $E(p) = \frac{S(p)}{p}$ |
| Scalabilité | Comportement de $S(p)$ quand $p$ augmente |

---

## 🔍 Algorithme Sample Sort

L'approche Sample Sort garantit un bon équilibrage de charge :

1. **Échantillonnage** : Chaque processus prélève p échantillons
2. **Pivot selection** : Tri des p² échantillons, sélection de p-1 pivots
3. **Distribution adaptative** : Les pivots définissent des frontières équilibrées

Cette méthode évite le déséquilibre qui peut survenir avec un partitionnement uniforme de l'espace [0, 1).

---

## 📚 Références

- Cours OS02 - Transparents n°3
- [MPI Documentation](https://www.open-mpi.org/doc/)
- [Sample Sort Algorithm](https://en.wikipedia.org/wiki/Samplesort)

---

*Dernière mise à jour : Février 2026*
