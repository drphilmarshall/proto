#!/usr/bin/env python
# ======================================================================

# Globally useful modules:

import numpy,sys,os,getopt,pyfits,pywcs

import proto

# ======================================================================

def proto_cutout(argv):

  USAGE = """
  NAME
    proto_cutout.py

  PURPOSE
    Given a sky position, and a list of FITS files, produce a set of 
    suitably-named cutout images.

  COMMENTS
    
  USAGE
    proto_cutout.py [flags] [options]  ra  dec  w  image1 image2 image2

  FLAGS
          -h             Print this message
          -v             Be verbose
          -b             Subtract background (3-sigma clipping)

  INPUTS
          ra dec         Sky position, in deg
          w              Width of cutout image, in arcsec
          image1, etc    List of input images

  OPTIONAL INPUTS
          -n name        Name to prefix output filenames with
          
  OUTPUTS
          cutout1, etc.  Cutout images

  EXAMPLES

    proto_cutout.py -v -b \
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
  name = 'cutout'
  for o,a in opts:
      if o in ("-v", "--verbose"):
          vb = True
      elif o in ("-h", "--help"):
          print USAGE
          return
      elif o in ("-b"):
          backsub = True
      elif o in ("-n", "--name"):
          name = a
      else:
          assert False, "unhandled option"
   
  if len(args) > 3 :
      ra0 = float(args[0])
      dec0 = float(args[1])
      w = float(args[2])
      inputfiles = (args[3:])
      if vb: 
        print " "
        print "Making",w,"arcsec cutouts centred on",ra0,",",dec0,"degrees"
        print "from the following input files:"
        print "  ",inputfiles
        print "Output files will be prefixed with",name
  else :
      print USAGE
      return

  # --------------------------------------------------------------------

  # Loop over images:

  for input in inputfiles:

    # Read in image header:
    hdulist = pyfits.open(input)
    hdr = hdulist[0].header
    if vb: print "Read in header from ",input
    
    # Read WCS, and measure pixel scale:
    wcs = pywcs.WCS(hdr)
    #  wcs.wcs.print_contents()
    cell = proto.pixscale(hdr) 
    if vb: print "Pixel scale =",cell
    
    iw = 2*int(0.5*w/cell) + 1
    ww = iw*cell
    if vb: print "Cutout size  =",iw,"pixels, or",ww,"arcsec"
        
    # Check if sky position is in image:
    footprint = wcs.calcFootprint(hdr)
    if proto.point_inside_polygon(ra0,dec0,footprint):
      if vb: print "Object centre does lie in footprint of image"

      # Find central pixel:
      x0,y0 = wcs.wcs_sky2pix(ra0,dec0,0)
      i0,j0 = int(x0),int(y0)
      i0,j0 = i0+int(x0-i0 >= 0.5),j0+int(y0-j0 >= 0.5)
      if vb: print "Central pixel:",x0,y0," -> ",[i0,j0]
      # and then edge pixels:
      i1,i2 = i0-(iw-1)/2,i0+(iw+1)/2
      j1,j2 = j0-(iw-1)/2,j0+(iw+1)/2
      # Check for edge of image,
      i1,i2 = numpy.max([0,i1]),numpy.min([hdr['NAXIS1'],i2])
      j1,j2 = numpy.max([0,j1]),numpy.min([hdr['NAXIS2'],j2])
      # and find corresponding cutout pixels:
      imin,imax = iw/2 - (i0 - i1),iw/2 + (i2 - i0)
      jmin,jmax = iw/2 - (j0 - j1),iw/2 + (j2 - j0)
      if vb: print "Input image pixel ranges:",[i1,i2],[j1,j2]
      if vb: print "Non-zero part of cutout:",[imin,imax],[jmin,jmax]
      
      # Make cutout, centred on iw/2:
      cutout = numpy.zeros([iw,iw])
      cutout[jmin:jmax,imin:imax] = hdulist[0].data[j1:j2,i1:i2]
      
      # Subtract background:
      if backsub:
        image = hdulist[0].data
        stats = proto.imagestats(image,clip=3)
        back = stats['median']
        if vb: print "Subtracting constant background:",back
        index = numpy.where(cutout > 0)
        cutout[index] -= back
      
      
      # Almost ready to write out - first adjust hdr:
      x0 = float(iw/2 + x0-i0 + 1)
      y0 = float(iw/2 + y0-j0 + 1)
      if vb: print "Switching to one-indexing,"
      if vb: print "Cutout central pixel:",x0,y0
      # BUG: this is only accurate to ~0.5 pixels with SDSS cutouts, due to 
      # more complex astrometric transformation... Ho hum.
      
      hdr['CRPIX1'] = x0
      hdr['CRPIX2'] = y0
      hdr['CRVAL1'] = ra0
      hdr['CRVAL2'] = dec0
      hdr['NAXIS1'] = iw
      hdr['NAXIS2'] = iw

      # and then set up filename:
      
      filter = hdr['FILTER']
      sw = str(int(w))
      output = name+'_'+sw+'x'+sw+'arcsec_'+filter+'_sci.fits'

      # Write out cutout image to output file:

      if vb: print "Writing cutout image to ",output

      if os.path.exists(output): os.remove(output) 
      pyfits.writeto(output,cutout,hdr)

      if vb: print "Done with",input
          
    else:
      if vb: print "Object centre is not in footprint of image, skipping"
    
  return

# ======================================================================

# If called as a script, the python variable __name__ will be set to 
# "__main__" - so test for this, and execute the main program if so.
# Writing it like this allows the function addnoise to be called
# from the python command line as well as from the unix prompt.

if __name__ == '__main__':
  proto_cutout(sys.argv[1:])

# ======================================================================


