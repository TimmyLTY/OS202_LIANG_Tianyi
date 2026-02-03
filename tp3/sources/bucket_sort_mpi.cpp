/**
 * Bucket Sort Parallèle - Version MPI
 *
 * TP3 - Parallélisation du Bucket Sort
 * Auteur: LIANG Tianyi
 *
 * Implémentation basée sur l'algorithme décrit dans le cours OS02:
 * 1. Process 0 génère un tableau de nombres arbitraires
 * 2. Il les dispatch aux autres processus
 * 3. Tous les processus participent au tri en parallèle
 * 4. Le tableau trié est rassemblé sur le process 0
 */

#include <algorithm>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <mpi.h>
#include <numeric>
#include <random>
#include <vector>

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
 * Vérifie si un vecteur est trié
 */
bool is_sorted(const std::vector<double> &data) {
  for (size_t i = 1; i < data.size(); ++i) {
    if (data[i] < data[i - 1])
      return false;
  }
  return true;
}

/**
 * Bucket Sort Parallèle MPI
 *
 * Algorithme:
 * 1. Process 0 génère et distribue les données (Scatter)
 * 2. Chaque processus trie ses données locales
 * 3. Échantillonnage pour déterminer les frontières des buckets
 * 4. All-to-All pour redistribuer selon les buckets
 * 5. Tri fusion local
 * 6. Gather vers process 0
 */
