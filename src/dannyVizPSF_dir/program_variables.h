/**
 * program_variables.h
 *
 *  A list of typedefs designed to hold PSFAKE program data. For a 
 *  decription of the parameters see the readme.
 *
 *  D Farrow
 */

#ifndef PROGRAM_VARIABLES_H
#define PROGRAM_VARIABLES_H

typedef struct ipp_psf
{
  int nside;
  float* E0s;
  float* E1s;
  float* E2s;
  float* Ks;
  float alpha;
} ippPSFModel;
  

//This structure holds the source properties
typedef struct properties
{
  float x, y;
  float theta;
  float b_o_a_bulge, b_o_a_disc;
  float rh_bulge, rh_disc;
  float flux_star, flux_bulge, flux_disc;
  float mag_star, mag_bulge, mag_disc;
} sourcePropertyType;

//This structure holds the sizes of the image arrays used
typedef struct image_sizes
{ 
  //Sizes
  int pre_conv_image_x;
  int pre_conv_image_y;  
  int conv_image_x;
  int conv_image_y;
  int cutout_image_x; 
  int cutout_image_y;
  int unbinned_image_x;
  int unbinned_image_y ;
  int original_axis_x;
  int original_axis_y;
  int border_x;
  int border_y;
  int x_psf;
  int y_psf;
} sizeType;


//This structures holds the user's input options
typedef struct options
{
  int subdivs;
  int sizex;
  int sizey;
  int hdunum;
  int bitpix;
  int psf_model_num;
  float scale;
  float coverage;
  float new_psf_width;
  float scaling;
  float zp;
  float mag_const;
  float gain;
  float fracEnc;
  float new_background_var;
  float mag_lim;
  float exptime;
  float pixsize;
  float soft_bias;
  char compressed[10];
  char warp_noise[10];
  char logged[10];
  char new_background[200];
  char catalog_file[200];
  char psf_file[200];
  char weight_out_file[200];
  char weight_map_out[200];
  char infile[200];
  char outfile[200];
  char coverage_file[200];
  char weight[200];
  char wcsfile[200];
  char variable_psf_galaxies[5];
} inputType;


#endif
