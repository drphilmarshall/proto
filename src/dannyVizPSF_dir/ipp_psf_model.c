/*+
 *  Name:
 *     ipp_model_psf

 *  Purpose:
 *     Rooutines for PS1 IPP PSF generation.

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
 *     DJF: Daniel J. Farrow
 *     (And authors of the IPP code of Pan-STARRS) 
 *     {enter_new_authors_here}

 *  History:
 *     24-MAR-2010 (DJF):
 *        Original version, lots copied from the ppVizPSF and psLib codes
 *        in the Pan-STARRS IPP source code. That code is copyright IfA.
 *-
 */


#include <stdio.h>
#include <math.h>
#include "string.h"
#include "fitsio.h"
#include "array_functions.h"

# define SQRT2   1.41421356 

/**
 * Stokes polarisation parameters -> model parameters (adapted from IPP's pslib)
 * original file in: http://svn.pan-starrs.ifa.hawaii.edu/trac/ipp/browser/trunk/psLib/src/math/psEllipse.c
 */
int ellipse_pols_to_model_params(float E0, float E1, float E2, float* SXX, float* SYY, float* SXY)
{
  double theta ;
  double cs, sn;
  double ds=0.0, major, minor;
  double f1, f2, SXR, SYR;

  theta = 0.5*atan2(E2, E1);

  cs = cos(2.0*theta);
  sn = sin(2.0*theta);
  
  if ((cs > 0.707) || (cs < -0.707)) {
    ds = E1 / cs;
  } 
  else {
    ds = E2 / sn;
  }

  major = sqrt(0.5*(E0 + ds));
  minor = sqrt(0.5*(E0 - ds));

  f1 = 1.0/(minor*minor) + 1.0/(major*major);
  f2 = 1.0/(minor*minor) - 1.0/(major*major);
  
  SXR = 0.5*f1 - 0.5*f2*cos(2*theta);
  SYR = 0.5*f1 + 0.5*f2*cos(2*theta);

  *SXX = SQRT2/sqrt(SXR);
  *SYY = SQRT2/sqrt(SYR);
  *SXY = -0.5*f2*sin(2*theta);

  return 0;
}


float linear_interpolation( float val1, float val2, float x1, float x2, float x)
{
  float ret;
  
  ret= (1.0/((x2 - x1)))*(val2*(x - x1) + val1*(x2 - x));
  
  return ret;
}

float bilinear_interpolation(float val11, 
			     float val12, 
			     float val21, 
			     float val22, float x1, float y1, float x2, float y2, float x, float y)
{
  float ret;

  ret = (1.0/((x2 - x1)*(y2 - y1))) * ( val11*(x2 - x)*(y2 - y) + val21*(x - x1)*(y2 - y) + val12*(x2 - x)*(y - y1)
					+ val22*(x - x1)*(y - y1));

  return ret;
}



/**
 *
 Return PSF model parameters for a certain position
*/

