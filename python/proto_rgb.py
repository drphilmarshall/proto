#!/usr/bin/env python
# ======================================================================

# Globally useful modules:

import matplotlib
# Force matplotlib to not use any Xwindows backend:
matplotlib.use('Agg')

import numpy,sys,os,getopt,pyfits,pywcs,proto,aplpy

# ======================================================================

def proto_rgb(argv):

  USAGE = """
  NAME
    proto_rgb.py

  PURPOSE
    Given a list of FITS files, produce an rgb image.

  COMMENTS
    
  USAGE
    proto_rgb.py [flags] [options]  image1 image2 ...

  FLAGS
          -h             Print this message
          -v             Be verbose

  INPUTS
          image1, etc    List of 3 images to combine into RGB display

  OPTIONAL INPUTS
          -n name        Name to prefix output filenames with
          
  OUTPUTS
          rgb

  EXAMPLES

    proto_rgb.py -v -b \
      -n CSWA1 \
      177.13811  19.50089  15 \
      CSWA1_13x10arcmin_?_sci.fits
      
    ls  CSWA1_15*
      CSWA1_15x15arcsec_r_sci.fits CSWA1_15x15arcsec_z_sci.fits
      CSWA1_15x15arcsec_i_sci.fits CSWA1_15x15arcsec_u_sci.fits
      CSWA1_15x15arcsec_g_sci.fits
  
  
  DEPENDENCIES
    pyfits
  
  BUGS

  HISTORY
    2010-08-15 started Marshall (Oxford)      
  """

  # --------------------------------------------------------------------

  try:
      opts, args = getopt.getopt(argv, "hvbn:", ["help","verbose","name="])
  except getopt.GetoptError, err:
      # print help information and exit:
      print str(err) # will print something like "option -a not recognized"
      print USAGE
      return

  vb = False
  backsub = False
  name = 'rgb'
  for o,a in opts:
      if o in ("-v", "--verbose"):
          vb = True
      elif o in ("-h", "--help"):
          print USAGE
          return
      elif o in ("-n", "--name"):
          name = a
      else:
          assert False, "unhandled option"
   
  if len(args) == 3 :
      redfile = args[0]
      greenfile = args[1]
      bluefile = args[2]
      if vb: 
        print " "
        print "Making RGB png image from the following input files:"
        print "  ",redfile,greenfile,bluefile
        print "Output files will be prefixed with",name
  else :
      print USAGE
      return

  # --------------------------------------------------------------------

  # Measure image stats:
  hdulist = pyfits.open(redfile)
  redimage = hdulist[0].data
  redstats = proto.imagestats(redimage)
  hdulist.close()
  hdulist = pyfits.open(greenfile)
  greenimage = hdulist[0].data
  greenstats = proto.imagestats(greenimage)
  hdulist.close()
  hdulist = pyfits.open(bluefile)
  blueimage = hdulist[0].data
  bluestats = proto.imagestats(blueimage)
  hdulist.close()

  # Plot from a*sigma to b*sigma, using each channel's sigma
  a = 0.5
  b = 8

  # Set up output filename:
  output = name+'_rgb.png'

  # Call aplply:
  
  pmin,pmax = 50.0,99.0
  stretch = 'linear'
  mid = None
  
#   aplpy.make_rgb_image([redfile,greenfile,bluefile],output,
#                        pmin_r=pmin, pmax_r=pmax, 
#                          stretch_r=stretch, vmid_r=mid, 
#                        pmin_g=pmin, pmax_g=pmax, 
#                          stretch_g=stretch, vmid_g=mid, 
#                        pmin_b=pmin, pmax_b=pmax, 
#                          stretch_b=stretch, vmid_b=mid, )
#   
  aplpy.make_rgb_image([redfile,greenfile,bluefile],output,
                       vmin_r=a*redstats['stdev'], vmax_r=b*redstats['stdev'], 
                         stretch_r=stretch, vmid_r=mid, 
                       vmin_g=a*greenstats['stdev'], vmax_g=b*greenstats['stdev'], 
                         stretch_g=stretch, vmid_g=mid, 
                       vmin_b=a*bluestats['stdev'], vmax_b=b*bluestats['stdev'], 
                         stretch_b=stretch, vmid_b=mid, )
  
  # See http://aplpy.github.com/documentation/api.html#rgb-images for
  # more information.
  
  if vb: print "Finished RGB image file:",output
              
  return

# ======================================================================

# If called as a script, the python variable __name__ will be set to 
# "__main__" - so test for this, and execute the main program if so.
# Writing it like this allows the function addnoise to be called
# from the python command line as well as from the unix prompt.

if __name__ == '__main__':
  proto_rgb(sys.argv[1:])

# ======================================================================


