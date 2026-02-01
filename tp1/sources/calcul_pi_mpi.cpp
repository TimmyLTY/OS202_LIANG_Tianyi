/**
 * TP1 - Section 2.2 : Calcul approché de π - Version MPI
 * 
 * Parallélisation en mémoire distribuée avec MPI
 * Chaque processus génère sa portion de points, puis on utilise MPI_Reduce
 * pour sommer les résultats.
 * 
 * Compilation : mpic++ -O2 -o calcul_pi_mpi.exe calcul_pi_mpi.cpp
 * Exécution   : mpirun -np 4 ./calcul_pi_mpi.exe [nombre_de_points]
 */

#include <iostream>
#include <random>
#include <chrono>
#include <cstdlib>
#include <iomanip>
#include <cmath>
#include <mpi.h>

int main(int argc, char* argv[])
{
    MPI_Init(&argc, &argv);
    
    int rank, nbp;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nbp);
    
    unsigned long nbSamples = 100000000;  // 10^8 par défaut
    
    if (argc > 1) {
        nbSamples = std::atol(argv[1]);
    }
    
    // Chaque processus traite sa portion
    unsigned long samplesPerProc = nbSamples / nbp;
    unsigned long myStart = rank * samplesPerProc;
    unsigned long myEnd = (rank == nbp - 1) ? nbSamples : myStart + samplesPerProc;
    unsigned long mySamples = myEnd - myStart;
    
    // Graine unique pour chaque processus
    unsigned int seed = std::chrono::system_clock::now().time_since_epoch().count() + rank * 12345;
    std::default_random_engine generator(seed);
    std::uniform_real_distribution<double> distribution(-1.0, 1.0);
    
    // Synchronisation avant le début de la mesure
    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();
    
    // Comptage local des points dans le cercle
    unsigned long localDarts = 0;
    for (unsigned long sample = 0; sample < mySamples; ++sample) {
        double x = distribution(generator);
        double y = distribution(generator);
        if (x * x + y * y <= 1.0) {
            localDarts++;
        }
    }
    
    // Réduction : somme de tous les compteurs locaux
    unsigned long totalDarts = 0;
    MPI_Reduce(&localDarts, &totalDarts, 1, MPI_UNSIGNED_LONG, MPI_SUM, 0, MPI_COMM_WORLD);
    
    // Synchronisation à la fin
    MPI_Barrier(MPI_COMM_WORLD);
    double end_time = MPI_Wtime();
    double elapsed = end_time - start_time;
    
    // Le processus 0 affiche le résultat
    if (rank == 0) {
        double pi = 4.0 * static_cast<double>(totalDarts) / static_cast<double>(nbSamples);
        double error = std::abs(pi - M_PI) / M_PI * 100.0;
        
        std::cout << "=== Calcul de π - Version MPI ===" << std::endl;
        std::cout << "Nombre de points     : " << nbSamples << std::endl;
        std::cout << "Nombre de processus  : " << nbp << std::endl;
        std::cout << std::fixed << std::setprecision(10);
        std::cout << "π calculé  : " << pi << std::endl;
        std::cout << "π réel     : " << M_PI << std::endl;
        std::cout << "Erreur     : " << std::setprecision(6) << error << " %" << std::endl;
        std::cout << "Temps      : " << elapsed << " secondes" << std::endl;
    }
    
    MPI_Finalize();
    return 0;
}
