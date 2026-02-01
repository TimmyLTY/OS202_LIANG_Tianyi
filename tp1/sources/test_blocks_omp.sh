#!/bin/bash
# =============================================================================
# TP1 - Expérience 2.5 : Combinaison Bloc + OpenMP
# Teste la combinaison de blocking et parallélisation
# Usage: ./test_blocks_omp.sh
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Expérience 2.5 : Bloc + OpenMP           ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# 备份原文件
cp ProdMatMat.cpp ProdMatMat.cpp.backup

# 设置为最优循环顺序 JKI，并确保 #pragma omp 在正确位置
cat > ProdMatMat_temp.cpp << 'CPPEOF'
#include <algorithm>
#include <cassert>
#include <iostream>
#include <thread>
#if defined(_OPENMP)
#include <omp.h>
#endif
#include "ProdMatMat.hpp"

namespace {
void prodSubBlocks(int iRowBlkA, int iColBlkB, int iColBlkA, int szBlock,
                   const Matrix& A, const Matrix& B, Matrix& C) {
  int iMax = std::min(A.nbRows, iRowBlkA + szBlock);
  int jMax = std::min(B.nbCols, iColBlkB + szBlock);
  int kMax = std::min(A.nbCols, iColBlkA + szBlock);

  // Ordre j,k,i avec OpenMP sur la boucle externe
  #pragma omp parallel for
  for (int j = iColBlkB; j < jMax; ++j)
    for (int k = iColBlkA; k < kMax; ++k)
      for (int i = iRowBlkA; i < iMax; ++i)
        C(i, j) += A(i, k) * B(k, j);
}

const int szBlock = SZBLOCK_VALUE;
}  // namespace

Matrix operator*(const Matrix& A, const Matrix& B) {
  Matrix C(A.nbRows, B.nbCols, 0.0);
  prodSubBlocks(0, 0, 0, std::max({A.nbRows, B.nbCols, A.nbCols}), A, B, C);
  return C;
}
CPPEOF

# 编译 Matrix.o 和 TestProductMatrix.o 带 OpenMP
echo -e "${YELLOW}Compilation avec OpenMP...${NC}"
g++ -std=c++14 -O2 -march=native -Wall -fopenmp -c Matrix.cpp -o Matrix.o
g++ -std=c++14 -O2 -march=native -Wall -fopenmp -c TestProductMatrix.cpp -o TestProductMatrix.o

# 结果文件
RESULTS_FILE="results_blocks_omp.csv"
echo "szBlock,OMP_NUM,MFlops_512,MFlops_1024,MFlops_2048" > $RESULTS_FILE

echo -e "${CYAN}Test en cours...${NC}"
echo ""
printf "%-8s | %-7s | %-12s | %-12s | %-12s\n" "szBlock" "OMP_NUM" "MFlops(512)" "MFlops(1024)" "MFlops(2048)"
echo "---------|---------|--------------|--------------|-------------"

# 测试组合
for szBlock in 64 128 256 512 1024; do
    # 用 sed 替换 szBlock 值
    sed "s/SZBLOCK_VALUE/$szBlock/" ProdMatMat_temp.cpp > ProdMatMat.cpp
    
    # 重新编译（带 OpenMP）
    g++ -std=c++14 -O2 -march=native -Wall -fopenmp -c ProdMatMat.cpp -o ProdMatMat.o
    g++ -std=c++14 -O2 -march=native -Wall -fopenmp TestProductMatrix.o Matrix.o ProdMatMat.o -o TestProductMatrix.exe -lpthread
    
    for threads in 1 4 8; do
        M512=$(OMP_NUM_THREADS=$threads ./TestProductMatrix.exe 512 2>&1 | grep "MFlops" | awk '{print $NF}')
        M1024=$(OMP_NUM_THREADS=$threads ./TestProductMatrix.exe 1024 2>&1 | grep "MFlops" | awk '{print $NF}')
        M2048=$(OMP_NUM_THREADS=$threads ./TestProductMatrix.exe 2048 2>&1 | grep "MFlops" | awk '{print $NF}')
        
        printf "%-8s | %-7s | %-12s | %-12s | %-12s\n" "$szBlock" "$threads" "$M512" "$M1024" "$M2048"
        echo "$szBlock,$threads,$M512,$M1024,$M2048" >> $RESULTS_FILE
    done
    echo "---------|---------|--------------|--------------|-------------"
done

# 清理临时文件并恢复原文件
rm -f ProdMatMat_temp.cpp
mv ProdMatMat.cpp.backup ProdMatMat.cpp

# 重新编译默认版本
g++ -std=c++14 -O2 -march=native -Wall -c ProdMatMat.cpp -o ProdMatMat.o
g++ -std=c++14 -O2 -march=native -Wall TestProductMatrix.o Matrix.o ProdMatMat.o -o TestProductMatrix.exe -lpthread

echo ""
echo -e "${GREEN}Résultats sauvegardés dans: $RESULTS_FILE${NC}"
echo ""

# 找出最优组合
echo -e "${CYAN}Meilleure combinaison pour n=1024:${NC}"
sort -t',' -k4 -nr $RESULTS_FILE | head -2 | tail -1

echo ""
echo -e "${GREEN}Expérience terminée!${NC}"
