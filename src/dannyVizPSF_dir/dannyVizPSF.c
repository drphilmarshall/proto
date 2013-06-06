/**
 *
 Visualise a PS1 PSF
 *
 *
 * AUTHOR: Daniel Farrow 2012
 * parts adapted from Pan-STARRS IPP
*/

#include <stdio.h>
#include "program_variables.h"
#include "ipp_psf_model.h"
#include "array_functions.h"
#include "fitsio.h"

int main(int argc, char* argv[])
{

  fitsfile* fptr = NULL;

  int status = 0;
  int  nside;
  int *pNside = &nside;

  long fpixel[2] = {1,1};
  long naxis[2] = {51, 51};
  long imx, imy;

  float *psfImage = NULL;
  float E0, E0s[10];
  float E1, E1s[10];
  float E2, E2s[10];
  float K, Ks[10];
  float alpha;
  float x, y;

  ippPSFModel psf;

  if(argc < 8){

    printf("\nUSAGE: dannyVizPSF image_x image_y psf_x psf_y stamp_x stamp_y psf_file.fpa.psf output.fits \n *\n * Produces a postage stamp image of the PSF of size stamp_x*stamp_y \n * From a PSF at position psf_x, psf_y from an image of dimensions image_x, image_y \n * \n * Example: dannyVizPSF 6600.0 6600.0 1810.0 221.1 101 101 psf_file.fpa.psf out.fits \n * \n * This generates an image of the PSF model sized 101x101 as it would appear at\n * a position of 1810.0, 221.1 on a skycell of size 6600.0 6600.0\n * NOTES: Only supports up 3x3 square grids for interpolation (i.e. PSF.TREND.NX <= 3 and PSF.TREND.NX=PSF.TREND.NY)\n *\n");

    return 1;

  }

  /*Read command line arguments*/
  sscanf(argv[1], "%ld", &imx);
  sscanf(argv[2], "%ld", &imy);
  sscanf(argv[5], "%ld", &naxis[0]);
  sscanf(argv[6], "%ld", &naxis[1]);
  sscanf(argv[3], "%f", &x);
  sscanf(argv[4], "%f", &y);
  
  /*Read PSF file into 'ippPSFModel' structure */
  if( read_psf_file(argv[7], E0s, E1s, E2s, Ks, &alpha, &pNside) != 0){
    printf("Reading PSF file failed!\n");
    return 1;
  }

  psf.E0s = E0s;
  psf.E1s = E1s;
  psf.E2s = E2s;
  psf.Ks = Ks;
  psf.alpha = alpha;
  psf.nside = *pNside; 

  /*Do the interpolation to identify which parameters to use */
  interpolate_model(psf, imx, imy, x,  y, &E0, &E1, &E2, &K);

  /*Produce the image */
  printf("Interpolated model Parameters- E0: %f  E1: %f E2:  %f K:  %f alpha:  %f\n", E0, E1, E2, K, alpha);
  psfImage = ipp_psf_viz(E0, E1, E2, K, naxis[0], naxis[1], naxis[0]/2.0, naxis[1]/2.0, 1.0, alpha);

  printf("PSF.TREND.NX %d\n", psf.nside);

  /*Output the image */
  fits_create_file(&fptr, argv[8], &status);
  if(status){
    fits_report_error(stderr, status);  
    printf("ERROR: Could not create output file \n");
    free(psfImage);
    return 1;
  }

  fits_create_img(fptr, -64, 2, naxis, &status);
  fits_write_pix(fptr, TFLOAT, fpixel, naxis[0]*naxis[1], psfImage, &status);

  /*Close files */
  fits_close_file(fptr, &status);

  if(status){
    fits_report_error(stderr, status);  
    printf("ERROR: Could not close output file \n");
    free(psfImage);
    return 1;
  }

  free(psfImage);
  return 0;
}
  
  
  
