/**
 *
 * Header file from the PSF model drawer based on code from IPP
 *
 */

#ifndef H_IPP_MODEL_PSF
#define H_IPP_MODEL_PSF


int ellipse_pols_to_model_params(float E0, float E1, float E2, float* SXX, float* SYY, float* SXY);
float* ipp_psf_viz(float E0, float E1, float E2, float K, int sizex, int sizey, float XPOS, float YPOS, float image_scale, float alpha);
int read_psf_file(char* filename, float* E0s,float* E1s, float*  E2s, float* Ks, float* alpha, int** nside);
void  ipp_choose_convolution_size(float E0, float E1, float E2, float K, float alpha, int* xsize , int* ysize, float scale, float* fracEnc);
void interpolate_model(ippPSFModel psf, long xsize, long ysize, double x, double y, float *E0, float *E1, float *E2, float *k);

#endif
