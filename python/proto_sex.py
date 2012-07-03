#!/usr/bin/env python
# ======================================================================

# Globally useful modules:

import numpy,sys,os,getopt,pyfits,pywcs,string,atpy,subprocess

import proto

# ======================================================================

def proto_sex(argv):

   USAGE = """
   NAME
     proto_sex.py

   PURPOSE
     Given a list of fits images, run SExtractor on each one, concatenate 
     resulting tables and write out to file.

   COMMENTS

   USAGE
     proto_sex.py [flags] [options]  image1 image2 image3 ...

   FLAGS
           -h             Print this message
           -v             Be verbose

   INPUTS
           image1, etc    List of input images

   OPTIONAL INPUTS
           -n name        Name to prefix output filenames with

   OUTPUTS
       *_sources.fits     Catalog

   EXAMPLES

     proto_sex.py -v -n H1413+117_10x10arcsec \
                  H1413+117_10x10arcsec_?????.?????_*sci.fits

   DEPENDENCIES
     pyfits, ATpy, SExtractor

   BUGS
     - moments/ellipticities may be either wrong or badly interpreted

   HISTORY
     2012-06-26 started Marshall (Oxford)      
   """

   # --------------------------------------------------------------------

   try:
       opts, args = getopt.getopt(argv, "hvn:", ["help","verbose","name="])
   except getopt.GetoptError, err:
       # print help information and exit:
       print str(err) # will print something like "option -a not recognized"
       print USAGE
       return

   vb = False
   backsub = False
   name = 'source_catalog'
   
   # outtype = 'fits'
   # outtype = 'ascii'
   outtype = 'ipac'
   
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

   if len(args) > 0 :
       inputfiles = (args[:])
       outputfile = name+'_sources.'+outtype
       if vb: 
         print " "
         print "Running SExtractor on the following input files:"
         print "  ",inputfiles
         print "Output source catalog file will be",outputfile
   else :
       print USAGE
       return

   # --------------------------------------------------------------------

   # Loop over images:

   first = True
   for scifile in inputfiles:

      # Read in image header:
      hdulist = pyfits.open(scifile)
      # Check for empty extension, if so advance to next extension:
      k,NAXIS = -1,0
      while NAXIS == 0 :
        k += 1
        hdr = hdulist[k].header
        NAXIS = hdr['NAXIS']

      # if vb: print "Read in header from extension",k,"of",scifile

      # Read WCS, and measure pixel scale:
      wcs = pywcs.WCS(hdr)
      pltscale = proto.pixscale(hdr) 
      # if vb: print "Pixel scale =",pltscale

      # Extract filter, MJD, GAIN and zero point from FITS header:
      if hdr.has_key('PSCAMERA') :
        # PS1 data:
        filter = hdr['HIERARCH FPA.FILTER']
        # filter = string.split(filter,'.')[0]
        MJD = hdr['MJD-OBS']
        zpt = hdr['HIERARCH FPA.ZP']
        if zpt == 'NaN': zpt = 30.0  # HACK.
        gain = hdr['HIERARCH CELL.GAIN']
        FWHM = hdr['HIERARCH CHIP.SEEING']*pltscale # in arcsec
        if (FWHM <= 0 or FWHM > 100): FWHM = 0.999999 # red flag value
      else :
        filter = hdr['FILTER']
        MJD = hdr['MJD']
        zpt = hdr['MAGZERO']
        gain = hdr['GAIN']
        FWHM = 0.9 # in arcsec
      MJDstring = "%.5f" % MJD

      # Find weight (var) file that goes with scifile:
      varfile = find_whtfile(scifile,suffix='var')

      # Now call SExtractor, returning a table:
      catalog = call_sextractor(zpt,gain,pltscale,FWHM,scifile,whtfile=varfile)
      
      if vb: print "Extracted",len(catalog),"sources from "+scifile
      
      # Add columns containing MJD and filter, and platescale. Note position
      # angle is zero because we measured moments in world coords:
      catalog = paste_column(catalog,'mjd_obs',numpy.array([MJD]),fill='copy')
      catalog = paste_column(catalog,'filterid',numpy.array([filter]),fill='copy')
      catalog = paste_column(catalog,'pltscale',numpy.array([pltscale]),fill='copy')
      catalog = paste_column(catalog,'posangle',numpy.array([0.0]),fill='copy')
      
      # Concatenate this catalog into the master catalog
      if first:
         master = catalog
         first = False
      else:
         master.append(catalog)
      
      # Add this file name to end of the catalog header:
      master.add_keyword("FITSFILE", scifile)  

   # End of loop over inputfiles.
   
   # -------------------------------------------------------------------------
         
   # Write out table to output file:
   if vb: print "Writing catalog to ",outputfile

   # Add some comments and keywords at the end of the catalog header:
   master.add_comment("SExtractor catalog made by proto_sex.py")
   master.add_comment("P.J. Marshall, June 2012")

   if os.path.exists(outputfile): os.remove(outputfile) 
   master.write(outputfile,type=outtype)                      

   return

