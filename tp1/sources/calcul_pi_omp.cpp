/**
 * TP1 - Section 2.2 : Calcul approché de π - Version OpenMP
 * 
 * Parallélisation en mémoire partagée avec OpenMP
 * 
 * Compilation : g++ -O2 -fopenmp -o calcul_pi_omp.exe calcul_pi_omp.cpp
 * Exécution   : OMP_NUM_THREADS=4 ./calcul_pi_omp.exe [nombre_de_points]
 */

#include <iostream>
#include <random>
#include <chrono>
#include <cstdlib>
#include <iomanip>
#include <cmath>

#if defined(_OPENMP)
#include <omp.h>
#endif

double approximate_pi_openmp(unsigned long nbSamples)
{
    unsigned long totalDarts = 0;
    
    #pragma omp parallel reduction(+:totalDarts)
    {
        int thread_id = omp_get_thread_num();
        int num_threads = omp_get_num_threads();
        
        // Chaque thread a sa propre graine
        unsigned int seed = std::chrono::system_clock::now().time_since_epoch().count() + thread_id * 1000;
        std::default_random_engine generator(seed);
        std::uniform_real_distribution<double> distribution(-1.0, 1.0);
        
        // Calcul de la portion de travail pour ce thread
        unsigned long samples_per_thread = nbSamples / num_threads;
        unsigned long start = thread_id * samples_per_thread;
        unsigned long end = (thread_id == num_threads - 1) ? nbSamples : start + samples_per_thread;
        
        unsigned long localDarts = 0;
        for (unsigned long sample = start; sample < end; ++sample) {
            double x = distribution(generator);
            double y = distribution(generator);
            if (x * x + y * y <= 1.0) {
                localDarts++;
            }
        }
        totalDarts += localDarts;
    }
    
    return 4.0 * static_cast<double>(totalDarts) / static_cast<double>(nbSamples);
}

int main(int argc, char* argv[])
{
    unsigned long nbSamples = 100000000;  // 10^8 par défaut
    
    if (argc > 1) {
        nbSamples = std::atol(argv[1]);
    }
    
    int num_threads;
    #pragma omp parallel
    {
        #pragma omp single
        num_threads = omp_get_num_threads();
    }
    
    std::cout << "=== Calcul de π - Version OpenMP ===" << std::endl;
    std::cout << "Nombre de points  : " << nbSamples << std::endl;
    std::cout << "Nombre de threads : " << num_threads << std::endl;
    
    // Mesure du temps
    auto start = std::chrono::high_resolution_clock::now();
    
    double pi = approximate_pi_openmp(nbSamples);
    
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    
    double error = std::abs(pi - M_PI) / M_PI * 100.0;
    
    std::cout << std::fixed << std::setprecision(10);
    std::cout << "π calculé  : " << pi << std::endl;
    std::cout << "π réel     : " << M_PI << std::endl;
    std::cout << "Erreur     : " << std::setprecision(6) << error << " %" << std::endl;
    std::cout << "Temps      : " << elapsed.count() << " secondes" << std::endl;
    
    return 0;
}
