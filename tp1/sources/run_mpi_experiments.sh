#!/bin/bash
# =============================================================================
# TP1 - Section 2 : Parallélisation MPI - Script d'expérimentation
# 
# Ce script compile et exécute toutes les expériences de la section 2
# Usage: ./run_mpi_experiments.sh
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Nombre de points pour le calcul de π
N_POINTS=100000000  # 10^8

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  TP1 - Parallélisation MPI                ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# =============================================================================
# Section 2.1 : Circulation d'un jeton
# =============================================================================

echo -e "${CYAN}--- Section 2.1 : Circulation d'un jeton ---${NC}"
echo ""

echo -e "${YELLOW}Compilation...${NC}"
mpic++ -O2 -o circulation_jeton.exe circulation_jeton.cpp

echo -e "${YELLOW}Exécution avec différents nombres de processus :${NC}"
echo ""

for np in 2 4 8; do
    echo -e "${CYAN}=== $np processus ===${NC}"
    mpirun --mca btl_base_warn_component_unused 0 -np $np ./circulation_jeton.exe 2>/dev/null
    echo ""
done

# =============================================================================
# Section 2.2 : Calcul de π
# =============================================================================

echo -e "${CYAN}--- Section 2.2 : Calcul approché de π ---${NC}"
echo ""

# -----------------------------------------------------------------------------
# 2.2.1 Version séquentielle
# -----------------------------------------------------------------------------

echo -e "${YELLOW}Compilation de la version séquentielle...${NC}"
g++ -O2 -o calcul_pi_seq.exe calcul_pi_seq.cpp

echo -e "${YELLOW}Exécution de la version séquentielle :${NC}"
./calcul_pi_seq.exe $N_POINTS
echo ""

# Mesure du temps séquentiel pour calculer le speedup
SEQ_TIME=$(./calcul_pi_seq.exe $N_POINTS 2>&1 | grep "Temps" | awk '{print $3}')
echo "Temps séquentiel de référence : $SEQ_TIME secondes"
echo ""

# -----------------------------------------------------------------------------
# 2.2.2 Version OpenMP
# -----------------------------------------------------------------------------

echo -e "${CYAN}--- Version OpenMP ---${NC}"
echo ""

echo -e "${YELLOW}Compilation de la version OpenMP...${NC}"
g++ -O2 -fopenmp -o calcul_pi_omp.exe calcul_pi_omp.cpp

echo -e "${YELLOW}Test avec différents nombres de threads :${NC}"
echo ""

RESULTS_OMP="results_pi_omp.csv"
echo "threads,time,speedup" > $RESULTS_OMP

printf "%-10s | %-12s | %-10s\n" "Threads" "Temps (s)" "Speedup"
echo "-----------|--------------|----------"

for threads in 1 2 4 8; do
    OMP_TIME=$(OMP_NUM_THREADS=$threads ./calcul_pi_omp.exe $N_POINTS 2>&1 | grep "Temps" | awk '{print $3}')
    SPEEDUP=$(awk "BEGIN {printf \"%.2f\", $SEQ_TIME / $OMP_TIME}")
    printf "%-10s | %-12s | %-10s\n" "$threads" "$OMP_TIME" "${SPEEDUP}x"
    echo "$threads,$OMP_TIME,$SPEEDUP" >> $RESULTS_OMP
done

echo ""
echo -e "${GREEN}Résultats OpenMP sauvegardés dans: $RESULTS_OMP${NC}"
echo ""

# -----------------------------------------------------------------------------
# 2.2.3 Version MPI (C++)
# -----------------------------------------------------------------------------

echo -e "${CYAN}--- Version MPI (C++) ---${NC}"
echo ""

echo -e "${YELLOW}Compilation de la version MPI...${NC}"
mpic++ -O2 -o calcul_pi_mpi.exe calcul_pi_mpi.cpp

echo -e "${YELLOW}Test avec différents nombres de processus :${NC}"
echo ""

RESULTS_MPI="results_pi_mpi.csv"
echo "processes,time,speedup" > $RESULTS_MPI

printf "%-10s | %-12s | %-10s\n" "Processus" "Temps (s)" "Speedup"
echo "-----------|--------------|----------"

for np in 1 2 4 8; do
    MPI_TIME=$(mpirun --mca btl_base_warn_component_unused 0 -np $np ./calcul_pi_mpi.exe $N_POINTS 2>/dev/null | grep "Temps" | awk '{print $3}')
    if [ -n "$MPI_TIME" ]; then
        SPEEDUP=$(awk "BEGIN {printf \"%.2f\", $SEQ_TIME / $MPI_TIME}")
    else
        MPI_TIME="erreur"
        SPEEDUP="N/A"
    fi
    printf "%-10s | %-12s | %-10s\n" "$np" "$MPI_TIME" "${SPEEDUP}x"
    echo "$np,$MPI_TIME,$SPEEDUP" >> $RESULTS_MPI
done

echo ""
echo -e "${GREEN}Résultats MPI sauvegardés dans: $RESULTS_MPI${NC}"
echo ""

# -----------------------------------------------------------------------------
# 2.2.4 Version mpi4py (Python)
# -----------------------------------------------------------------------------

echo -e "${CYAN}--- Version mpi4py (Python) ---${NC}"
echo ""

# Vérification de mpi4py
if python3 -c "from mpi4py import MPI" 2>/dev/null; then
    echo -e "${YELLOW}Test avec différents nombres de processus :${NC}"
    echo ""

    RESULTS_MPI4PY="results_pi_mpi4py.csv"
    echo "processes,time,speedup" > $RESULTS_MPI4PY

    printf "%-10s | %-12s | %-10s\n" "Processus" "Temps (s)" "Speedup"
    echo "-----------|--------------|----------"

    for np in 1 2 4 8; do
        OUTPUT=$(mpirun --mca btl_base_warn_component_unused 0 -np $np python3 calcul_pi_mpi.py $N_POINTS 2>&1)
        MPI4PY_TIME=$(echo "$OUTPUT" | grep "Temps" | sed 's/.*: *//' | awk '{print $1}')
        if [ -n "$MPI4PY_TIME" ] && [ "$MPI4PY_TIME" != "" ]; then
            SPEEDUP=$(awk "BEGIN {printf \"%.2f\", $SEQ_TIME / $MPI4PY_TIME}")
        else
            # Afficher l'erreur pour le diagnostic
            echo "DEBUG: $OUTPUT" >&2
            MPI4PY_TIME="erreur"
            SPEEDUP="N/A"
        fi
        printf "%-10s | %-12s | %-10s\n" "$np" "$MPI4PY_TIME" "${SPEEDUP}x"
        echo "$np,$MPI4PY_TIME,$SPEEDUP" >> $RESULTS_MPI4PY
    done

    echo ""
    echo -e "${GREEN}Résultats mpi4py sauvegardés dans: $RESULTS_MPI4PY${NC}"
else
    echo -e "${RED}mpi4py non installé. Installation :${NC}"
    echo "pip install mpi4py numpy"
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Expériences terminées !                  ${NC}"
echo -e "${GREEN}============================================${NC}"