void interpolate_model(ippPSFModel psf, long xsize, long ysize, double x, double y, float *E0, float *E1, float *E2, float *k)
{
  /*Sizes of cell to interpolate over*/
  static float xbsize ; 
  static float ybsize ;

  int xcell, ycell;
  int model_num;
  int model_num_save[4];
  float x_cen[9];
  float y_cen[9];
  int i, j;

  /*Size of psf model grid cells */
  xbsize = (float) xsize / (float) psf.nside;
  ybsize = (float) ysize / (float) psf.nside;

  
  printf("%ld %ld\n", xsize, ysize);

  /*Which grid cell are we in?*/
  xcell = floor(x / xbsize);
  ycell = floor(y / ybsize);
  model_num = xcell*psf.nside + ycell;


  if(psf.nside == 1)
    {
      /*Only one model*/
      *E0 = psf.E0s[0];
      *E1 = psf.E1s[0];
      *E2 = psf.E2s[0];
      *k = psf.Ks[0];
    }
  /*More than one model - start the interpolation!*/
  /*Don't interpolate in corners*/
  else if( (x < (xbsize/2.0) && y < (ybsize/2.0)) || 
	   (x > (xsize - (xbsize/2.0)) && y > (ysize - (ybsize/2.0))) ||
	   (x < (xbsize/2.0) && (y > (ysize - ybsize/2.0))) || 
	   (x > (xsize - xbsize/2.0) && (y < (ybsize/2.0)))){
        
    *E0 = psf.E0s[model_num];
    *E1 = psf.E1s[model_num];
    *E2 = psf.E2s[model_num];
    *k = psf.Ks[model_num];
  }
  /**
   *  This section for 2x2 PSF grid
   */
  else if (psf.nside == 2){
   
    /*1D interpolation on sides*/
    if( x < (xbsize/2.0) )
      {
	*E0 = linear_interpolation(psf.E0s[0], psf.E0s[1], ybsize / 2.0, ybsize + ybsize / 2.0, y);
	*E1 = linear_interpolation(psf.E1s[0], psf.E1s[1], ybsize / 2.0, ybsize + ybsize / 2.0, y);
	*E2 = linear_interpolation(psf.E2s[0], psf.E2s[1], ybsize / 2.0, ybsize + ybsize / 2.0, y);
	*k = linear_interpolation(psf.Ks[0], psf.Ks[1], ybsize / 2.0, ybsize + ybsize / 2.0, y);
	}
    else if( x > (xsize - (xbsize/2.0) ))
      {
	*E0 = linear_interpolation(psf.E0s[2], psf.E0s[3], ybsize / 2.0, ybsize + ybsize / 2.0, y);
	*E1 = linear_interpolation(psf.E1s[2], psf.E1s[3], ybsize / 2.0, ybsize + ybsize / 2.0, y);
	*E2 = linear_interpolation(psf.E2s[2], psf.E2s[3], ybsize / 2.0, ybsize + ybsize / 2.0, y);
	*k = linear_interpolation(psf.Ks[2], psf.Ks[3], ybsize / 2.0, ybsize + ybsize / 2.0, y);
      }
    else if( y < (ybsize/2.0) )
      {
	*E0 = linear_interpolation(psf.E0s[0], psf.E0s[2], xbsize / 2.0, xbsize + xbsize / 2.0, x);
	*E1 = linear_interpolation(psf.E1s[0], psf.E1s[2], xbsize / 2.0, xbsize + xbsize / 2.0, x);
	*E2 = linear_interpolation(psf.E2s[0], psf.E2s[2], xbsize / 2.0, xbsize + xbsize / 2.0, x);
	*k = linear_interpolation(psf.Ks[0], psf.Ks[2], xbsize / 2.0, xbsize + xbsize / 2.0, x);
	}
    else if( y > (ysize - (ybsize/2.0) ))
      {
	*E0 = linear_interpolation(psf.E0s[1], psf.E0s[3], xbsize / 2.0, xbsize + xbsize / 2.0, x);
	*E1 = linear_interpolation(psf.E1s[1], psf.E1s[3], xbsize / 2.0, xbsize + xbsize / 2.0, x);
	*E2 = linear_interpolation(psf.E2s[1], psf.E2s[3], xbsize / 2.0, xbsize + xbsize / 2.0, x);
	*k = linear_interpolation(psf.Ks[1], psf.Ks[3], xbsize / 2.0, xbsize + xbsize / 2.0, x);
      }
    else{
      /*Bilinear in middle*/ 	
      /*2x2 Grid, so only 4 points available! */
      *E0 = bilinear_interpolation( psf.E0s[0],
				    psf.E0s[1], 
				    psf.E0s[2],
				    psf.E0s[3], xbsize / 2.0, ybsize / 2.0, xbsize +  xbsize / 2.0, ybsize + ybsize / 2.0, x, y);
    
      *E1 = bilinear_interpolation(  psf.E1s[0], 
				     psf.E1s[1], 
				     psf.E1s[2], 
				     psf.E1s[3], xbsize / 2.0, ybsize / 2.0, xbsize +  xbsize / 2.0, ybsize + ybsize / 2.0, x, y);
      *E2 = bilinear_interpolation(  psf.E2s[0], 
				     psf.E2s[1], 
				     psf.E2s[2], 
				     psf.E2s[3], xbsize / 2.0, ybsize / 2.0, xbsize +  xbsize / 2.0, ybsize + ybsize / 2.0, x, y);
      *k = bilinear_interpolation(  psf.Ks[0], 
				    psf.Ks[1], 
				    psf.Ks[2], 
				    psf.Ks[3], xbsize / 2.0, ybsize / 2.0, xbsize +  xbsize / 2.0, ybsize + ybsize / 2.0, x, y);
    }    
  }
   /**
   *  This section for 3x3 PSF grid
   */
    /* Find the four points we need for bilinear interpolation */
    else if( psf.nside == 3){
    
      /*Calculate the centers of all of the PSF model grid cells */
      for(j = 0; j< psf.nside; j++){
	for(i= 0; i < psf.nside; i++){
	  y_cen[j + psf.nside*i] = j*ybsize + ybsize / 2.0 ;
	  x_cen[j + psf.nside*i] = i*xbsize + xbsize / 2.0 ;
	}
      }

      //for(j=0; j <9; j++){
      //printf("%f, %f\n", x_cen[j], y_cen[j]);
      //}

      
      /*Find out which quadrant we are in,
      use this to determine the required centers*/
    
      /*Upper right*/
      if( x > xsize / 2.0 && y >  ysize / 2.0){
	
	model_num_save[0] = 4;
	model_num_save[1] = 5;
	model_num_save[2] = 7;
	model_num_save[3] = 8;
      }
      /*Lower right */
      else if(x > xsize / 2.0 && y <= ysize /2.0){
	model_num_save[0] = 3;
	model_num_save[1] = 4;
	model_num_save[2] = 6;
	model_num_save[3] = 7;
      }
      /*Lower left */
      else if(x <= xsize / 2.0 && y <=  ysize / 2.0){
	model_num_save[0] = 0;
	model_num_save[1] = 1;
	model_num_save[2] = 3;
	model_num_save[3] = 4;
      }
      /*Upper Left*/
      else if(x < xsize / 2.0 && y > ysize / 2.0){
	model_num_save[0] = 1;
	model_num_save[1] = 2;
	model_num_save[2] = 4;
	model_num_save[3] = 5;
      }
    
      printf("%f %f, %f %f, %f %f, %f %f \n", x_cen[model_num_save[0]], y_cen[model_num_save[0]],
	     x_cen[model_num_save[1]], y_cen[model_num_save[1]],
	     x_cen[model_num_save[2]], y_cen[model_num_save[2]],
	     x_cen[model_num_save[3]], y_cen[model_num_save[3]]);
      
    /*Now we have our four centres, go ahead and do the interpolation*/

    /*First check if we're on a side*/
    /*1D interpolation on sides*/
    if( x < (xbsize/2.0) )
      {
	*E0 = linear_interpolation(psf.E0s[model_num_save[0]], psf.E0s[model_num_save[1]], y_cen[model_num_save[0]],  y_cen[model_num_save[1]], y);
	*E1 = linear_interpolation(psf.E1s[model_num_save[0]], psf.E1s[model_num_save[1]], y_cen[model_num_save[0]],  y_cen[model_num_save[1]], y);
	*E2 = linear_interpolation(psf.E2s[model_num_save[0]], psf.E2s[model_num_save[1]], y_cen[model_num_save[0]],  y_cen[model_num_save[1]], y);
	*k = linear_interpolation(psf.Ks[model_num_save[0]], psf.Ks[model_num_save[1]], y_cen[model_num_save[0]],  y_cen[model_num_save[1]], y);
	}
    else if( x > (xsize - (xbsize/2.0) ))
      {
	*E0 = linear_interpolation(psf.E0s[model_num_save[2]], psf.E0s[model_num_save[3]], y_cen[model_num_save[2]],  y_cen[model_num_save[3]], y);
	*E1 = linear_interpolation(psf.E1s[model_num_save[2]], psf.E1s[model_num_save[3]], y_cen[model_num_save[2]],  y_cen[model_num_save[3]], y);
	*E2 = linear_interpolation(psf.E2s[model_num_save[2]], psf.E2s[model_num_save[3]], y_cen[model_num_save[2]],  y_cen[model_num_save[3]], y);
	*k = linear_interpolation(psf.Ks[model_num_save[2]], psf.Ks[model_num_save[3]], y_cen[model_num_save[2]],  y_cen[model_num_save[3]], y);
      }
    else if( y < (ybsize/2.0) )
      {
	*E0 = linear_interpolation(psf.E0s[model_num_save[0]], psf.E0s[model_num_save[2]], x_cen[model_num_save[0]],  x_cen[model_num_save[2]], x);
	*E1 = linear_interpolation(psf.E1s[model_num_save[0]], psf.E1s[model_num_save[2]], x_cen[model_num_save[0]],  x_cen[model_num_save[2]], x);
	*E2 = linear_interpolation(psf.E2s[model_num_save[0]], psf.E2s[model_num_save[2]], x_cen[model_num_save[0]],  x_cen[model_num_save[2]], x);
	*k = linear_interpolation(psf.Ks[model_num_save[0]], psf.Ks[model_num_save[2]], x_cen[model_num_save[0]],  x_cen[model_num_save[2]], x);
      }
    else if( y > (ysize - (ybsize/2.0) ))
      {
	*E0 = linear_interpolation(psf.E0s[model_num_save[1]], psf.E0s[model_num_save[3]], x_cen[model_num_save[1]],  x_cen[model_num_save[3]], x);
	*E1 = linear_interpolation(psf.E1s[model_num_save[1]], psf.E1s[model_num_save[3]], x_cen[model_num_save[1]],  x_cen[model_num_save[3]], x);
	*E2 = linear_interpolation(psf.E2s[model_num_save[1]], psf.E2s[model_num_save[3]], x_cen[model_num_save[1]],  x_cen[model_num_save[3]], x);
	*k = linear_interpolation(psf.Ks[model_num_save[1]], psf.Ks[model_num_save[3]], x_cen[model_num_save[1]],  x_cen[model_num_save[3]], x);
      }
    else{
      /*Bilinear interpolation on centre*/

      *E0 = bilinear_interpolation( psf.E0s[model_num_save[0]],  
				    psf.E0s[model_num_save[1]],  
				    psf.E0s[model_num_save[2]],  
				    psf.E0s[model_num_save[3]], x_cen[model_num_save[0]], y_cen[model_num_save[0]], x_cen[model_num_save[3]], y_cen[model_num_save[3]],
				    x, y);
      *E1 = bilinear_interpolation( psf.E1s[model_num_save[0]], 
				    psf.E1s[model_num_save[1]],  
				    psf.E1s[model_num_save[2]],  
				    psf.E1s[model_num_save[3]], x_cen[model_num_save[0]], y_cen[model_num_save[0]], x_cen[model_num_save[3]], y_cen[model_num_save[3]],
				    x, y );
      *E2 = bilinear_interpolation( psf.E2s[model_num_save[0]],  
				    psf.E2s[model_num_save[1]],  
				    psf.E2s[model_num_save[2]], 
				    psf.E2s[model_num_save[3]], x_cen[model_num_save[0]], y_cen[model_num_save[0]], x_cen[model_num_save[3]], y_cen[model_num_save[3]],
				    x, y );
      *k = bilinear_interpolation(  psf.Ks[model_num_save[0]], 
				    psf.Ks[model_num_save[1]], 
				    psf.Ks[model_num_save[2]],  
				    psf.Ks[model_num_save[3]], x_cen[model_num_save[0]], y_cen[model_num_save[0]], x_cen[model_num_save[3]], y_cen[model_num_save[3]],
				    x, y);

      printf("%f, %f, %f, %f\n", psf.E2s[model_num_save[0]],  
	     psf.E2s[model_num_save[1]],  
	     psf.E2s[model_num_save[2]],  
	     psf.E2s[model_num_save[3]]);
    }
    
    
    }
  /*PSF model not supported!*/
  else
    {
      printf("Sorry, this PSF model has too large a PSF.TEND.NX / PSF.TREND.NY. Maximum supported is 3x3.\n");
    }
  
  return;
}


