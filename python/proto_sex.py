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
       outputfile = name+'_sources.fits'
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
      cell = proto.pixscale(hdr) 
      # if vb: print "Pixel scale =",cell

      # Extract filter, MJD, GAIN and zero point from FITS header:
      if hdr.has_key('PSCAMERA') :
        # PS1 data:
        filter = hdr['HIERARCH FPA.FILTER']
        filter = string.split(filter,'.')[0]
        MJD = hdr['MJD-OBS']
        zpt = hdr['FPA.ZP']
        gain = hdr['HIERARCH CELL.GAIN']
      else :
        filter = hdr['FILTER']
        MJD = hdr['MJD']
        zpt = hdr['MAGZERO']
        gain = hdr['GAIN']
      MJDstring = "%.5f" % MJD

      # Find weight (var) file that goes with scifile:
      varfile = find_whtfile(scifile,suffix='var')

      # Now call SExtractor, returning a table:
      catalog = call_sextractor(zpt,gain,scifile,whtfile=varfile)
      
      if vb: print "Extracted",len(catalog),"sources from "+scifile
      
      # Add columns containing MJD and filter:
      catalog = paste_column(catalog,'mjdobs',numpy.array([MJD]),fill='copy')
      catalog = paste_column(catalog,'filterid',numpy.array([filter]),fill='copy')
      
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
   
   # Clean catalog with flags:
   
   
   # Rename columns to match PS1 measurements:
   # t.rename_column('time','space')
   
   # Write out table to output file:
   if vb: print "Writing catalog to ",outputfile

   # Add some comments and keywords at the end of the catalog header:
   master.add_comment("SExtractor catalog made by proto_sex.py")
   master.add_comment("P.J. Marshall, June 2012")

   if os.path.exists(outputfile): os.remove(outputfile) 
   master.write(outputfile,type='FITS')                      

   return

# ======================================================================
# Set up and run SExtractor:

def call_sextractor(zpt,gain,scifile,whtfile=None):
   
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
   
   defconvfile = 'default.conv'
   if not os.path.exists(defconvfile): 
      command = 'cp '+os.environ['PROTO_DIR']+'/sex/'+defconvfile+' .'
      subprocess.call(command, shell=True)
   
   command = 'cat '+defsexfile+' | sed s/xxxZPT/'+str(zpt)+'/g' \
                              +' | sed s/xxxGAIN/'+str(gain)+'/g' \
                              +' | sed s/xxxPARFILE/'+defparfile+'/g' \
                              +' | sed s/xxxCATALOG/'+catfile+'/g' \
                              +' > '+sexfile
   subprocess.call(command, shell=True)
   
   # Run SExtractor:
   command = 'sex -c '+sexfile
   if whtfile:
     command += ' -WEIGHT_TYPE MAP_VAR -WEIGHT_IMAGE '+whtfile
   command += ' '+scifile  
   subprocess.call(command, shell=True)
   
   # Read in table:
   table = atpy.Table(catfile,type='fits',hdu=2)
      
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
         values[nx+1:nt] = x[-1]
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


