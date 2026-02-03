#!/bin/bash
# ============================================================
# Script d'expérimentation - TP3 Bucket Sort Parallèle
# Auteur: LIANG Tianyi
# ============================================================

# Configuration
RESULTS_DIR="../results"
mkdir -p $RESULTS_DIR

# Tailles de données à tester
SIZES="100000 1000000 10000000"

# Nombres de processus à tester
PROCS="1 2 4 8"

# Seed pour la reproductibilité
SEED=42

echo "============================================================"
echo "TP3 - Bucket Sort Parallèle - Expérimentations"
echo "============================================================"
echo ""

# Compilation
echo ">>> Compilation..."
make clean
make all
if [ $? -ne 0 ]; then
    echo "ERREUR: La compilation a échoué!"
    exit 1
fi
echo ">>> Compilation terminée."
echo ""

# ============================================================
# Expérience 1: Version séquentielle (référence)
# ============================================================
echo "============================================================"
echo "Expérience 1: Version séquentielle (référence)"
echo "============================================================"

echo "N,Temps_Generation,Temps_Tri,Temps_Total" > $RESULTS_DIR/sequential_results.csv

for N in $SIZES; do
    echo ""
    echo ">>> Séquentiel avec N = $N"
    
    # Capturer la sortie du programme
    OUTPUT=$(./bucket_sort_seq.exe $N 100 $SEED)
    echo "$OUTPUT"
    
    # Extraire les temps (format: "Temps de génération : X.XXXX s")
    TIME_GEN=$(echo "$OUTPUT" | grep "Temps de génération" | sed 's/.*: \([0-9.]*\) s/\1/')
    TIME_SORT=$(echo "$OUTPUT" | grep "Temps de tri" | sed 's/.*: \([0-9.]*\) s/\1/')
    
    # Calculer le temps total
    TIME_TOTAL=$(echo "$TIME_GEN + $TIME_SORT" | bc -l 2>/dev/null || echo "")
    
    # Écrire dans le CSV
    echo "$N,$TIME_GEN,$TIME_SORT,$TIME_TOTAL" >> $RESULTS_DIR/sequential_results.csv
done

echo ""

# ============================================================
# Expérience 2: Version parallèle MPI
# ============================================================
echo "============================================================"
echo "Expérience 2: Version parallèle MPI"
echo "============================================================"

echo "N,Processus,Temps_Scatter,Temps_LocalSort,Temps_Sample,Temps_AlltoAll,Temps_Merge,Temps_Gather,Temps_Total" > $RESULTS_DIR/parallel_results.csv

for N in $SIZES; do
    echo ""
    echo ">>> Données: N = $N"
    echo "-----------------------------------------------------------"
    
    for P in $PROCS; do
        echo ""
        echo ">>> mpirun -np $P ./bucket_sort_mpi.exe $N"
        
        # Capturer la sortie du programme
        OUTPUT=$(mpirun --oversubscribe -np $P ./bucket_sort_mpi.exe $N $SEED 2>&1)
        echo "$OUTPUT"
        
        # Extraire les temps avec sed (plus robuste que awk pour ce format)
        TIME_SCATTER=$(echo "$OUTPUT" | grep "Scatter (distribution)" | sed 's/.*: \([0-9.]*\) s/\1/')
        TIME_LOCAL=$(echo "$OUTPUT" | grep "Tri local" | sed 's/.*: \([0-9.]*\) s/\1/')
        TIME_SAMPLE=$(echo "$OUTPUT" | grep "Échantillonnage" | sed 's/.*: \([0-9.]*\) s/\1/')
        TIME_ALLTOALL=$(echo "$OUTPUT" | grep "All-to-All " | sed 's/.*: \([0-9.]*\) s/\1/')
        TIME_MERGE=$(echo "$OUTPUT" | grep "Tri fusion" | sed 's/.*: \([0-9.]*\) s/\1/')
        TIME_GATHER=$(echo "$OUTPUT" | grep "Gather (rassemblement)" | sed 's/.*: \([0-9.]*\) s/\1/')
        TIME_TOTAL=$(echo "$OUTPUT" | grep "Temps total parallèle" | sed 's/.*: \([0-9.]*\) s/\1/')
        
        # Écrire dans le CSV
        echo "$N,$P,$TIME_SCATTER,$TIME_LOCAL,$TIME_SAMPLE,$TIME_ALLTOALL,$TIME_MERGE,$TIME_GATHER,$TIME_TOTAL" >> $RESULTS_DIR/parallel_results.csv
        
        echo ""
    done
done

echo ""
echo "============================================================"
echo "Expérimentations terminées!"
echo "Résultats sauvegardés dans: $RESULTS_DIR"
echo "============================================================"
echo ""
echo ">>> Contenu des fichiers CSV:"
echo ""
echo "=== sequential_results.csv ==="
cat $RESULTS_DIR/sequential_results.csv
echo ""
echo "=== parallel_results.csv ==="
cat $RESULTS_DIR/parallel_results.csv
echo ""
echo ">>> Pour générer les graphiques:"
echo "    pip3 install pandas matplotlib"
echo "    python3 plot_results.py"
