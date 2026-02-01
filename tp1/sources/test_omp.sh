#!/bin/bash
# =============================================================================
# TP1 - Expérience 2.3 : Test OpenMP avec différents nombres de threads
# Utilise l'ordre de boucles optimal (j,k,i)
# Usage: ./test_omp.sh
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Expérience 2.3 : Parallélisation OpenMP  ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# 确保使用最优循环顺序 j,k,i
echo -e "${YELLOW}Configuration de l'ordre optimal (j,k,i)...${NC}"

# 备份原文件
cp ProdMatMat.cpp ProdMatMat.cpp.backup

# 设置为 JKI 顺序
sed -i 's/^#define LOOP_ORDER_/\/\/ #define LOOP_ORDER_/' ProdMatMat.cpp
sed -i 's/^\/\/ #define LOOP_ORDER_JKI/#define LOOP_ORDER_JKI/' ProdMatMat.cpp

# 添加 OpenMP 并行化到最优循环
# 检查是否已经有 #pragma omp
if ! grep -q "#pragma omp" ProdMatMat.cpp; then
    echo -e "${YELLOW}Ajout de la directive OpenMP...${NC}"
    # 在 JKI 循环前添加 OpenMP pragma
    sed -i 's/for (int j = iColBlkB; j < jMax; ++j)/#pragma omp parallel for\n  for (int j = iColBlkB; j < jMax; ++j)/' ProdMatMat.cpp
fi

# 编译带 OpenMP 支持
echo -e "${YELLOW}Compilation avec OpenMP...${NC}"
g++ -std=c++14 -O2 -march=native -Wall -fopenmp -c Matrix.cpp -o Matrix.o
g++ -std=c++14 -O2 -march=native -Wall -fopenmp -c ProdMatMat.cpp -o ProdMatMat.o
g++ -std=c++14 -O2 -march=native -Wall -fopenmp -c TestProductMatrix.cpp -o TestProductMatrix.o
g++ -std=c++14 -O2 -march=native -Wall -fopenmp TestProductMatrix.o Matrix.o ProdMatMat.o -o TestProductMatrix.exe -lpthread

echo -e "${GREEN}Compilation réussie!${NC}"
echo ""

# 结果文件
RESULTS_FILE="results_omp.csv"
echo "OMP_NUM_THREADS,MFlops_512,MFlops_1024,MFlops_2048" > $RESULTS_FILE

echo -e "${CYAN}Test en cours...${NC}"
echo ""
printf "%-15s | %-12s | %-12s | %-12s\n" "OMP_NUM_THREADS" "MFlops(512)" "MFlops(1024)" "MFlops(2048)"
echo "----------------|--------------|--------------|-------------"

for threads in 1 2 3 4 5 6 7 8; do
    M512=$(OMP_NUM_THREADS=$threads ./TestProductMatrix.exe 512 2>&1 | grep "MFlops" | awk '{print $NF}')
    M1024=$(OMP_NUM_THREADS=$threads ./TestProductMatrix.exe 1024 2>&1 | grep "MFlops" | awk '{print $NF}')
    M2048=$(OMP_NUM_THREADS=$threads ./TestProductMatrix.exe 2048 2>&1 | grep "MFlops" | awk '{print $NF}')
    
    printf "%-15s | %-12s | %-12s | %-12s\n" "$threads" "$M512" "$M1024" "$M2048"
    echo "$threads,$M512,$M1024,$M2048" >> $RESULTS_FILE
done

echo ""
echo -e "${GREEN}Résultats sauvegardés dans: $RESULTS_FILE${NC}"

# 计算 Speedup
echo ""
echo -e "${CYAN}Calcul du Speedup:${NC}"
echo ""

# 读取基准值 (1 thread)
BASE_512=$(head -2 $RESULTS_FILE | tail -1 | cut -d',' -f2)
BASE_1024=$(head -2 $RESULTS_FILE | tail -1 | cut -d',' -f3)
BASE_2048=$(head -2 $RESULTS_FILE | tail -1 | cut -d',' -f4)

printf "%-15s | %-12s | %-12s | %-12s\n" "OMP_NUM_THREADS" "Speedup(512)" "Speedup(1024)" "Speedup(2048)"
echo "----------------|--------------|--------------|-------------"

tail -n +2 $RESULTS_FILE | while IFS=',' read -r threads m512 m1024 m2048; do
    s512=$(echo "scale=2; $m512 / $BASE_512" | bc)
    s1024=$(echo "scale=2; $m1024 / $BASE_1024" | bc)
    s2048=$(echo "scale=2; $m2048 / $BASE_2048" | bc)
    printf "%-15s | %-12s | %-12s | %-12s\n" "$threads" "$s512" "$s1024" "$s2048"
done

# 恢复原文件
mv ProdMatMat.cpp.backup ProdMatMat.cpp

echo ""
echo -e "${GREEN}Expérience terminée!${NC}"
