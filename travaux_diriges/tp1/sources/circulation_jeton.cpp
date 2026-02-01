/**
 * TP1 - Section 2.1 : Circulation d'un jeton dans un anneau
 * 
 * Le processus 0 initialise un jeton à 1, puis chaque processus
 * incrémente le jeton et le passe au suivant. Le dernier processus
 * renvoie au processus 0 qui affiche la valeur finale.
 * 
 * Compilation : mpic++ -O2 -o circulation_jeton.exe circulation_jeton.cpp
 * Exécution   : mpirun -np 4 ./circulation_jeton.exe
 */

#include <iostream>
#include <mpi.h>

int main(int argc, char* argv[])
{
    MPI_Init(&argc, &argv);
    
    int rank, nbp;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &nbp);
    
    int jeton;
    
    if (rank == 0) {
        // Processus 0 : initialise le jeton à 1
        jeton = 1;
        std::cout << "Processus " << rank << " : jeton initial = " << jeton << std::endl;
        
        // Envoie au processus 1
        MPI_Send(&jeton, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
        
        // Attend la réception du jeton du dernier processus
        MPI_Recv(&jeton, 1, MPI_INT, nbp - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        std::cout << "Processus " << rank << " : jeton final reçu = " << jeton 
                  << " (attendu : " << nbp << ")" << std::endl;
    }
    else {
        // Autres processus : reçoivent, incrémentent, envoient
        MPI_Recv(&jeton, 1, MPI_INT, rank - 1, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
        std::cout << "Processus " << rank << " : jeton reçu = " << jeton;
        
        jeton++;  // Incrémente le jeton
        std::cout << ", après incrément = " << jeton << std::endl;
        
        // Envoie au processus suivant (ou au processus 0 si c'est le dernier)
        int next = (rank + 1) % nbp;
        MPI_Send(&jeton, 1, MPI_INT, next, 0, MPI_COMM_WORLD);
    }
    
    MPI_Finalize();
    return 0;
}
