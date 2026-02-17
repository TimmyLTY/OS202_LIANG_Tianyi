# TP4 — Le Jeu de la Vie : Parallélisation MPI

**Auteur :** LIANG Tianyi  
**Cours :** OS02 - Calcul Parallèle et Distribué  
**Date :** 17 février 2026

---

## 1. Introduction

Le jeu de la vie est un automate cellulaire inventé par John Conway.

L'objectif de ce TP est de paralléliser le calcul de la simulation via **MPI** en utilisant une **décomposition de domaine** par bandes horizontales avec échange de **cellules fantômes** (ghost cells).

---

## 2. Architecture du code

### 2.1 Structure MPI

Le code utilise deux communicateurs MPI :

- **`globCom`** : communicateur global (tous les processus)
- **`newCom`** : communicateur de calcul (créé par `globCom.Split(rank != 0, rank)`)

Le processus de **rang 0** joue le rôle de **contrôleur** (Controller) :
- Il ne participe pas au calcul
- Il gère l'affichage via pygame
- Il interroge périodiquement le groupe de calcul pour récupérer la grille globale

Les processus de **rang ≥ 1** forment le groupe de **workers** :
- Chacun possède un sous-domaine local de la grille
- Ils échangent leurs lignes frontières (ghost cells) entre voisins
- Ils rassemblent la grille globale via `Gatherv` pour l'envoi au contrôleur

### 2.2 Décomposition de domaine

La grille globale de dimensions $N_y \times N_x$ est découpée en **bandes horizontales** réparties entre les $P$ workers. Chaque worker gère `ny_local = ny // P` lignes (avec ajustement si la division n'est pas exacte).

```
Worker 0 :  lignes [0, ny_local)         + 2 ghost rows
Worker 1 :  lignes [ny_local, 2*ny_local) + 2 ghost rows
...
Worker P-1 : lignes [..., ny)             + 2 ghost rows
```

Chaque sous-domaine local a donc une taille de `(ny_local + 2) × nx`, où les 2 lignes supplémentaires sont les **ghost rows** — la première ligne contient les données du voisin du haut, la dernière celles du voisin du bas.

### 2.3 Échange de cellules fantômes

L'échange se fait via des communications non-bloquantes `Irecv` + bloquantes `Send` :

```python
def update_ghost_cells(self):
    # Réception non-bloquante des ghost rows
    req1 = newCom.Irecv(self.cells[-1,:], source=(rank+1)%size, tag=101)  # du voisin du bas
    req2 = newCom.Irecv(self.cells[0,:],  source=(rank-1)%size, tag=102)  # du voisin du haut
    # Envoi bloquant des lignes frontières
    newCom.Send(self.cells[-2,:], dest=(rank+1)%size, tag=102)  # ma dernière ligne → voisin du bas
    newCom.Send(self.cells[1,:],  dest=(rank-1)%size, tag=101)  # ma première ligne → voisin du haut
    req1.Wait()
    req2.Wait()
```

### 2.4 Calcul des voisins

Le calcul utilise `np.roll` pour décaler la grille dans les 8 directions et sommer les voisins :

```python
neighbours_count = sum(
    np.roll(np.roll(self.cells, i, 0), j, 1)
    for i in (-1, 0, 1) for j in (-1, 0, 1) if (i != 0 or j != 0)
)
next_cells = (neighbours_count == 3) | (self.cells & (neighbours_count == 2))
```

### 2.5 Diagramme de communication

```
     ┌──────────────────────────────────────────────┐
     │               Rang 0 (Controller)            │
     │  • pygame display                            │
     │  • send(1)/recv(grid) polling avec Iprobe    │
     └──────────────┬───────────────────────────────┘
                    │ globCom.send / recv
     ┌──────────────▼───────────────────────────────┐
     │            newCom (Workers)                  │
     │  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    │
     │  │ W0  │◄──►│ W1  │◄──►│ W2  │◄──►│ W3  │    │
     │  └──┬──┘    └─────┘    └─────┘    └──┬──┘    │
     │     └────────────── wrap ────────────┘       │
     │                                              │
     │Chaque Wi : compute → ghost_exchange → Gatherv│
     └──────────────────────────────────────────────┘
```

---

## 3. Résultats expérimentaux

### 3.1 Comparaison série : version naïve vs vectorisée

Avant la parallélisation, nous avons comparé les deux versions série sur le pattern `glider_gun` (200×100) :

| Version | Temps calcul/itération | Temps affichage/itération |
|---------|:----------------------:|:------------------------:|
| `game_of_life.py` (boucles Python) | **5.91×10⁻¹ s** | 5.69×10⁻² s |
| `game_of_life_vect.py` (convolve2d) | **4.32×10⁻³ s** | 5.93×10⁻² s |

**Accélération vectorisation : ~137×**

Le temps d'affichage est identique dans les deux cas (~60 ms), ce qui confirme que le goulot d'étranglement de la version naïve est bien le calcul, pas le rendu. La version vectorisée réduit le calcul à ~4 ms, rendant le rendu dominant.

### 3.2 Benchmark parallèle : `block_switch_engine` (400×400, 5000 itérations)

| Nb workers | T_calcul (s) | T_ghost (s) | T_gather (s) | T_total (s) | Speedup | Efficacité |
|:----------:|:------------:|:-----------:|:------------:|:-----------:|:-------:|:----------:|
| 1 (série)  | 1.107        | 0.016       | 0.024        | 1.147       | 0.96×   | 96.2%      |
| 2          | 0.780        | 0.029       | 0.037        | 0.847       | **1.31×** | 65.5%    |
| 4          | 0.603        | 0.032       | 0.057        | 0.692       | **1.61×** | 40.2%    |
| 8          | 0.761        | 0.329       | 0.569        | 1.660       | 0.96×   | 12.0%      |

**Répartition du temps (8 workers) :**
- Calcul : 45.8%
- Ghost exchange : 19.8%  
- Gatherv : 34.3%

### 3.3 Benchmark parallèle : `flat` (200×400, 5000 itérations)

| Nb workers | T_calcul (s) | T_ghost (s) | T_gather (s) | T_total (s) | Speedup | Efficacité |
|:----------:|:------------:|:-----------:|:------------:|:-----------:|:-------:|:----------:|
| 1 (série)  | 0.803        | 0.017       | 0.017        | 0.837       | 0.93×   | 93.5%      |
| 2          | 0.596        | 0.030       | 0.027        | 0.653       | **1.19×** | 59.5%    |
| 4          | 0.437        | 0.037       | 0.043        | 0.517       | **1.51×** | 37.8%    |
| 8          | 0.564        | 0.130       | 0.236        | 0.932       | 1.21×   | 15.1%      |

---

## 4. Analyse des résultats

### 4.1 Accélération et efficacité

L'accélération maximale observée est de **1.61×** avec 4 workers sur la grille 400×400. Cependant, l'efficacité est faible (40.2%), bien en dessous de l'efficacité idéale. Avec 8 workers, on observe même un **ralentissement** sur la grille 400×400 (speedup < 1).

### 4.2 Analyse du surcoût de communication

Le principal facteur limitant est le **ratio calcul/communication**. Pour une grille $N_y \times N_x$ découpée en $P$ bandes :

- **Volume de calcul** par worker : $O(N_y \cdot N_x / P)$
- **Volume de communication** ghost : $O(N_x)$ par échange (2 lignes)
- **Volume de communication** Gatherv : $O(N_y \cdot N_x / P)$ par itération

Avec $P = 8$ et une grille 400×400 :
- Chaque worker calcule seulement 50 lignes × 400 colonnes = 20 000 cellules
- Mais échange 2 lignes × 400 = 800 éléments (ghost) + 20 000 éléments (Gatherv)
- Le temps de calcul par itération (~0.15 ms) est du même ordre que la latence MPI

Le **rapport calcul/communication** est trop faible pour justifier 8 processus sur cette taille de grille.

### 4.3 Loi d'Amdahl

Avec une fraction parallélisable estimée à ~95% (le Gatherv et la synchronisation représentent ~5% en série), la loi d'Amdahl prédit :

$$S_{max}(P) = \frac{1}{(1-f) + f/P} = \frac{1}{0.05 + 0.95/P}$$

| P | Speedup théorique (Amdahl) | Speedup observé |
|:-:|:--------------------------:|:---------------:|
| 2 | 1.90× | 1.31× |
| 4 | 3.48× | 1.61× |
| 8 | 5.93× | 0.96× |

L'écart entre théorie et pratique s'explique par :
1. **La latence MPI** : chaque appel `Irecv`/`Send`/`Gatherv` a une latence fixe qui domine quand le volume de données est petit
2. **Le surcoût `Gatherv`** : rassembler la grille globale à chaque itération est coûteux et n'est pas strictement nécessaire au calcul (uniquement pour l'affichage)
3. **Le partage des cœurs CPU** (oversubscribe) : les 8 workers partagent les mêmes cœurs physiques

