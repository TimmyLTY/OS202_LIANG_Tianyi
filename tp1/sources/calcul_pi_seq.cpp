/**
 * TP1 - Section 2.2 : Calcul approché de π - Version séquentielle
 * 
 * Algorithme de Monte-Carlo : génère des points aléatoires dans [-1,1]x[-1,1]
 * et compte ceux qui tombent dans le cercle unité.
 * π ≈ 4 × (nombre de points dans le cercle / nombre total de points)
 * 
 * Compilation : g++ -O2 -o calcul_pi_seq.exe calcul_pi_seq.cpp
 * Exécution   : ./calcul_pi_seq.exe [nombre_de_points]
 */

#include <iostream>
#include <random>
#include <chrono>
#include <cstdlib>
#include <iomanip>
#include <cmath>

double approximate_pi_sequential(unsigned long nbSamples, unsigned int seed)
{
    std::default_random_engine generator(seed);
    std::uniform_real_distribution<double> distribution(-1.0, 1.0);
    
    unsigned long nbDarts = 0;
    
    for (unsigned long sample = 0; sample < nbSamples; ++sample) {
        double x = distribution(generator);
        double y = distribution(generator);
        if (x * x + y * y <= 1.0) {
            nbDarts++;
        }
    }
    
    return 4.0 * static_cast<double>(nbDarts) / static_cast<double>(nbSamples);
}

int main(int argc, char* argv[])
{
    unsigned long nbSamples = 100000000;  // 10^8 par défaut
    
    if (argc > 1) {
        nbSamples = std::atol(argv[1]);
    }
    
    std::cout << "=== Calcul de π - Version séquentielle ===" << std::endl;
    std::cout << "Nombre de points : " << nbSamples << std::endl;
    
    // Mesure du temps
    auto start = std::chrono::high_resolution_clock::now();
    
    // Génère une graine basée sur le temps
    unsigned int seed = std::chrono::system_clock::now().time_since_epoch().count();
    double pi = approximate_pi_sequential(nbSamples, seed);
    
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
