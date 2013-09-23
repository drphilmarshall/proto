#Directory of your CFITSIO library
CFITSIO_DIR = /usr/include/libcfitsio0
GSL_DIR = /usr/local2/misc/gsl-0/gsl-1.8/gsl
CBLAS_DIR = /usr/local2/misc/gsl-0/gsl-1.8/cblas/
#Compiler flags for gcc
CFLAGS = -I$(CFITSIO_DIR) -I$(GSL_DIR) -I$(CBLAS_DIR) -c -Wall  -ggdb -std=c99 
#Link flags for gcc
#LINK_FLAGS = -L$(CFITSIO_DIR) -L$(GSL_DIR) -L$(CBLAS_DIR)  -lcfitsio -lgsl -lgslcblas -lm 
LINK_FLAGS = -L$(CFITSIO_DIR) -L$(GSL_DIR) -L$(CBLAS_DIR)  -lcfitsio -lm 
#Compiler
CC = gcc

#Clear existing suffixes
.SUFFIXES:

#Impicit Rules
.SUFFIXES: .exe .o .c

.c.o:
	$(CC) $(CFLAGS) $<  

.o.exe:
	$(CC) $(LINK_FLAGS) $< -o  $*.exe
#Explicit Rules

dannyVizPSF: ipp_psf_model.o array_functions.o  dannyVizPSF.o
	$(CC)  $(LINK_FLAGS) $^ -o ../../bin/dannyVizPSF

clean:
	rm *.o
