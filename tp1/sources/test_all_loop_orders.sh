#!/bin/bash
# =============================================================================
# TP1 - 自动测试所有循环顺序的脚本
# 用法: ./test_all_loop_orders.sh [matrix_size]
# 例如: ./test_all_loop_orders.sh 1024
# =============================================================================

set -e

# 默认矩阵大小
N=${1:-1024}
N2=${2:-2048}

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 所有循环顺序
ORDERS=("IJK" "IKJ" "JIK" "JKI" "KIJ" "KJI")

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  TP1 - Test de tous les ordres de boucles ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "Taille de matrice: n=$N et n=$N2"
echo ""

# 保存原始文件
cp ProdMatMat.cpp ProdMatMat.cpp.backup

# 创建结果文件
RESULTS_FILE="loop_order_results.csv"
echo "Ordre,Temps_n${N}(s),MFlops_n${N},Temps_n${N2}(s),MFlops_n${N2}" > $RESULTS_FILE

echo -e "${YELLOW}Compilation des fichiers objets...${NC}"
g++ -std=c++14 -O2 -march=native -Wall -c Matrix.cpp -o Matrix.o
g++ -std=c++14 -O2 -march=native -Wall -c TestProductMatrix.cpp -o TestProductMatrix.o

for ORDER in "${ORDERS[@]}"; do
    echo ""
    echo -e "${CYAN}=== Test de l'ordre: $ORDER ===${NC}"
    
    # 修改 ProdMatMat.cpp 中的 #define
    # 先注释掉所有的 #define LOOP_ORDER_*
    sed -i 's/^#define LOOP_ORDER_/\/\/ #define LOOP_ORDER_/' ProdMatMat.cpp
    # 然后激活当前测试的顺序
    sed -i "s/^\/\/ #define LOOP_ORDER_${ORDER}/#define LOOP_ORDER_${ORDER}/" ProdMatMat.cpp
    
    # 编译 ProdMatMat.cpp
    g++ -std=c++14 -O2 -march=native -Wall -c ProdMatMat.cpp -o ProdMatMat.o
    
    # 链接
    g++ -std=c++14 -O2 -march=native -Wall TestProductMatrix.o Matrix.o ProdMatMat.o -o TestProductMatrix.exe -lpthread
    
    # 运行测试 n=N
    echo "  Test n=$N..."
    OUTPUT1=$(./TestProductMatrix.exe $N 2>&1)
    TIME1=$(echo "$OUTPUT1" | grep "Temps CPU" | awk '{print $7}')
    MFLOPS1=$(echo "$OUTPUT1" | grep "MFlops" | awk '{print $NF}')
    echo "    Temps: ${TIME1}s, MFlops: $MFLOPS1"
    
    # 运行测试 n=N2
    echo "  Test n=$N2..."
    OUTPUT2=$(./TestProductMatrix.exe $N2 2>&1)
    TIME2=$(echo "$OUTPUT2" | grep "Temps CPU" | awk '{print $7}')
    MFLOPS2=$(echo "$OUTPUT2" | grep "MFlops" | awk '{print $NF}')
    echo "    Temps: ${TIME2}s, MFlops: $MFLOPS2"
    
    # 转换顺序名称为小写 i,j,k 格式
    ORDER_LOWER=$(echo "$ORDER" | sed 's/I/i,/g; s/J/j,/g; s/K/k/g')
    
    # 保存结果
    echo "$ORDER_LOWER,$TIME1,$MFLOPS1,$TIME2,$MFLOPS2" >> $RESULTS_FILE
done

# 恢复原始文件
mv ProdMatMat.cpp.backup ProdMatMat.cpp

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Résultats sauvegardés dans: $RESULTS_FILE ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Résultats:"
echo ""
column -t -s',' $RESULTS_FILE
echo ""
