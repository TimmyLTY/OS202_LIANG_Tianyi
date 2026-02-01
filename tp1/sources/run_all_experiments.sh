#!/bin/bash
# =============================================================================
# TP1 - 完整实验自动化脚本
# 运行所有实验并生成结果
# 用法: ./run_all_experiments.sh
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

RESULTS_DIR="./results"
mkdir -p $RESULTS_DIR

echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}     TP1 - Expériences complètes de multiplication matricielle ${NC}"
echo -e "${GREEN}================================================================${NC}"

# =============================================================================
# 1. 系统信息
# =============================================================================
echo ""
echo -e "${YELLOW}[1/6] Collecte des informations système...${NC}"
lscpu > $RESULTS_DIR/system_info.txt
echo "Informations CPU sauvegardées dans $RESULTS_DIR/system_info.txt"
lscpu | grep -E "Model name|CPU\(s\)|Thread|Core|cache" || true

# =============================================================================
# 2. 编译
# =============================================================================
echo ""
echo -e "${YELLOW}[2/6] Compilation du projet...${NC}"
make clean 2>/dev/null || true
g++ -std=c++14 -O2 -march=native -Wall -c Matrix.cpp -o Matrix.o
g++ -std=c++14 -O2 -march=native -Wall -c ProdMatMat.cpp -o ProdMatMat.o
g++ -std=c++14 -O2 -march=native -Wall -c TestProductMatrix.cpp -o TestProductMatrix.o
g++ -std=c++14 -O2 -march=native -Wall TestProductMatrix.o Matrix.o ProdMatMat.o -o TestProductMatrix.exe -lpthread
echo -e "${GREEN}Compilation réussie!${NC}"

# =============================================================================
# 3. 测试不同矩阵大小
# =============================================================================
echo ""
echo -e "${YELLOW}[3/6] Test de l'effet de la taille de matrice...${NC}"
echo "n,Temps(s),MFlops" > $RESULTS_DIR/size_effect.csv

for n in 256 512 1024 2048; do
    echo -n "  n=$n: "
    OUTPUT=$(./TestProductMatrix.exe $n 2>&1)
    TIME=$(echo "$OUTPUT" | grep "Temps CPU" | awk '{print $7}')
    MFLOPS=$(echo "$OUTPUT" | grep "MFlops" | awk '{print $NF}')
    echo "Temps=${TIME}s, MFlops=$MFLOPS"
    echo "$n,$TIME,$MFLOPS" >> $RESULTS_DIR/size_effect.csv
done
echo "Résultats: $RESULTS_DIR/size_effect.csv"

# =============================================================================
# 4. 测试循环顺序
# =============================================================================
echo ""
echo -e "${YELLOW}[4/6] Test des ordres de boucles...${NC}"
echo "Ordre,Temps_1024(s),MFlops_1024,Temps_2048(s),MFlops_2048" > $RESULTS_DIR/loop_orders.csv

ORDERS=("IJK" "IKJ" "JIK" "JKI" "KIJ" "KJI")
cp ProdMatMat.cpp ProdMatMat.cpp.backup

for ORDER in "${ORDERS[@]}"; do
    echo -n "  Ordre $ORDER: "
    
    # 修改 #define
    sed -i 's/^#define LOOP_ORDER_/\/\/ #define LOOP_ORDER_/' ProdMatMat.cpp
    sed -i "s/^\/\/ #define LOOP_ORDER_${ORDER}/#define LOOP_ORDER_${ORDER}/" ProdMatMat.cpp
    
    # 重新编译 ProdMatMat.cpp
    g++ -std=c++14 -O2 -march=native -Wall -c ProdMatMat.cpp -o ProdMatMat.o
    g++ -std=c++14 -O2 -march=native -Wall TestProductMatrix.o Matrix.o ProdMatMat.o -o TestProductMatrix.exe -lpthread
    
    # 测试 n=1024
    OUTPUT1=$(./TestProductMatrix.exe 1024 2>&1)
    TIME1=$(echo "$OUTPUT1" | grep "Temps CPU" | awk '{print $7}')
    MFLOPS1=$(echo "$OUTPUT1" | grep "MFlops" | awk '{print $NF}')
    
    # 测试 n=2048
    OUTPUT2=$(./TestProductMatrix.exe 2048 2>&1)
    TIME2=$(echo "$OUTPUT2" | grep "Temps CPU" | awk '{print $7}')
    MFLOPS2=$(echo "$OUTPUT2" | grep "MFlops" | awk '{print $NF}')
    
    ORDER_LOWER=$(echo "$ORDER" | sed 's/./&,/g' | sed 's/,$//' | tr 'A-Z' 'a-z')
    echo "n=1024: ${MFLOPS1} MFlops, n=2048: ${MFLOPS2} MFlops"
    echo "$ORDER_LOWER,$TIME1,$MFLOPS1,$TIME2,$MFLOPS2" >> $RESULTS_DIR/loop_orders.csv