/**
 *Create an image of the psf
 * 
 * for PS1_V1 alpha = 1.666
 * for QGAUSS alpha = 2.250
 *
 */
float* ipp_psf_viz(float E0, float E1, float E2, float K, int sizex, int sizey, float XPOS, float YPOS, float image_scale, float alpha)
{  


  /*PSF Model Params*/ 
  float IO = 1.0;
  float SXX = 1.0;
  float SYY = 1.0;
  float SXY = 0.0;

  /*Code stuff*/
  long x=0;
  float xco, yco, z;
  long size;

  /*Image arrays*/
  float* psf_image; 

  size = sizex*sizey;
  
  psf_image = malloc(size*sizeof(float));

  ellipse_pols_to_model_params(E0, E1, E2, &SXX, &SYY, &SXY);

 while (x < sizex){
    long y = 0;
    while (y < sizey){
      xco = (x - XPOS + 1)* image_scale;
      yco = (y - YPOS + 1) * image_scale;
      z = ((xco*xco)/(SXX*SXX) + (yco*yco)/(SYY*SYY)) + xco*yco*SXY;
      *(psf_image + x + y*sizex) =  IO / (pow(z, alpha) + K*z + 1.0) ;
      y++;
    }
    x++;
  }

  return psf_image;
}


/**
 *  Open an .fpa.psf file and read parameters
 *  
 */
