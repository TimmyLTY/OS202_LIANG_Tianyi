#!/bin/bash
# =============================================================================
# TP1 - Expérience 2.4 : Test du produit par blocs (SANS OpenMP)
# Teste différentes tailles de blocs avec l'ordre optimal (j,k,i)
# Usage: ./test_blocks.sh
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Expérience 2.4 : Produit par blocs       ${NC}"
echo -e "${GREEN}  (Test séquentiel - sans OpenMP)          ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# 创建一个临时的 ProdMatMat.cpp 不带 OpenMP pragma
cat > ProdMatMat_blocks_test.cpp << 'CPPEOF'
#include <algorithm>
#include <cassert>
#include <iostream>
#include <thread>
#include "ProdMatMat.hpp"

namespace {
void prodSubBlocks(int iRowBlkA, int iColBlkB, int iColBlkA, int szBlock,
                   const Matrix& A, const Matrix& B, Matrix& C) {
  int iMax = std::min(A.nbRows, iRowBlkA + szBlock);
  int jMax = std::min(B.nbCols, iColBlkB + szBlock);
  int kMax = std::min(A.nbCols, iColBlkA + szBlock);

  // Ordre j,k,i (optimal pour column-major) - SANS OpenMP
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

# 编译 Matrix.o 和 TestProductMatrix.o
echo -e "${YELLOW}Compilation...${NC}"
g++ -std=c++14 -O2 -march=native -Wall -c Matrix.cpp -o Matrix.o
g++ -std=c++14 -O2 -march=native -Wall -c TestProductMatrix.cpp -o TestProductMatrix.o

# 结果文件
RESULTS_FILE="results_blocks.csv"
echo "szBlock,MFlops_512,MFlops_1024,MFlops_2048" > $RESULTS_FILE

echo -e "${CYAN}Test en cours...${NC}"
echo ""
printf "%-10s | %-12s | %-12s | %-12s\n" "szBlock" "MFlops(512)" "MFlops(1024)" "MFlops(2048)"
echo "-----------|--------------|--------------|-------------"

# 测试不同的块大小
for szBlock in 32 64 128 256 512 1024 2048; do
    # 用 sed 替换 szBlock 值
    sed "s/SZBLOCK_VALUE/$szBlock/" ProdMatMat_blocks_test.cpp > ProdMatMat.cpp
    
    # 重新编译（不带 OpenMP）
    g++ -std=c++14 -O2 -march=native -Wall -c ProdMatMat.cpp -o ProdMatMat.o
    g++ -std=c++14 -O2 -march=native -Wall TestProductMatrix.o Matrix.o ProdMatMat.o -o TestProductMatrix.exe -lpthread
    
    # 测试
    M512=$(./TestProductMatrix.exe 512 2>&1 | grep "MFlops" | awk '{print $NF}')
    M1024=$(./TestProductMatrix.exe 1024 2>&1 | grep "MFlops" | awk '{print $NF}')
    M2048=$(./TestProductMatrix.exe 2048 2>&1 | grep "MFlops" | awk '{print $NF}')
    
    printf "%-10s | %-12s | %-12s | %-12s\n" "$szBlock" "$M512" "$M1024" "$M2048"
    echo "$szBlock,$M512,$M1024,$M2048" >> $RESULTS_FILE
done

# 清理临时文件
rm -f ProdMatMat_blocks_test.cpp

echo ""
echo -e "${GREEN}Résultats sauvegardés dans: $RESULTS_FILE${NC}"
echo ""

# 找出最优块大小
echo -e "${CYAN}Analyse:${NC}"
echo "Meilleur szBlock pour n=1024:"
sort -t',' -k3 -nr $RESULTS_FILE | head -2 | tail -1

echo ""
echo -e "${GREEN}Expérience terminée!${NC}"
