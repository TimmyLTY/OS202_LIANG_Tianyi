#!/bin/bash
# =============================================================================
# TP1 - Expérience 2.6 : Comparaison avec BLAS
# Compare notre implémentation avec OpenBLAS
# Usage: ./test_blas.sh
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Expérience 2.6 : Comparaison avec BLAS   ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# 检查 OpenBLAS 是否安装
if ! ldconfig -p 2>/dev/null | grep -q openblas; then
    if ! [ -f /usr/lib/aarch64-linux-gnu/libopenblas.so ] && ! [ -f /usr/lib/libopenblas.so ]; then
        echo -e "${RED}OpenBLAS non trouvé. Installation requise:${NC}"
        echo "sudo apt install libopenblas-dev"
        exit 1
    fi
fi

echo -e "${YELLOW}Compilation du test BLAS...${NC}"

# 编译 Matrix.o
g++ -std=c++14 -O2 -march=native -Wall -c Matrix.cpp -o Matrix.o

# 创建优化版本的 ProdMatMat.cpp (用于对比)
cat > ProdMatMat_opt.cpp << 'CPPEOF'
#include <algorithm>
#include "ProdMatMat.hpp"

namespace {
void prodSubBlocks(int iRowBlkA, int iColBlkB, int iColBlkA, int szBlock,
                   const Matrix& A, const Matrix& B, Matrix& C) {
  int iMax = std::min(A.nbRows, iRowBlkA + szBlock);
  int jMax = std::min(B.nbCols, iColBlkB + szBlock);
  int kMax = std::min(A.nbCols, iColBlkA + szBlock);
  // Ordre j,k,i optimal
  for (int j = iColBlkB; j < jMax; ++j)
    for (int k = iColBlkA; k < kMax; ++k)
      for (int i = iRowBlkA; i < iMax; ++i)
        C(i, j) += A(i, k) * B(k, j);
}
const int szBlock = 512;
}

Matrix operator*(const Matrix& A, const Matrix& B) {
  Matrix C(A.nbRows, B.nbCols, 0.0);
  prodSubBlocks(0, 0, 0, std::max({A.nbRows, B.nbCols, A.nbCols}), A, B, C);
  return C;
}
CPPEOF

# 编译我们的优化版本
g++ -std=c++14 -O2 -march=native -Wall -c ProdMatMat_opt.cpp -o ProdMatMat_opt.o
g++ -std=c++14 -O2 -march=native -Wall -c TestProductMatrix.cpp -o TestProductMatrix.o
g++ -std=c++14 -O2 -march=native -Wall TestProductMatrix.o Matrix.o ProdMatMat_opt.o -o TestProductMatrix_opt.exe

# 编译 BLAS 版本
g++ -std=c++14 -O2 -march=native -Wall -c test_product_matrice_blas.cpp -o test_product_matrice_blas.o
g++ -std=c++14 -O2 -march=native -Wall test_product_matrice_blas.o Matrix.o ProdMatMat_opt.o -o test_product_matrice_blas.exe -lopenblas

echo -e "${GREEN}Compilation réussie!${NC}"
echo ""

# 结果文件
RESULTS_FILE="results_blas.csv"
echo "n,Notre_MFlops,BLAS_MFlops,Ratio" > $RESULTS_FILE

echo -e "${CYAN}Test en cours...${NC}"
echo ""
printf "%-8s | %-18s | %-18s | %-10s\n" "n" "Notre impl (MFlops)" "BLAS (MFlops)" "Ratio"
echo "---------|--------------------|--------------------|----------"

# 测试不同大小
for n in 512 1024 2048 4096; do
    # 我们的实现
    OUR_RESULT=$(./TestProductMatrix_opt.exe $n 2>&1 | grep "MFlops" | awk '{print $NF}')
    
    # BLAS 实现
    BLAS_RESULT=$(./test_product_matrice_blas.exe $n 2>&1 | grep "MFlops" | awk '{print $NF}')
    
    # 计算比率 (使用 awk 代替 bc)
    if [ -n "$OUR_RESULT" ] && [ -n "$BLAS_RESULT" ]; then
        RATIO=$(awk "BEGIN {printf \"%.2f\", $BLAS_RESULT / $OUR_RESULT}")
    else
        RATIO="N/A"
    fi
    
    printf "%-8s | %-18s | %-18s | %-10s\n" "$n" "$OUR_RESULT" "$BLAS_RESULT" "${RATIO}x"
    echo "$n,$OUR_RESULT,$BLAS_RESULT,$RATIO" >> $RESULTS_FILE
done

echo ""
echo -e "${GREEN}Résultats sauvegardés dans: $RESULTS_FILE${NC}"

# 清理临时文件
rm -f ProdMatMat_opt.cpp ProdMatMat_opt.o TestProductMatrix_opt.exe

echo ""
echo -e "${CYAN}======================================${NC}"
echo -e "${CYAN}  Analyse des résultats BLAS         ${NC}"
echo -e "${CYAN}======================================${NC}"
echo ""
echo "OpenBLAS utilise des optimisations avancées :"
echo "  - Instructions SIMD (NEON sur ARM)"
echo "  - Prefetching optimisé"
echo "  - Blocking multi-niveaux"
echo "  - Assembleur optimisé pour chaque architecture"
echo ""
echo -e "${GREEN}Expérience terminée!${NC}"
