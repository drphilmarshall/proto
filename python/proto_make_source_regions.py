#!/usr/bin/env python
# ======================================================================
# Copyright 2011 Phil Marshall (Oxford) and Eric Morganson (MPIA).
# All rights reserved (for now).

# Globally useful modules:

import string,numpy,pyfits,pywcs,sys,os,getopt

import atpy,proto


# ======================================================================

def proto_make_source_regions(argv):

  USAGE = """
  NAME
    proto_make_source_regions.py

  PURPOSE
    Read in a catalogue, including ra and dec, and produce regions in
    ds9 format for all observations.

  COMMENTS
    Compute ellipse parameters a,b,phi for all sources in a catalog, which is
    assumed to be for a particular patch of sky. Use MJDobs and filter values 
    to make regions for each source in each observation.
    Display each source as an ellipse with second moments as in the catalog, 
    coloured by filter (and shaded by flux?). 
    PSF FWHM is shown in the bottom  left hand corner, object name in the top
    left hand corner,  central ra and dec are shown in the top right hand 
    corner. MJD and filter are in the bottom righthand corner. 
    
  USAGE
    proto_make_source_regions.py [flags] [options] catalog.fits

  FLAGS
          -h             Print this message
          -v             Be verbose

  INPUTS
          catalog.fits   Source catalog

  OPTIONAL INPUTS
          -n name        Name to prefix output filenames with [PS1]
          -r radius      Only plot sources within some radius in arcsec [Inf]

  OUTPUTS
          Region files:
            name+'_'+str(mjdobs)+'_'+filter+'_'+'sci.reg'  
          for all mjdobs and filter  

  EXAMPLES

    proto_make_source_regions.py -v -n H1413+117 -r 5 kl_9.fits
  
  
  DEPENDENCIES
    astrometry,atpy,matplotlib,proto
  
  BUGS

  HISTORY
    2011-10-26 started Marshall (Oxford)      
  """

  # --------------------------------------------------------------------

  try:
      opts, args = getopt.getopt(argv, "hvn:r:", 
         ["help","verbose","name=","radius="])
  except getopt.GetoptError, err:
      # print help information and exit:
      print str(err) # will print something like "option -a not recognized"
      print USAGE
      return

  vb = False
  name = 'PS1'
  Null = -100
  radius = Null
  
  for o,a in opts:
      if o in ("-v", "--verbose"):
          vb = True
      elif o in ("-h", "--help"):
          print USAGE
          return
      elif o in ("-n", "--name"):
          name = a
      elif o in ("-r", "--radius"):
          radius = a
      else:
          assert False, "unhandled option"
   
  if len(args) == 1 :
      catalog = args[0]
      if vb: 
        print " "
        print "Making ds9 regions for all sources in catalog:",catalog
  else :
      print USAGE
      return

  # Semi-arbitrary survey start date:
  #   date2mjd 2010-01-01 09:00:00
  #   survey_start = 55197.375
  survey_start = 0.0
  
  # --------------------------------------------------------------------

  # Read in table:

  source = proto.proto_source_catalog(catalog)
  Nsrc = source.number
  if vb: print "Read in",Nsrc,"sources"
      
  # Detect unique filters and MJDs:
  
  uniqfilters = numpy.unique(source.table['band'])
  if vb: print "  in",len(uniqfilters),"filters:",uniqfilters
  uniqepochs = numpy.unique(source.table['mjd_obs'])
  if vb: print "  at",len(uniqepochs),"epochs"
  
  # mjd_obs defines epoch - these are the ones we need to loop over, 
  # making a region file for each one. First compute ellipticities:
  
  source.ellipse_parameters()
  
  for epoch in uniqepochs:
    
    index = numpy.flatnonzero(source.table['mjd_obs'] == epoch)
    # assume all filters are the same at this epoch:
    filter = source.table['band'][index[0]]
    
    # Write filenames:
    MJDstring = "%.5f" % epoch
    
    regfile = name+'_'+MJDstring+'_'+filter+'_sci.reg'
    fitsfile = name+'_'+MJDstring+'_'+filter+'_sci.fits'

    # Start region file:
    if vb: print "Writing regions to "+regfile
    f = ds9_region_start(regfile,fitsfile)
    
    # Add ellipses:
    for i in index:      
      s = source.table[i]
      ds9_region_ellipse(f,source.table[i])
    if vb: print "  Written",len(index),"source regions to file"
  
    # Extract WCS from fitsfile:
    hdulist = pyfits.open(fitsfile)
    # Check for empty extension, if so advance to next extension:
    ext,NAXIS = -1,0
    while NAXIS == 0 :
      ext += 1
      hdr = hdulist[ext].header
      NAXIS = hdr['NAXIS']
    if vb: print "Read in header from extension",ext,"of",fitsfile
  
    # Annotation regions:
    ds9_region_annotations(f,name,source.table[i],hdr)
  
    ds9_region_finish(f)
    
  return
  
# ----------------------------------------------------------------------------
# Functions to write ds9 region file lines:

def ds9_region_start(regfile,fitsfile):

# Open regfile:
  f = open(regfile,'w')
  
# Write lines:  
  f.write('# Region file format: DS9 version 4.1\n')
  f.write('# Filename: %s\n' % fitsfile)
  f.write('global color=black dashlist=8 3 width=1 font="helvetica 10 normal roman" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n')
  f.write('fk5\n')
    
  return f

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def ds9_region_ellipse(f,s):

  f.write('ellipse(%f,%f,%f",%f",%f) # color="%s" width=2\n' % (s['ra'],s['dec'],s['moments_a'],s['moments_b'],s['moments_theta'],s['plotcolor']))

  return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def ds9_region_annotations(f,name,s,hdr):

  # Figure out size and orientation of field, and get corner positions in 
  # world coordinates:
  x = wcs.calcFootprint(hdr)
  

  # Object name in top lefthand corner, in black:
  ra,dec = 
  f.write('text(%f,%f) text={%s}' % (ra,dec,name))
  # Observation band in top right-hand corner, in plot color:
  ra,dec = 
  f.write('text(%f,%f) text={%s band} # color="%s"' % (ra,dec,s['band'],s['plotcolor']))

  return

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def ds9_region_finish(f):

  f.close()
  
  return

# ======================================================================

# If called as a script, the python variable __name__ will be set to 
# "__main__" - so test for this, and execute the main program if so.
# Writing it like this allows the function to be called
# from the python command line as well as from the unix prompt.

if __name__ == '__main__':
  proto_make_source_regions(sys.argv[1:])

# ======================================================================


