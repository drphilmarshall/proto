/*+
 *  Name:
 *    array_functions

 *  Purpose:
 *     Useful functions for dealing with arrays 

 *  Copyright:
 *     Copyright (C) 2010 Durham University
 *     All Rights Reserved.

 *  Licence:
 *     This program is free software; you can redistribute it and/or
 *     modify it under the terms of the GNU General Public License as
 *     published by the Free Software Foundation; either version 2 of the
 *     License, or (at your option) any later version.
 *
 *     This program is distributed in the hope that it will be
 *     useful, but WITHOUT ANY WARRANTY; without even the implied warranty
 *     of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *     GNU General Public License for more details.
 *
 *     You should have received a copy of the GNU General Public License
 *     along with this program; if not, write to the Free Software
 *     Foundation, Inc., 59 Temple Place,Suite 330, Boston, MA
 *     02111-1307, USA

 *  Authors:
 *     DJF: Daniel J. Farrow (Durham University)
 *     {enter_new_authors_here}

 *  History:
 *     24-MAR-2010 (DJF):
 *        Original version
 *     {enter_further_changes_here}
 *-
 */

#include <stdio.h>
#include <math.h>
#include "program_variables.h"

/**
 *
 * Bins an array of (xsize+1)*subdivs by (ysize+1)*subdivs in an array of xsize by ysize
 *
 */
void bin_array(float* subarray, float* mainarray, int xsize, int ysize, int subdivs, int* status)
{
  int row = 0;
  int col = 0;

  /*Abort if status is set */
  if(*status != 0)
    {
      return;
    }

  while ( row < (ysize) )
    {
      while (col < (xsize))
	{
	  double total = 0;
	  int y = 0;
	  while (y < subdivs)
	    {
	      int x = 0;
	      while (x < subdivs)
		{
		  total += (double) *(subarray +((xsize+1)*subdivs)*row*subdivs\
			                   + y*(xsize+1)*subdivs + subdivs*col + x);
		  x++;			  
		}
	      y++;
	    }
	  *(mainarray + (xsize)*row + col) = total ;
	  col++;
	    }
      row++;
      col = 0;
    }

  return;
}

/**
 *
 * Sums an input array
 *
 */
float sum(float* array, int n_elements)
{
  float sum = 0.0;
  int x = 0;

  while (x < n_elements)
    {
      sum += *(array + x);
      x++;
    }
  x = 0;
  return sum;
}

/**
 *
 * Normalizes an input array
 *
 */
void normalize_array(float* array, int x_array_size, int y_array_size, int* status)
{
  float sum = 0.0;
  int x = 0;
  
  /*Abort if status is set */
  if(*status !=0)
    {
      return;
    }

  while (x < (x_array_size * y_array_size))
    {
      sum += *(array + x);
      x++;
    }
  x = 0;
  while (x < (x_array_size * y_array_size))
    {
      *(array + x) = *(array + x) / sum  ;
      x++;
    }
  //printf("\nTotal in array: %f\n", sum);
  return;
}

/**
 *
 * Directly convolves two arrays, leaving a gap around the border of the output array that's the size of the convolution array
 *
 */
void convolve_array(float* array, float* convolution, float* out_array, int x_array_size,\
		                                          int y_array_size, int x_conarray_size, int y_conarray_size)
{
  int row = 0 ;
  int col = 0;
  int array_dim; /* Number of diagonal elements of the matrix from the centre to the top left of the matrix. */
  
  array_dim = (y_conarray_size + 1 ) / 2  - 1;

  row = array_dim;
  col = array_dim;
      
  while ( row < (y_array_size - array_dim))
    {
      while (col < (x_array_size - array_dim))
	{
	  float total = 0;
	  int y = 0;
	  while (y < y_conarray_size )
	    {
	      int x = 0;
	      while (x < x_conarray_size )
		{
		  total += (*(convolution +(x_conarray_size)*y + x)) * (*(array +\
							  (x_array_size) * (row+y - array_dim) +(col- array_dim) + x));
		  x++;
		}
	      y++;
	    }
	  *(out_array + (x_array_size)*(row) + col) = total ;
	  col++;
	}
      
      row++;
      col = array_dim;
    }
  return;
}

/*
 *
 * Adds two 2D arrays, centering array1 on x,y in array2. Array 1 has to have odd x and y.
 *
 */
void blit_image(float* array1, float* array2, int xsize1, int ysize1,  int xsize2, int ysize2,\
		int x, int y, int* status)
{
  int i, j;
  int x_shift;
  int y_shift;
  int array1_xcenter;
  int array1_ycenter;
  
  /*Abort if status is set */
  if(*status !=0)
    {
      return;
    }

  /* If passed -1, center axes of both images */ 
  if(x == -1){
    x_shift = (xsize2 - xsize1) / 2;
    y_shift = (ysize2 - ysize1) / 2;
  }
  else{
    array1_xcenter = (xsize1 - 1) / 2 ;  /* Don't +1 as pixels start at 0 */
    array1_ycenter = (ysize1 - 1) / 2 ;
    x_shift = x - array1_xcenter;
    y_shift = y - array1_ycenter;
  }

  for(i = 0; i< xsize1; i++)
    {
    for(j = 0; j< ysize1; j++)  
      {
	int x2, y2;
	x2 = i + x_shift;
	y2 = j + y_shift;
	if( (x2 >= 0) && (y2 >= 0) && (x2 < xsize2) && (y2 <ysize2)){
	  array2[x2 + y2*xsize2] += array1[i + j*xsize1];
	}
      }
    }
}

/**
 *
 * Convert coordinates in an unbinned from to coords in 
 * the binned frame
 *
 */
//XXX Odd numbers only
int unbinnedToBinned(int un, int subdivs, int border)
{
  int binned;
  binned = un*subdivs + floor( (float) subdivs/2.0 ) + border; 
  return binned;
}

/**
 * Output the input catalogue again, but append a value
 * from an array
 */
 
void value_at_position(char* file, float* image, sourcePropertyType* sources, int n_sources, long xsize, long ysize, int* status)
{
  FILE* fptr=NULL;
  int i=0; /*Index of current source*/
  sourcePropertyType source;

  /*If status is set return */
  if(*status != 0)
    {
      return;
    }
  
  fptr = fopen(file, "w");
  fprintf(fptr, "#x, y, magstar, magbulge, magdisc, rbulge, rdisc, boabul, boadis, theta, value\n");

  for(i=0; i<n_sources; i++)
    {
      float value;
      source = *(sources + i);
      value = -99.0; /*Default if off image*/
      if((source.x < xsize) && (source.y<ysize))
	{
	  value = *(image + (int) (round(source.x)) + (int) ((round(source.y))*xsize) );
	}
      /*Set to -99 if nan*/
      if(isnan(value)) value=-99.0;

      /*Output to file*/
      fprintf(fptr, "%f %f %f %f %f %f %f %f %f %f %f\n", source.x, source.y, source.mag_star, source.mag_bulge,
	     source.mag_disc, source.rh_bulge, source.rh_disc, source.b_o_a_bulge, source.b_o_a_disc,
	     source.theta, value);
    }
      
  fclose(fptr);
  
  return;
}