int read_psf_file(char* filename, float* E0s,float* E1s, float*  E2s, float* Ks, float* alpha, int **nside) 
{
  fitsfile* fptr_psf;
  int i=0;
  int status_psf=0;
  int ncols;
  int* param_names;
  int p1=0, p2=0, p3=0, p4=0;
  long nrows;
  float* params;
  char psf_model[70];

  fits_open_file(&fptr_psf, filename, READONLY, &status_psf);
  if(status_psf) fits_report_error(stderr, status_psf);

  /* Move to the HDU with the PSF model parameters */
  fits_movabs_hdu(fptr_psf, 2, NULL, &status_psf);
  fits_get_num_cols(fptr_psf, &ncols, &status_psf);
  fits_get_num_rows(fptr_psf, &nrows, &status_psf);
  
  /*Read the PSF model type*/
  fits_read_key(fptr_psf, TSTRING, "PSF_NAME", psf_model, NULL, &status_psf);

  /*Choose appropriate alpha*/
  if(!strcmp("PS_MODEL_PS1_V1", psf_model))
    {
      *alpha = 1.666;
      printf("%e\n", *alpha);
    }
  else if(!strcmp("PS_MODEL_QGAUSS", psf_model))
    {
      *alpha = 2.250;
    }
  else
    {
      printf("ERROR: PSF model %s unsupported\n", psf_model);
      fits_close_file(fptr_psf, &status_psf);
      return 1;
    }


  param_names = malloc(nrows * sizeof(int));
  params = malloc(nrows * sizeof(float));

  /* Read the fits file */
  fits_read_col(fptr_psf,TINT, 1, 1, 1, nrows, NULL, param_names, NULL, &status_psf);
  fits_read_col(fptr_psf,TFLOAT, 4, 1, 1, nrows, NULL, params, NULL, &status_psf);
 
  /* Read in models */
  for(i=0; i<nrows; i++){
    
    if((param_names[i]==4)){ E0s[p1] = params[i];  p1++;}
    if((param_names[i]==5)){ E1s[p2] = params[i];  p2++;}
    if((param_names[i]==6)){ E2s[p3] = params[i];  p3++;}
    if((param_names[i]==7)){ Ks[p4] = params[i];  p4++;}
    
  }

  /*Size of grid models defined on */
  **nside = (int) sqrt(p1);

  /* Free the memory */
  free(params);
  free(param_names);
  
  /* Close and quit if any errors occured */
  fits_close_file(fptr_psf, &status_psf);
  if(status_psf) {fits_report_error(stderr, status_psf); return 1;}

  return 0;
}

