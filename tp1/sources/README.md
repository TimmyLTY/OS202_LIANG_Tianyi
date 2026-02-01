
# TD1 - Produit Matrice-Matrice : Analyse de Performance

`pandoc -s --toc README.md --css=./github-pandoc.css -o README.html`

**Auteur :** [Votre nom]  
**Date :** 20 janvier 2026  
**Environnement :** OrbStack Ubuntu sur macOS

---

## 1. Informations Système (lscpu)

*La commande `lscpu` fournit des informations utiles sur le processeur : nombre de cœurs, taille des caches, etc.*

```bash
$ lscpu
```

**Configuration matérielle :**

| Caractéristique | Valeur |
|-----------------|--------|
| Modèle CPU      | [À compléter] |
| Cœurs physiques | [À compléter] |
| Threads         | [À compléter] |
| Cache L1d       | [À compléter] |
| Cache L1i       | [À compléter] |
| Cache L2        | [À compléter] |
| Cache L3        | [À compléter] |

**Commande de compilation :**
```bash
g++ -std=c++14 -O2 -march=native -Wall -fopenmp
```

---

## 2. Produit Matrice-Matrice

### 2.1 Effet de la taille de la matrice

**Objectif :** Étudier l'impact de la dimension de la matrice sur les performances (MFlops).

**Commande :**
```bash
./TestProductMatrix.exe <n>
```

| n              | Temps (s) | MFlops    |
|----------------|-----------|-----------|
| 256            | [résultat]| [résultat]|
| 512            | [résultat]| [résultat]|
| 1024 (origine) | [résultat]| [résultat]|
| 2048           | [résultat]| [résultat]|
| 4096           | [résultat]| [résultat]|

**Analyse des résultats :**

Les performances varient en fonction de la taille de la matrice en raison de l'effet de cache :

- **Petites matrices (n ≤ 512)** : Les données tiennent entièrement dans le cache L2/L3, ce qui permet un accès rapide à la mémoire et des performances élevées.
- **Matrices moyennes (n = 1024)** : Les données commencent à dépasser la capacité du cache, entraînant des défauts de cache (cache misses) plus fréquents.
- **Grandes matrices (n ≥ 2048)** : Les données dépassent largement le cache, nécessitant des accès fréquents à la mémoire principale (RAM), ce qui ralentit significativement les calculs.

---

### 2.2 Permutation des boucles

**Objectif :** Analyser l'impact de l'ordre des boucles i, j, k sur les performances.

**Contexte :** La matrice est stockée en ordre colonne-majeur (column-major). L'ordre des boucles affecte le pattern d'accès mémoire et donc l'efficacité du cache.

**Commande de compilation :**
```bash
make clean && make TestProductMatrix.exe && ./TestProductMatrix.exe 1024
```

| Ordre des boucles | Temps (s) | MFlops (n=1024) | MFlops (n=2048) |
|-------------------|-----------|-----------------|-----------------|
| i,j,k (origine)   | [résultat]| [résultat]      | [résultat]      |
| j,i,k             | [résultat]| [résultat]      | [résultat]      |
| i,k,j             | [résultat]| [résultat]      | [résultat]      |
| k,i,j             | [résultat]| [résultat]      | [résultat]      |
| j,k,i             | [résultat]| [résultat]      | [résultat]      |
| k,j,i             | [résultat]| [résultat]      | [résultat]      |

**Analyse des résultats :**

L'ordre des boucles a un impact significatif sur les performances :

1. **Meilleur ordre attendu : i,k,j ou k,i,j**
   - La boucle interne sur `j` permet un accès séquentiel aux éléments de `C(i,j)` et `B(k,j)` en mémoire (stockage colonne-majeur).
   - Cela maximise la localité spatiale et l'utilisation du cache.

2. **Pire ordre attendu : j,i,k ou k,j,i**
   - Les accès mémoire sont non-contigus, provoquant de nombreux défauts de cache.

3. **Explication théorique :**
   - Pour `C(i,j) += A(i,k) * B(k,j)`, les matrices sont stockées par colonnes.
   - Un accès séquentiel à `i` (indice de ligne) avec `j` fixe est efficace.

---

### 2.3 Parallélisation OpenMP sur la meilleure boucle

**Objectif :** Mesurer le gain de performance avec la parallélisation OpenMP.

**Commande :**
```bash
OMP_NUM_THREADS=<N> ./TestProductMatrix.exe 1024
```

| OMP_NUM_THREADS | MFlops (n=512) | MFlops (n=1024) | MFlops (n=2048) | MFlops (n=4096) |
|-----------------|----------------|-----------------|-----------------|-----------------|
| 1               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 2               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 3               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 4               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 5               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 6               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 7               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 8               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |

**Calcul du Speedup :**

$$Speedup(N) = \frac{MFlops(N\ threads)}{MFlops(1\ thread)}$$