### 4.4 Pistes d'amélioration

1. **Réduire la fréquence du Gatherv** : rassembler la grille tous les N pas au lieu de chaque pas
2. **Augmenter la taille de la grille** : sur des grilles 1000×1000 ou plus, le ratio calcul/communication s'améliorerait
3. **Utiliser des communications non-bloquantes** : remplacer le Gatherv synchrone par des Isend/Irecv
4. **Recouvrement calcul/communication** : commencer le calcul des cellules intérieures pendant l'échange des ghost cells

---

## 5. Fichiers du projet

| Fichier | Description |
|---------|-------------|
| `game_of_life.py` | Implémentation parallèle MPI (controller + workers) |
| `game_of_life_parallel.py` | Copie identique (même architecture) |
| `benchmark_headless.py` | Benchmark sans affichage, mesure calcul/ghost/gather séparément |
| `benchmark_results.csv` | Résultats expérimentaux bruts |

### Exécution

```bash
# Simulation avec affichage (1 controller + 3 workers)
mpirun -np 4 python3 game_of_life.py glider_gun

# Benchmark headless (tous les rangs calculent)
mpirun -np 4 python3 benchmark_headless.py --steps 5000 --pattern block_switch_engine
```

---

## 6. Conclusion

Ce TP a permis d'étudier la parallélisation du jeu de la vie par décomposition de domaine MPI. Les résultats montrent que :

1. **La vectorisation** (passage de boucles Python à `np.roll`) apporte un gain considérable (~137×)
2. **La parallélisation MPI** apporte un gain supplémentaire modeste (jusqu'à 1.61× avec 4 workers) mais limité par le surcoût de communication
3. **Le ratio calcul/communication** est le facteur déterminant de l'efficacité parallèle : sur les petites grilles (400×400), la latence MPI domine rapidement
4. **Le Gatherv à chaque itération** constitue le principal goulot d'étranglement (jusqu'à 34% du temps total avec 8 workers)