int main(int argc, char *argv[]) {
  MPI_Init(&argc, &argv);

  int rank, nbp;
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &nbp);

  // Paramètres
  size_t n = 1000000; // Nombre total d'éléments
  unsigned int seed = 42;

  if (argc >= 2)
    n = std::atol(argv[1]);
  if (argc >= 3)
    seed = std::atoi(argv[2]);

  // Calcul de la répartition (gestion du reste)
  size_t base_count = n / nbp;
  size_t remainder = n % nbp;
  size_t local_n = base_count + (static_cast<size_t>(rank) < remainder ? 1 : 0);

  // Calcul des counts et displacements pour Scatterv/Gatherv
  std::vector<int> sendcounts(nbp);
  std::vector<int> displs(nbp);
  for (int i = 0; i < nbp; ++i) {
    sendcounts[i] = static_cast<int>(
        base_count + (static_cast<size_t>(i) < remainder ? 1 : 0));
    displs[i] = (i == 0) ? 0 : displs[i - 1] + sendcounts[i - 1];
  }

  if (rank == 0) {
    std::cout << "=== Bucket Sort Parallèle MPI ===" << std::endl;
    std::cout << "N = " << n << " éléments" << std::endl;
    std::cout << "Processus = " << nbp << std::endl;
    std::cout << "Seed = " << seed << std::endl;
    std::cout << std::endl;
  }

  // Variables pour les mesures de temps
  double time_gen = 0, time_scatter = 0, time_local_sort = 0;
  double time_sample = 0, time_alltoall = 0, time_merge = 0, time_gather = 0;
  double start_time, end_time;

  // ============================================================
  // Étape 1: Génération des données (process 0 uniquement)
  // ============================================================
  std::vector<double> global_data;
  if (rank == 0) {
    start_time = MPI_Wtime();
    global_data = generate_random_data(n, seed);
    end_time = MPI_Wtime();
    time_gen = end_time - start_time;
    std::cout << "Temps de génération      : " << std::fixed
              << std::setprecision(4) << time_gen << " s" << std::endl;
  }

  // ============================================================
  // Étape 2: Distribution initiale (Scatterv)
  // ============================================================
  std::vector<double> local_data(local_n);

  MPI_Barrier(MPI_COMM_WORLD);
  start_time = MPI_Wtime();

  MPI_Scatterv(global_data.data(), sendcounts.data(), displs.data(), MPI_DOUBLE,
               local_data.data(), static_cast<int>(local_n), MPI_DOUBLE, 0,
               MPI_COMM_WORLD);

  end_time = MPI_Wtime();
  time_scatter = end_time - start_time;

  // ============================================================
  // Étape 3: Tri local
  // ============================================================
  start_time = MPI_Wtime();
  std::sort(local_data.begin(), local_data.end());
  end_time = MPI_Wtime();
  time_local_sort = end_time - start_time;

  // ============================================================
  // Étape 4: Échantillonnage et détermination des frontières
  // ============================================================
  start_time = MPI_Wtime();

  // Chaque processus prend nbp échantillons équidistants
  std::vector<double> local_samples(nbp);
  for (int i = 0; i < nbp; ++i) {
    size_t idx = (local_n > 0) ? (i * local_n / nbp) : 0;
    local_samples[i] = (local_n > 0) ? local_data[idx] : 0.0;
  }

  // Rassemblement de tous les échantillons sur tous les processus
  std::vector<double> all_samples(nbp * nbp);
  MPI_Allgather(local_samples.data(), nbp, MPI_DOUBLE, all_samples.data(), nbp,
                MPI_DOUBLE, MPI_COMM_WORLD);

  // Tri des échantillons et sélection des frontières
  std::sort(all_samples.begin(), all_samples.end());

  // Sélection de nbp-1 frontières (pivots)
  std::vector<double> pivots(nbp - 1);
  for (int i = 0; i < nbp - 1; ++i) {
    pivots[i] = all_samples[(i + 1) * nbp];
  }

  end_time = MPI_Wtime();
  time_sample = end_time - start_time;

  // ============================================================
  // Étape 5: Redistribution All-to-All
  // ============================================================
  start_time = MPI_Wtime();

  // Compter combien d'éléments vont à chaque processus
  std::vector<int> send_counts(nbp, 0);
  std::vector<std::vector<double>> buckets(nbp);

  for (const auto &val : local_data) {
    // Trouver le bucket approprié
    int bucket_idx = 0;
    for (int i = 0; i < nbp - 1; ++i) {
      if (val > pivots[i])
        bucket_idx = i + 1;
    }
    buckets[bucket_idx].push_back(val);
    send_counts[bucket_idx]++;
  }

  // Créer le buffer d'envoi contigu
  std::vector<double> send_buffer;
  send_buffer.reserve(local_n);
  std::vector<int> send_displs(nbp);
  send_displs[0] = 0;
  for (int i = 0; i < nbp; ++i) {
    if (i > 0)
      send_displs[i] = send_displs[i - 1] + send_counts[i - 1];
    for (const auto &val : buckets[i]) {
      send_buffer.push_back(val);
    }
  }

  // Échanger les counts
  std::vector<int> recv_counts(nbp);
  MPI_Alltoall(send_counts.data(), 1, MPI_INT, recv_counts.data(), 1, MPI_INT,
               MPI_COMM_WORLD);

  // Calculer les déplacements de réception
  std::vector<int> recv_displs(nbp);
  recv_displs[0] = 0;
  for (int i = 1; i < nbp; ++i) {
    recv_displs[i] = recv_displs[i - 1] + recv_counts[i - 1];
  }

  int total_recv = recv_displs[nbp - 1] + recv_counts[nbp - 1];
  std::vector<double> recv_buffer(total_recv);

  // All-to-Allv pour échanger les données
  MPI_Alltoallv(send_buffer.data(), send_counts.data(), send_displs.data(),
                MPI_DOUBLE, recv_buffer.data(), recv_counts.data(),
                recv_displs.data(), MPI_DOUBLE, MPI_COMM_WORLD);

  end_time = MPI_Wtime();
  time_alltoall = end_time - start_time;

  // ============================================================
  // Étape 6: Tri fusion local (merge des sous-listes triées)
  // ============================================================
  start_time = MPI_Wtime();

  // Les données reçues de chaque processus sont déjà triées
  // On fait un merge de nbp listes triées
  std::vector<double> sorted_local(total_recv);

  // Utiliser un heap pour le merge multi-voies
  using HeapElement =
      std::pair<double, std::pair<int, int>>; // (value, (source, index))
  std::vector<HeapElement> heap;

  for (int i = 0; i < nbp; ++i) {
    if (recv_counts[i] > 0) {
      heap.push_back({recv_buffer[recv_displs[i]], {i, 0}});
    }
  }
  std::make_heap(heap.begin(), heap.end(), std::greater<HeapElement>());

  int sorted_idx = 0;
  while (!heap.empty()) {
    std::pop_heap(heap.begin(), heap.end(), std::greater<HeapElement>());
    auto [val, source_info] = heap.back();
    heap.pop_back();

    sorted_local[sorted_idx++] = val;

    int src = source_info.first;
    int idx = source_info.second + 1;

    if (idx < recv_counts[src]) {
      heap.push_back({recv_buffer[recv_displs[src] + idx], {src, idx}});
      std::push_heap(heap.begin(), heap.end(), std::greater<HeapElement>());
    }
  }

  end_time = MPI_Wtime();
  time_merge = end_time - start_time;

  // ============================================================
  // Étape 7: Rassemblement final sur process 0 (Gatherv)
  // ============================================================
  start_time = MPI_Wtime();

  // Collecter les tailles de chaque processus
  int my_count = static_cast<int>(sorted_local.size());
  std::vector<int> gather_counts(nbp);
  MPI_Gather(&my_count, 1, MPI_INT, gather_counts.data(), 1, MPI_INT, 0,
             MPI_COMM_WORLD);

  std::vector<int> gather_displs(nbp);
  std::vector<double> final_sorted;

  if (rank == 0) {
    gather_displs[0] = 0;
    for (int i = 1; i < nbp; ++i) {
      gather_displs[i] = gather_displs[i - 1] + gather_counts[i - 1];
    }
    final_sorted.resize(n);
  }

  MPI_Gatherv(sorted_local.data(), my_count, MPI_DOUBLE, final_sorted.data(),
              gather_counts.data(), gather_displs.data(), MPI_DOUBLE, 0,
              MPI_COMM_WORLD);

  end_time = MPI_Wtime();
  time_gather = end_time - start_time;

  // ============================================================
  // Affichage des résultats
  // ============================================================

  // Collecter les temps maximaux
  double max_scatter, max_local_sort, max_sample, max_alltoall, max_merge,
      max_gather;
  MPI_Reduce(&time_scatter, &max_scatter, 1, MPI_DOUBLE, MPI_MAX, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&time_local_sort, &max_local_sort, 1, MPI_DOUBLE, MPI_MAX, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&time_sample, &max_sample, 1, MPI_DOUBLE, MPI_MAX, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&time_alltoall, &max_alltoall, 1, MPI_DOUBLE, MPI_MAX, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&time_merge, &max_merge, 1, MPI_DOUBLE, MPI_MAX, 0,
             MPI_COMM_WORLD);
  MPI_Reduce(&time_gather, &max_gather, 1, MPI_DOUBLE, MPI_MAX, 0,
             MPI_COMM_WORLD);

  if (rank == 0) {
    double total_parallel = max_scatter + max_local_sort + max_sample +
                            max_alltoall + max_merge + max_gather;

    std::cout << std::endl;
    std::cout << "=== Temps par étape ===" << std::endl;
    std::cout << "Scatter (distribution)   : " << std::fixed
              << std::setprecision(4) << max_scatter << " s" << std::endl;
    std::cout << "Tri local                : " << std::fixed
              << std::setprecision(4) << max_local_sort << " s" << std::endl;
    std::cout << "Échantillonnage          : " << std::fixed
              << std::setprecision(4) << max_sample << " s" << std::endl;
    std::cout << "All-to-All               : " << std::fixed
              << std::setprecision(4) << max_alltoall << " s" << std::endl;
    std::cout << "Tri fusion               : " << std::fixed
              << std::setprecision(4) << max_merge << " s" << std::endl;
    std::cout << "Gather (rassemblement)   : " << std::fixed
              << std::setprecision(4) << max_gather << " s" << std::endl;
    std::cout << std::endl;
    std::cout << "Temps total parallèle    : " << std::fixed
              << std::setprecision(4) << total_parallel << " s" << std::endl;

    // Vérification
    bool sorted = is_sorted(final_sorted);
    std::cout << std::endl;
    std::cout << "Vérification : "
              << (sorted ? "✓ Tableau trié correctement"
                         : "✗ ERREUR: Tableau non trié!")
              << std::endl;

    // Affichage de quelques valeurs
    std::cout << std::endl;
    std::cout << "Premiers éléments : ";
    for (size_t i = 0; i < std::min(n, size_t(5)); ++i) {
      std::cout << std::fixed << std::setprecision(4) << final_sorted[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Derniers éléments : ";
    size_t start_idx = n > 5 ? n - 5 : 0;
    for (size_t i = start_idx; i < n; ++i) {
      std::cout << std::fixed << std::setprecision(4) << final_sorted[i] << " ";
    }
    std::cout << std::endl;

    if (!sorted) {
      MPI_Finalize();
      return 1;
    }
  }

  // Affichage des statistiques par processus (debug)
  for (int p = 0; p < nbp; ++p) {
    MPI_Barrier(MPI_COMM_WORLD);
    if (rank == p) {
      std::cout << "Process " << rank << ": reçu " << total_recv
                << " éléments après redistribution" << std::endl;
    }
  }

  MPI_Finalize();
  return 0;
}
