#!/bin/bash
# Test minimal pour mpi4py
echo "=== Test mpi4py ==="

echo "1. Vérification de l'installation..."
python3 -c "from mpi4py import MPI; print('mpi4py OK')" 2>&1

echo ""
echo "2. Test avec 2 processus..."
mpirun -np 2 python3 calcul_pi_mpi.py 1000000

echo ""
echo "3. Extraction du temps..."
OUTPUT=$(mpirun -np 2 python3 calcul_pi_mpi.py 1000000 2>&1)
echo "OUTPUT complet:"
echo "$OUTPUT"
echo ""
echo "Ligne Temps:"
echo "$OUTPUT" | grep "Temps"
echo ""
echo "Temps extrait avec sed:"
echo "$OUTPUT" | grep "Temps" | sed 's/.*: *//' | awk '{print $1}'
