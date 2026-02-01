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

const int szBlock = 2048;
}  // namespace

Matrix operator*(const Matrix& A, const Matrix& B) {
  Matrix C(A.nbRows, B.nbCols, 0.0);
  prodSubBlocks(0, 0, 0, std::max({A.nbRows, B.nbCols, A.nbCols}), A, B, C);
  return C;
}
