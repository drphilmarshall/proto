/**
 *
 *  Header file for the useful array functions 
 * D Farrow
 */

#ifndef H_ARRAY_FUNCTIONS
#define H_ARRAY_FUNCTIONS

#include "program_variables.h"

void bin_array(float* subarray, float* mainarray, int xsize, int ysize, int subdivs, int* status);
void normalize_array(float* array, int x_array_size, int y_array_size, int* status);
int convolve_array(float* array, float* convolution, float* out_array, int x_array_size,\
		   int y_array_size, int x_conarray_size, int y_conarray_size);
float sum(float* array, int n_elements);
void blit_image(float* array1, float* array2, int xsize1, int ysize1,  int xsize2, int ysize2,\
		int x, int y, int* status);
int unbinnedToBinned(int un, int subdivs, int border);
void value_at_position(char* file, float* image, sourcePropertyType* sources, int n_sources, long xsize, long ysize, int* status);
#endif

