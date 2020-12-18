#!/usr/bin/sh -e
echo "Building Fortran code"
gfortran -c cmd_line.f90
gfortran -c core.f90
gfortran -c utils.f90
gfortran -c main.f90
gfortran cmd_line.o core.o utils.o main.o
echo
echo "Building Python module"
python3 -m numpy.f2py -c -m core core.f90
