#!/bin/bash

# TP2 - Script d'exécution complet de toutes les expériences
# Usage: ./run_all_tp2_experiments.sh

echo "========================================"
echo "TP2 - Expériences complètes"
echo "Date: $(date)"
echo "========================================"

# Se placer dans le répertoire tp2
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Options MPI pour supprimer les avertissements réseau
export OMPI_MCA_btl_base_warn_component_unused=0
export OMPI_MCA_btl="^tcp"
MPI_OPTS="--oversubscribe --mca btl_base_warn_component_unused 0 --mca opal_warn_on_missing_libcuda 0"

# Créer le répertoire de résultats
mkdir -p results

# Fichier de résultats
RESULTS_FILE="results/tp2_results_$(date +%Y%m%d_%H%M%S).txt"

echo "Résultats sauvegardés dans: $RESULTS_FILE"
echo ""

{
    echo "========================================"
    echo "TP2 - Résultats des expériences"
    echo "Date: $(date)"
    echo "========================================"
    echo ""

    # === Partie 1 : Mandelbrot ===
    echo "########################################"
    echo "# PARTIE 1 : ENSEMBLE DE MANDELBROT   #"
    echo "########################################"
    echo ""

    # 1.0 Séquentiel
    echo "--- 1.0 Version séquentielle (référence) ---"
    python3 mandelbrot.py
    echo ""

    # 1.1 Partition par blocs
    echo "--- 1.1 Partition par blocs de lignes ---"
    for np in 1 2 4 8; do
        echo ">>> mpirun -np $np <<<"
        mpirun $MPI_OPTS -np $np python3 mandelbrot_block.py
        echo ""
    done

    # 1.2 Répartition cyclique
    echo "--- 1.2 Répartition cyclique ---"
    for np in 1 2 4 8; do
        echo ">>> mpirun -np $np <<<"
        mpirun $MPI_OPTS -np $np python3 mandelbrot_cyclic.py
        echo ""
    done

    # 1.3 Maître-Esclave
    echo "--- 1.3 Stratégie Maître-Esclave ---"
    for np in 2 4 8; do
        echo ">>> mpirun -np $np <<<"
        mpirun $MPI_OPTS -np $np python3 mandelbrot_master_slave.py
        echo ""
    done

    # === Partie 2 : Produit Matrice-Vecteur ===
    echo ""
    echo "########################################"
    echo "# PARTIE 2 : PRODUIT MATRICE-VECTEUR  #"
    echo "########################################"
    echo ""

    # 2.a Par colonnes
    echo "--- 2.a Découpage par colonnes ---"
    for np in 1 2 4 8; do
        echo ">>> mpirun -np $np <<<"
        mpirun $MPI_OPTS -np $np python3 matvec_col.py
        echo ""
    done

    # 2.b Par lignes
    echo "--- 2.b Découpage par lignes ---"
    for np in 1 2 4 8; do
        echo ">>> mpirun -np $np <<<"
        mpirun $MPI_OPTS -np $np python3 matvec_row.py
        echo ""
    done

    echo ""
    echo "========================================"
    echo "Expériences terminées!"
    echo "========================================"

} 2>&1 | tee "$RESULTS_FILE"

echo ""
echo "Toutes les expériences sont terminées."
echo "Résultats sauvegardés dans: $RESULTS_FILE"
echo ""

# Lister les images générées
echo "Images générées:"
ls -la *.png 2>/dev/null || echo "Aucune image trouvée"
