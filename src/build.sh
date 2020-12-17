#!/usr/bin/env sh
echo "Building Fortran code separately"
gfortran core.f90
echo
echo "Building Python module"
python3 -m numpy.f2py -c -m core core.f90