# ======================================================================
# Set up and run SExtractor:

def call_sextractor(zpt,gain,pltscale,FWHM,scifile,whtfile=None):
   
   tidy = False
   
   # Make a config file:
   catfile = scifile.replace('sci.fits','sources.fits')
   sexfile = scifile.replace('fits','sex')
   
   defsexfile = 'proto.sex'
   if not os.path.exists(defsexfile): 
      command = 'cp '+os.environ['PROTO_DIR']+'/sex/'+defsexfile+' .'
      subprocess.call(command, shell=True)
   
   defparfile = 'proto.param'
   if not os.path.exists(defparfile): 
      command = 'cp '+os.environ['PROTO_DIR']+'/sex/'+defparfile+' .'
      subprocess.call(command, shell=True)
   
   # defconvfile = 'gauss_1.5_3x3.conv'
   # defconvfile = 'mexhat_1.5_5x5.conv'
   defconvfile = 'mexhat_2.5_7x7.conv'
   if not os.path.exists(defconvfile): 
      command = 'cp '+os.environ['PROTO_DIR']+'/sex/'+defconvfile+' .'
      subprocess.call(command, shell=True)
   
   command = 'cat '+defsexfile+' | sed s/xxxZPT/'+str(zpt)+'/g' \
                              +' | sed s/xxxGAIN/'+str(gain)+'/g' \
                              +' | sed s/xxxFWHM/'+str(FWHM)+'/g' \
                              +' | sed s/xxxPARFILE/'+defparfile+'/g' \
                              +' | sed s/xxxCATALOG/'+catfile+'/g' \
                              +' > '+sexfile
   subprocess.call(command, shell=True)
   
   # Run SExtractor:
   command = 'sex -c '+sexfile
   if whtfile:
     command += ' -WEIGHT_TYPE MAP_VAR -WEIGHT_IMAGE '+whtfile
   # command += ' '+scifile
   command += ' '+scifile+' >& /dev/null'
   subprocess.call(command, shell=True)
   
   # Read in table:
   table = atpy.Table(catfile,type='fits',hdu=2)
      
   # Rename columns to match PS1 names:
   table.rename_column('ALPHA_J2000','ra')   
   table.rename_column('DELTA_J2000','dec')   
   # table.rename_column('X_IMAGE','x')   
   # table.rename_column('Y_IMAGE','y')   
   table.rename_column('X2_WORLD','moments_xx')   
   table.rename_column('XY_WORLD','moments_xy')   
   table.rename_column('Y2_WORLD','moments_yy')   
   table.rename_column('FLUX_AUTO','kron_flux')   
   table.rename_column('FLUXERR_AUTO','kron_flux_err')
   # Note: Kron mags are missing from PS1 IPP catalogs...
   #   Thing we use is "cal_psf_mag" which is actually something quite
   #   different. Best to use fluxes not mags?   
   table.rename_column('MAG_AUTO','kron_mag')   
   table.rename_column('MAGERR_AUTO','kron_mag_err')   
   table.rename_column('FLAGS','flags')   
      
   # Convert moments to pixels:
   scale = (3600.0*3600.0)/(pltscale*pltscale)
   table.moments_xx *= scale
   table.moments_xy *= scale
   table.moments_yy *= scale
    
   # Clean catalog with flags:
   
   
   # Clean up:
   if tidy:
      command = 'rm -f '+catfile+' '+defsexfile+' '+defparfile+' '+defconvfile
      subprocess.call(command, shell=True)
  
   return table
      
# ======================================================================
# See if there is a corresponding wht image available:

def find_whtfile(scifile,suffix='var'):

    whtfile = scifile.replace('sci',suffix)
    if not os.path.exists(whtfile): 
       whtfile = None
    
    return whtfile

# ======================================================================
# Add column name=x to table, filling space if needed:

def paste_column(table,name,x,fill='zeros'):
   
   nt = len(table)
   nx = len(x)
   if nx != nt:
      values = numpy.zeros(nt,dtype=x.dtype)
      if fill == 'zeros':
         values[0:nx] = x
      elif fill == 'copy':
         values[0:nx] = x
         values[nx:nt] = x[-1]
   else:
      values = x.copy()
            
   table.add_column(name,values)
   
   return table
      
# ======================================================================

# If called as a script, the python variable __name__ will be set to 
# "__main__" - so test for this, and execute the main program if so.
# Writing it like this allows the function addnoise to be called
# from the python command line as well as from the unix prompt.

if __name__ == '__main__':
  proto_sex(sys.argv[1:])

# ======================================================================