/** 
 * Choose a convolution size to fit in fracEnc of PSF flux in the array
 */
void  ipp_choose_convolution_size(float E0, float E1, float E2, float K, float alpha, int* xsize , int* ysize, float scale, float* fracEnc)
{
  int xtry, ytry;
  int xcen, ycen;
  float* hugePSF, * smallPSF;
  double bigSum, smallSum;

  xtry = 101;
  ytry = 101;
  xcen = floorf(xtry / 2.0);
  ycen = floorf(ytry / 2.0);

  hugePSF = ipp_psf_viz(E0, E1, E2, K, 1001, 1001, 500, 500, scale, alpha);
  smallPSF= ipp_psf_viz(E0, E1, E2, K, xtry, ytry, xcen, ycen, scale, alpha);

  bigSum = sum( hugePSF, 1001*1001);
  smallSum = sum(smallPSF, xtry*ytry);

  while((1-((bigSum - smallSum)/ bigSum)) < *fracEnc)
    {
      free(smallPSF);
      printf("%f %d\n", (1-((bigSum - smallSum)/ bigSum)), xtry);
      xtry++;
      ytry++;
      xcen = floorf(xtry / 2.0);
      ycen = floorf(xtry / 2.0);
      smallPSF= ipp_psf_viz(E0, E1, E2, K, xtry, ytry, xcen, ycen, scale, alpha);
      smallSum = sum(smallPSF, xtry*ytry);
    }
  *fracEnc = (1-((bigSum - smallSum)/ bigSum));

  /* Must be odd for the code to work */
  if(xtry%2 != 0) { xtry = xtry + 1;}
  if(ytry%2 != 0) { ytry = ytry + 1;}
  printf("Using boxsize %d %d  contains %f\n", xtry, ytry, *fracEnc);
  *xsize = xtry;
  *ysize = ytry;
}
