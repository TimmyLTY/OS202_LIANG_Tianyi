/**
 * Bucket Sort - Version Séquentielle (Référence)
 * 
 * TP3 - Parallélisation du Bucket Sort
 * Auteur: LIANG Tianyi
 * 
 * Ce programme implémente un bucket sort séquentiel pour servir de
 * référence de performance et de vérification de correction.
 */

#include <iostream>
#include <vector>
#include <algorithm>
#include <random>
#include <chrono>
#include <cstdlib>
#include <iomanip>

/**
 * Génère un vecteur de nombres aléatoires dans [0, 1)
 */
std::vector<double> generate_random_data(size_t n, unsigned int seed) {
    std::vector<double> data(n);
    std::mt19937 gen(seed);
    std::uniform_real_distribution<double> dist(0.0, 1.0);
    
    for (size_t i = 0; i < n; ++i) {
        data[i] = dist(gen);
    }
    return data;
}

/**
 * Bucket Sort séquentiel
 * 
 * Algorithme:
 * 1. Créer k buckets (intervalles égaux de [0, 1))
 * 2. Distribuer chaque élément dans son bucket
 * 3. Trier chaque bucket
 * 4. Concaténer les buckets
 */
void bucket_sort(std::vector<double>& data, int num_buckets) {
    if (data.empty()) return;
    
    size_t n = data.size();
    std::vector<std::vector<double>> buckets(num_buckets);
    
    // Réserver de l'espace pour éviter les réallocations
    for (auto& bucket : buckets) {
        bucket.reserve(n / num_buckets + 10);
    }
    
    // Distribution dans les buckets
    for (const auto& val : data) {
        int bucket_idx = static_cast<int>(val * num_buckets);
        // Gérer le cas val == 1.0
        if (bucket_idx >= num_buckets) bucket_idx = num_buckets - 1;
        buckets[bucket_idx].push_back(val);
    }
    
    // Tri de chaque bucket
    for (auto& bucket : buckets) {
        std::sort(bucket.begin(), bucket.end());
    }
    
    // Concaténation des buckets
    size_t idx = 0;
    for (const auto& bucket : buckets) {
        for (const auto& val : bucket) {
            data[idx++] = val;
        }
    }
}

/**
 * Vérifie si un vecteur est trié
 */
bool is_sorted(const std::vector<double>& data) {
    for (size_t i = 1; i < data.size(); ++i) {
        if (data[i] < data[i-1]) return false;
    }
    return true;
}

int main(int argc, char* argv[]) {
    // Paramètres par défaut
    size_t n = 1000000;  // 1 million d'éléments
    int num_buckets = 100;
    unsigned int seed = 42;
    
    // Lecture des arguments
    if (argc >= 2) n = std::atol(argv[1]);
    if (argc >= 3) num_buckets = std::atoi(argv[2]);
    if (argc >= 4) seed = std::atoi(argv[3]);
    
    std::cout << "=== Bucket Sort Séquentiel ===" << std::endl;
    std::cout << "N = " << n << " éléments" << std::endl;
    std::cout << "Buckets = " << num_buckets << std::endl;
    std::cout << "Seed = " << seed << std::endl;
    std::cout << std::endl;
    
    // Génération des données
    auto start_gen = std::chrono::high_resolution_clock::now();
    std::vector<double> data = generate_random_data(n, seed);
    auto end_gen = std::chrono::high_resolution_clock::now();
    double time_gen = std::chrono::duration<double>(end_gen - start_gen).count();
    
    std::cout << "Temps de génération : " << std::fixed << std::setprecision(4) 
              << time_gen << " s" << std::endl;
    
    // Tri
    auto start_sort = std::chrono::high_resolution_clock::now();
    bucket_sort(data, num_buckets);
    auto end_sort = std::chrono::high_resolution_clock::now();
    double time_sort = std::chrono::duration<double>(end_sort - start_sort).count();
    
    std::cout << "Temps de tri        : " << std::fixed << std::setprecision(4) 
              << time_sort << " s" << std::endl;
    
    // Vérification
    bool sorted = is_sorted(data);
    std::cout << std::endl;
    std::cout << "Vérification : " << (sorted ? "✓ Tableau trié correctement" 
                                              : "✗ ERREUR: Tableau non trié!") 
              << std::endl;
    
    // Affichage de quelques valeurs
    std::cout << std::endl;
    std::cout << "Premiers éléments : ";
    for (size_t i = 0; i < std::min(n, size_t(5)); ++i) {
        std::cout << std::fixed << std::setprecision(4) << data[i] << " ";
    }
    std::cout << std::endl;
    
    std::cout << "Derniers éléments : ";
    size_t start_idx = n > 5 ? n - 5 : 0;
    for (size_t i = start_idx; i < n; ++i) {
        std::cout << std::fixed << std::setprecision(4) << data[i] << " ";
    }
    std::cout << std::endl;
    
    return sorted ? 0 : 1;
}
