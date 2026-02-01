# TP2 - Parallélisation MPI

**Auteur :** LIANG Tianyi  
**Date :** 27 janvier 2026

---

## 📋 Contenu du TP

Ce TP porte sur la parallélisation avec MPI (Message Passing Interface) en Python. Il couvre :

1. **Parallélisation de l'ensemble de Mandelbrot** avec 3 stratégies différentes
2. **Produit matrice-vecteur distribué** avec 2 approches
3. **Questions théoriques** sur les lois d'Amdahl et Gustafson

---

## 📁 Structure du dossier

```
tp2/
├── README.md                # Ce fichier
├── Sujet.md                 # Énoncé du TP
├── TP2_Rapport.md           # Rapport complet avec analyse
│
├── Code Mandelbrot/
│   ├── mandelbrot.py            # Version séquentielle (référence)
│   ├── mandelbrot_block.py      # Partition par blocs de lignes
│   ├── mandelbrot_cyclic.py     # Répartition cyclique
│   └── mandelbrot_master_slave.py # Stratégie maître-esclave
│
├── Code Produit Matrice-Vecteur/
│   ├── matvec.py            # Version séquentielle (référence)
│   ├── matvec_col.py        # Partition par colonnes (Allreduce)
│   └── matvec_row.py        # Partition par lignes (Allgather)
│
├── Outils/
│   ├── plot_results.py      # Génération des graphiques
│   └── run_all_tp2_experiments.sh # Script d'automatisation
│
├── images/                  # Images Mandelbrot générées
├── plots/                   # Graphiques de performance
└── results/                 # Résultats expérimentaux bruts
```

---

## 🛠️ Prérequis

```bash
# Python 3.x avec les packages suivants
pip install numpy mpi4py pillow matplotlib

# OpenMPI installé
mpirun --version
```

---

## 🚀 Exécution des expériences

### Version séquentielle (référence)
```bash
python3 mandelbrot.py
python3 matvec.py
```

### Mandelbrot - Partition par blocs
```bash
mpirun --mca btl_base_warn_component_unused 0 -np 1 python3 mandelbrot_block.py
mpirun --mca btl_base_warn_component_unused 0 -np 2 python3 mandelbrot_block.py
mpirun --mca btl_base_warn_component_unused 0 -np 4 python3 mandelbrot_block.py
mpirun --mca btl_base_warn_component_unused 0 -np 8 python3 mandelbrot_block.py
```

### Mandelbrot - Répartition cyclique
```bash
mpirun --mca btl_base_warn_component_unused 0 -np 4 python3 mandelbrot_cyclic.py
mpirun --mca btl_base_warn_component_unused 0 -np 8 python3 mandelbrot_cyclic.py
```

### Mandelbrot - Maître-esclave
```bash
mpirun --mca btl_base_warn_component_unused 0 -np 4 python3 mandelbrot_master_slave.py
mpirun --mca btl_base_warn_component_unused 0 -np 8 python3 mandelbrot_master_slave.py
```

### Produit matrice-vecteur
```bash
mpirun --mca btl_base_warn_component_unused 0 -np 4 python3 matvec_col.py
mpirun --mca btl_base_warn_component_unused 0 -np 4 python3 matvec_row.py
```

### Script automatisé
```bash
chmod +x run_all_tp2_experiments.sh
./run_all_tp2_experiments.sh
```

---

## 📊 Résultats principaux

| Stratégie | 8 processus | Speedup | Efficacité |
|-----------|-------------|---------|------------|
| Séquentiel | 1.289 s | 1.00× | - |
| Partition blocs | 0.247 s | 5.31× | 66% |
| Répartition cyclique | 0.210 s | **6.10×** | 76% |
| Maître-esclave | 0.224 s | 5.75× | **82%** |

**Conclusion :** La répartition cyclique offre le meilleur speedup absolu, tandis que la stratégie maître-esclave a la meilleure efficacité grâce à l'équilibrage dynamique de charge.

---

## 📈 Graphiques

Les graphiques de performance sont disponibles dans le dossier `plots/` :

| Graphique | Description |
|-----------|-------------|
| `mandelbrot_speedup_comparison.png` | Comparaison des speedups |
| `mandelbrot_efficiency_comparison.png` | Évolution de l'efficacité |
| `mandelbrot_execution_time.png` | Temps d'exécution |
| `mandelbrot_load_balance_8p.png` | Équilibrage de charge |

---

## 📖 Documentation

- **Rapport complet :** [TP2_Rapport.md](TP2_Rapport.md)
- **Énoncé du TP :** [Sujet.md](Sujet.md)
- **Retour à l'index :** [../README.md](../README.md)

---

*Dernière mise à jour : Janvier 2026*

