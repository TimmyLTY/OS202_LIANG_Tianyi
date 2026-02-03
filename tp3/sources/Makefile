include Make_linux.inc

ALL = bucket_sort_seq.exe bucket_sort_mpi.exe

default: help

all: $(ALL)

clean:
	@rm -fr *.o *.exe *~

bucket_sort_seq.exe: bucket_sort_seq.cpp
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LIB)

bucket_sort_mpi.exe: bucket_sort_mpi.cpp
	$(MPICXX) $(CXXFLAGS) $^ -o $@ $(LIB)

help:
	@echo "Available targets:"
	@echo "    all            : compile all executables"
	@echo "    clean          : remove compiled files"
	@echo ""
	@echo "Configuration:"
	@echo "    CXX      : $(CXX)"
	@echo "    MPICXX   : $(MPICXX)"
	@echo "    CXXFLAGS : $(CXXFLAGS)"