done

mv ProdMatMat.cpp.backup ProdMatMat.cpp
# 重新编译回默认版本
g++ -std=c++14 -O2 -march=native -Wall -c ProdMatMat.cpp -o ProdMatMat.o
g++ -std=c++14 -O2 -march=native -Wall TestProductMatrix.o Matrix.o ProdMatMat.o -o TestProductMatrix.exe -lpthread

echo "Résultats: $RESULTS_DIR/loop_orders.csv"

# =============================================================================
# 5. 测试 OpenMP
# =============================================================================
echo ""
echo -e "${YELLOW}[5/6] Test OpenMP (parallélisation)...${NC}"
echo "Threads,MFlops_512,MFlops_1024,MFlops_2048" > $RESULTS_DIR/omp_results.csv

# 检查是否支持 OpenMP，重新编译带 -fopenmp
g++ -std=c++14 -O2 -march=native -Wall -fopenmp -c ProdMatMat.cpp -o ProdMatMat.o 2>/dev/null || true
g++ -std=c++14 -O2 -march=native -Wall -fopenmp TestProductMatrix.o Matrix.o ProdMatMat.o -o TestProductMatrix.exe -lpthread -fopenmp 2>/dev/null || {
    echo -e "${RED}OpenMP non disponible, saut de ce test${NC}"
}

for threads in 1 2 4 8; do
    echo -n "  OMP_NUM_THREADS=$threads: "
    
    M512=$(OMP_NUM_THREADS=$threads ./TestProductMatrix.exe 512 2>&1 | grep "MFlops" | awk '{print $NF}')
    M1024=$(OMP_NUM_THREADS=$threads ./TestProductMatrix.exe 1024 2>&1 | grep "MFlops" | awk '{print $NF}')
    M2048=$(OMP_NUM_THREADS=$threads ./TestProductMatrix.exe 2048 2>&1 | grep "MFlops" | awk '{print $NF}')
    
    echo "512: $M512, 1024: $M1024, 2048: $M2048 MFlops"
    echo "$threads,$M512,$M1024,$M2048" >> $RESULTS_DIR/omp_results.csv
done
echo "Résultats: $RESULTS_DIR/omp_results.csv"

# =============================================================================
# 6. 生成汇总报告
# =============================================================================
echo ""
echo -e "${YELLOW}[6/6] Génération du rapport...${NC}"

cat > $RESULTS_DIR/SUMMARY.md << 'EOF'
# TP1 - Résumé des résultats

## Effet de la taille de matrice
EOF
echo '```' >> $RESULTS_DIR/SUMMARY.md
column -t -s',' $RESULTS_DIR/size_effect.csv >> $RESULTS_DIR/SUMMARY.md
echo '```' >> $RESULTS_DIR/SUMMARY.md

cat >> $RESULTS_DIR/SUMMARY.md << 'EOF'

## Ordre des boucles
EOF
echo '```' >> $RESULTS_DIR/SUMMARY.md
column -t -s',' $RESULTS_DIR/loop_orders.csv >> $RESULTS_DIR/SUMMARY.md
echo '```' >> $RESULTS_DIR/SUMMARY.md

cat >> $RESULTS_DIR/SUMMARY.md << 'EOF'

## Parallélisation OpenMP
EOF
echo '```' >> $RESULTS_DIR/SUMMARY.md
column -t -s',' $RESULTS_DIR/omp_results.csv >> $RESULTS_DIR/SUMMARY.md
echo '```' >> $RESULTS_DIR/SUMMARY.md

echo ""
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}     Toutes les expériences sont terminées!                    ${NC}"
echo -e "${GREEN}================================================================${NC}"
echo ""
echo "Fichiers de résultats:"
ls -la $RESULTS_DIR/
echo ""
echo -e "${CYAN}Voir le résumé: cat $RESULTS_DIR/SUMMARY.md${NC}"
