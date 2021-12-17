all:
	echo "Building Fortran code"
	# I'm using gfortran here explicitly instead of $(FC), since the default value is "f77" and this project uses Fortran 95/2003
	gfortran -c core.f90
	gfortran -c cmd_line.f90
	gfortran -c utils.f90
	gfortran -c main.f90
	gfortran cmd_line.o core.o utils.o main.o -o planetary-motion
	echo
	echo "Building Python module"
	python3 -m numpy.f2py -c -m core core.f90
clean:
	echo "Cleaning temporary files from the project."
	rm -f ./planetary-motion ./*.c ./*.f ./*.log ./*.mod ./*.o ./*.out ./*.so
