#!/bin/bash
# TP1 自动化测试脚本
# 在 OrbStack Ubuntu 环境下运行

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}     TP1 矩阵乘法性能测试脚本          ${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查是否在正确目录
if [ ! -f "Makefile" ]; then
    echo -e "${RED}错误：请在 tp1/sources 目录下运行此脚本${NC}"
    exit 1
fi

# 创建结果目录
RESULTS_DIR="../results"
mkdir -p $RESULTS_DIR

echo ""
echo -e "${YELLOW}=== 步骤 1: 系统信息 ===${NC}"
echo "记录 CPU 信息..."
lscpu > $RESULTS_DIR/lscpu_info.txt
lscpu | grep -E "Model name|CPU\(s\)|Thread|Core|cache" || true
echo "CPU 信息已保存到 $RESULTS_DIR/lscpu_info.txt"

echo ""
echo -e "${YELLOW}=== 步骤 2: 安装依赖 ===${NC}"
echo "检查并安装编译依赖..."
sudo apt-get update -qq
sudo apt-get install -y -qq build-essential libomp-dev libblas-dev > /dev/null 2>&1 || true
echo "依赖安装完成"

echo ""
echo -e "${YELLOW}=== 步骤 3: 编译项目 ===${NC}"
make clean > /dev/null 2>&1 || true
echo "编译 TestProductMatrix.exe..."
make TestProductMatrix.exe
echo "编译完成"

echo ""
echo -e "${YELLOW}=== 步骤 4: 测试不同矩阵大小 ===${NC}"
echo "测试矩阵大小对性能的影响..."
echo "n,MFlops,time" > $RESULTS_DIR/size_test.csv
for n in 256 512 1024 2048; do
    echo "  测试 n=$n ..."
    result=$(./TestProductMatrix.exe $n 2>&1)
    mflops=$(echo "$result" | grep "MFlops" | awk '{print $NF}')
    time_s=$(echo "$result" | grep "Temps CPU" | awk '{print $7}')
    echo "$n,$mflops,$time_s" >> $RESULTS_DIR/size_test.csv
    echo "    n=$n: MFlops=$mflops, time=${time_s}s"
done
echo "结果已保存到 $RESULTS_DIR/size_test.csv"

echo ""
echo -e "${YELLOW}=== 步骤 5: OpenMP 线程数测试 ===${NC}"
echo "测试不同线程数对性能的影响..."
echo "threads,n512,n1024,n2048" > $RESULTS_DIR/omp_test.csv
for threads in 1 2 4 8; do
    echo "  测试 OMP_NUM_THREADS=$threads ..."
    row="$threads"
    for n in 512 1024 2048; do
        mflops=$(OMP_NUM_THREADS=$threads ./TestProductMatrix.exe $n 2>&1 | grep "MFlops" | awk '{print $NF}')
        row="$row,$mflops"
    done
    echo "$row" >> $RESULTS_DIR/omp_test.csv
    echo "    threads=$threads: $row"
done
echo "结果已保存到 $RESULTS_DIR/omp_test.csv"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}     所有基础测试完成！                ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "结果文件位于: $RESULTS_DIR/"
ls -la $RESULTS_DIR/
echo ""
echo -e "${YELLOW}后续步骤:${NC}"
echo "1. 修改 ProdMatMat.cpp 中的循环顺序进行测试"
echo "2. 修改 szBlock 值进行分块测试"
echo "3. 查看 $RESULTS_DIR/ 目录下的 CSV 文件获取结果"