| OMP_NUM_THREADS | Speedup (n=512) | Speedup (n=1024) | Speedup (n=2048) | Speedup (n=4096) |
|-----------------|-----------------|------------------|------------------|------------------|
| 1               | 1.00            | 1.00             | 1.00             | 1.00             |
| 2               | [calcul]        | [calcul]         | [calcul]         | [calcul]         |
| 4               | [calcul]        | [calcul]         | [calcul]         | [calcul]         |
| 8               | [calcul]        | [calcul]         | [calcul]         | [calcul]         |

**Analyse des résultats :**

1. **Efficacité parallèle :** Le speedup idéal serait égal au nombre de threads. En pratique, il est limité par :
   - La bande passante mémoire (memory bandwidth)
   - La contention de cache entre les threads
   - L'overhead de synchronisation OpenMP
   - La loi d'Amdahl (partie séquentielle du code)

2. **Effet de la taille :** Les grandes matrices (n=4096) bénéficient généralement mieux de la parallélisation car le ratio calcul/communication est plus favorable.

---

### 2.4 Produit par blocs

**Objectif :** Optimiser l'utilisation du cache en découpant les matrices en blocs.

**Principe :** Le produit par blocs permet de garder les données en cache plus longtemps, réduisant les accès à la mémoire principale.

**Commande :**
```bash
./TestProductMatrix.exe 1024
```

| szBlock (taille bloc) | MFlops (n=512) | MFlops (n=1024) | MFlops (n=2048) | MFlops (n=4096) |
|-----------------------|----------------|-----------------|-----------------|-----------------|
| origine (=max)        | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 32                    | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 64                    | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 128                   | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 256                   | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 512                   | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 1024                  | [résultat]     | [résultat]      | [résultat]      | [résultat]      |

**Analyse des résultats :**

1. **Taille de bloc optimale :** Elle dépend de la taille du cache L1/L2.
   - Pour un cache L1 de 32KB : bloc optimal ≈ 32-64
   - Pour un cache L2 de 256KB : bloc optimal ≈ 128-256

2. **Compromis :** 
   - Blocs trop petits : overhead de gestion des boucles
   - Blocs trop grands : dépassement du cache, perte d'efficacité

---

### 2.5 Combinaison Bloc + OpenMP

**Objectif :** Combiner l'optimisation par blocs avec la parallélisation.

| szBlock | OMP_NUM_THREADS | MFlops (n=512) | MFlops (n=1024) | MFlops (n=2048) | MFlops (n=4096) |
|---------|-----------------|----------------|-----------------|-----------------|-----------------|
| 512     | 1               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 512     | 8               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 1024    | 1               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |
| 1024    | 8               | [résultat]     | [résultat]      | [résultat]      | [résultat]      |

**Analyse des résultats :**

La combinaison des deux optimisations peut être synergique ou antagoniste :
- **Synergique :** Chaque thread travaille sur son propre bloc, minimisant la contention de cache.
- **Antagoniste :** Si les blocs sont trop grands, plusieurs threads peuvent entrer en compétition pour le cache partagé.

---

### 2.6 Comparaison avec BLAS, Eigen et NumPy

**Objectif :** Comparer notre implémentation avec des bibliothèques optimisées.

**BLAS (Basic Linear Algebra Subprograms) :**
```bash
./test_product_matrice_blas.exe 1024
```

| n    | Notre implémentation (MFlops) | BLAS (MFlops) | Ratio BLAS/Notre |
|------|-------------------------------|---------------|------------------|
| 1024 | [résultat]                    | [résultat]    | [calcul]         |
| 2048 | [résultat]                    | [résultat]    | [calcul]         |
| 4096 | [résultat]                    | [résultat]    | [calcul]         |

**Analyse des résultats :**

Les bibliothèques comme BLAS sont hautement optimisées :
- Utilisation d'instructions SIMD (SSE, AVX)
- Optimisation spécifique au processeur
- Algorithmes de blocking sophistiqués
- Prefetching optimisé

---

## 3. Conclusion

### Résumé des optimisations

| Optimisation | Gain de performance |
|--------------|---------------------|
| Ordre des boucles optimal | [×N] |
| Parallélisation (8 threads) | [×N] |
| Blocking optimal | [×N] |
| Bloc + OMP | [×N] |
| BLAS vs notre code | [×N] |

### Recommandations

1. **Pour le code de production :** Utiliser des bibliothèques optimisées (BLAS, Eigen, NumPy).
2. **Pour l'apprentissage :** Comprendre les effets du cache et de la parallélisation est essentiel.
3. **Optimisations clés :**
   - Choisir l'ordre des boucles adapté au stockage mémoire
   - Utiliser le blocking pour améliorer la localité de cache
   - Paralléliser les boucles externes avec OpenMP

---

## Annexe : Commandes utiles

```bash
# Compilation
make clean && make TestProductMatrix.exe

# Test avec différentes tailles
./TestProductMatrix.exe 1024

# Test avec OpenMP
OMP_NUM_THREADS=4 ./TestProductMatrix.exe 1024

# Boucle de test automatique
for i in $(seq 1 8); do
    echo "=== OMP_NUM_THREADS=$i ==="
    OMP_NUM_THREADS=$i ./TestProductMatrix.exe 1024
done

# Informations système
lscpu | grep -E "Model|CPU|Thread|Core|cache"
```
