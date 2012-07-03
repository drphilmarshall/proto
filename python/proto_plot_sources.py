#!/usr/bin/env python
# ======================================================================
# Copyright 2011 Phil Marshall (Oxford) and Eric Morganson (MPIA).
# All rights reserved (for now).

# Globally useful modules:

import matplotlib
# Force matplotlib to not use any Xwindows backend:
matplotlib.use('Agg')

# Fonts, latex:
matplotlib.rc('font',**{'family':'serif', 'serif':['TimesNewRoman']})
matplotlib.rc('text', usetex=True)

import string,numpy,pylab,sys,os,getopt
import atpy,pyfits,pywcs
import proto
import pylab as plt

# ======================================================================

def proto_plot_sources(argv):

  USAGE = """
  NAME
    proto_plot_sources.py

  PURPOSE
    Read in a catalogue, including ra and dec, and plot all the sources in it
    overlaid on the cutout image of each.

  COMMENTS
    Compute ellipse parameters a,b,phi for all sources in a catalog, which is
    assumed to be for a particular patch of sky. Use MJDobs and filter values 
    to draw representation of each source in each observation. Display each
    source as an ellipse with second moments as in the catalog,  coloured by
    filter. Object name is shown in the top left hand corner, MJD and filter
    are in  the bottom lefthand corner.
    Plot names are based in image names: target_filter_sci.fits is plotted as
    target_filter_sci_annotated.png
    
  USAGE
    proto_plot_sources.py [flags] [options] catalog image1.fits image2.fits ...

  FLAGS
          -h             Print this message
          -v             Be verbose

  INPUTS
          catalog        Source catalog
          image*.fits    Cutout images for each epoch/filter combo.

  OPTIONAL INPUTS
          -r radius      Only plot sources within some radius in arcsec [Inf]
          -s altcatalog  Alternative source catalog (for comparison, fainter)

  OUTPUTS
          plot1,plot2,... Plots of source positions and fluxes 

  EXAMPLES

    proto_plot_sources.py -v -r 3 H1413+117_10x10arcsec_sources.fits \
                          H1413+117_10x10arcsec_?????.?????_z_sci.fits
   
  
  DEPENDENCIES
    astrometry,atpy,matplotlib
  
  BUGS
     - moments/ellipticities may be either wrong or badly interpreted

  HISTORY
    2010-08-17 started Marshall (Oxford)
    2012-07-01 adapted to overlay patches on images 
  """

  # --------------------------------------------------------------------

  try:
      opts, args = getopt.getopt(argv, "hvr:s:", ["help","verbose","radius=","secondcatalog="])
  except getopt.GetoptError, err:
      # print help information and exit:
      print str(err) # will print something like "option -a not recognized"
      print USAGE
      return

  vb = False
  radius = None
  altcatalog = None
  
  for o,a in opts:
      if o in ("-v", "--verbose"):
          vb = True
      elif o in ("-h", "--help"):
          print USAGE
          return
      elif o in ("-r", "--radius"):
          radius = a
      elif o in ("-s", "--secondcatalog"):
          altcatalog = a
      else:
          assert False, "unhandled option"
   
  if len(args) > 1 :
      catalog = args[0]
      fitsfiles = args[1:]
      if vb: 
        print " "
        print "Plotting sources in catalog:",catalog
        print "overlaid on",len(fitsfiles),"images"
        if altcatalog: print "Also showing sources from:",altcatalog
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
  if vb: print "  in",len(uniqfilters),"bands:",uniqfilters
  uniqepochs = numpy.unique(source.table['mjd_obs'])
  if vb: print "  at",len(uniqepochs),"epochs"
  
  # Compute ellipticities:
  source.ellipse_parameters()
  
  # Optional second catalog (to be shown in dots):
  if altcatalog:
    altsource = proto.proto_source_catalog(altcatalog)
    Naltsrc = altsource.number
    if vb: print "Read in",Nsrc,"alternative sources"
    altsource.ellipse_parameters()
  
  # --------------------------------------------------------------------

  # Loop over fits files, pulling out sources and plotting:
  
  for fitsfile in fitsfiles:
    
    # Read in image header and data:
    hdulist = pyfits.open(fitsfile)
    # Check for empty extension, if so advance to next extension:
    k,NAXIS = -1,0
    while NAXIS == 0 :
      k += 1
      hdr = hdulist[k].header
      NAXIS = hdr['NAXIS']
    img = hdulist[k].data
    bad = (img != img)
    img[bad] = 0.0

    # Read WCS, and measure pixel scale:
    wcs = pywcs.WCS(hdr)
    cell = proto.pixscale(hdr) 

    # Extract MJD from FITS header:
    if hdr.has_key('PSCAMERA') :
      # PS1 data:
      MJD = hdr['MJD-OBS']
      filter = hdr['HIERARCH FPA.FILTER']
      band = string.split(filter,'.')[0]
    else :
      MJD = hdr['MJD']
      band = hdr['FILTER']
    MJDstring = "%.5f" % MJD
    
    # Write output png filename:
    pngfile = fitsfile.replace('.fits','_annotated.png')

    # Start plot:
    figprops = dict(figsize=(4.0,4.0), dpi=128)                                          # Figure properties
    fig = plt.figure(**figprops)
    plt.clf()
    adjustprops = dict(\
      left=0.0,\
      bottom=0.0,\
      right=1.0,\
      top=1.0)
    fig.subplots_adjust(**adjustprops)
    
    # Plot image, with sensible limits on flux: 
    plt.gray()
    scale = numpy.std(img[numpy.logical_not(bad)])
    if scale == 0.0: scale = 1.0
    kwargs = dict(interpolation='nearest', origin='lower',
                     vmin=-10.*scale, vmax=3.*scale)
    plt.imshow(-img, **kwargs)
    
    # Turn off the axis ticks and labels:
    ax = pylab.gca()
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])

    sources = [(source, 1.)]
    ns = []
    if altcatalog:
       sources.append((altsource, 0.3))
    for s,a in sources:
       # Which (if any) entries in the source table belong to this image?
       # Find detection MJDs within 1 second of the image MJD.
       index = numpy.flatnonzero(numpy.abs(s.table['mjd_obs'] - MJD) < 1.0/86400.0)
       if len(index) > 0:
          # Add ellipses as outlined patches:    
          for i in index:
             source_plot_ellipse(s.table[i],wcs,alpha=a)
       ns.append(len(index))      

    # Legends:
    text = "MJD = %s, %s band" % (MJDstring,band)
    # plt.title(text,va='top')
    plt.text(1,1, text, fontsize=18)
    
    # Save plot:
    plt.savefig(pngfile)   
    if vb: print "New plot, of",ns,"sources: "+pngfile
    
  return
  
# ======================================================================
# Plot an ellipse, given a row of a source table:
def source_plot_ellipse(s,wcs,alpha=1.0):
    
    # Convert ra and dec of source to pixel coordinates:
    ra = s['ra']
    dec = s['dec']
    xy = wcs.wcs_sky2pix(numpy.array([[ra,dec],[ra,dec]]),0)
    x,y = xy[0]
    
    # Color and shape:
    a = s['moments_a']/s['pltscale']
    b = s['moments_b']/s['pltscale']
    phi = s['moments_theta']
    color = s['plotcolor']

    # Make patch and plot it:
    epatch = ellipse((x,y),(a,b),orientation=phi,lw=1.0/alpha**2,fc='none',ec=color,alpha=alpha)    
    plt.gca().add_patch(epatch)
    
#     # Debugging - label ellipses with flags.
#     text = "%s" % s['flags']
#     plt.text(x,y,text,color=color)
    
#     # Debugging - compare with SExtractor image coords x and y:     
#     x,y = s['x']-1.0,s['y']-1.0
#     plt.plot([x],[y],'.',ms=2,color='b')
#     
#     # Make patch and plot it:
#     epatch = ellipse((x,y),(a,b),orientation=phi,fc='none',alpha=0.5,ec=color)    
#     pylab.gca().add_patch(epatch)
    
    return

# ======================================================================
# Return an N-sided polygon in teh shape of an ellipse:
# Orientation in degrees. +90 is to account for different definition of 
# orientation between SExtractor  (and IPP?) and pylab.

def ellipse((x,y), (a, b), orientation=0, resolution=100, **kwargs):

    # phi = numpy.deg2rad(orientation+90.0)
    phi = numpy.deg2rad(orientation)
    theta = 2*numpy.pi*pylab.arange(resolution)/resolution
    xs = a * numpy.cos(theta)
    ys = b * numpy.sin(theta)
    xr = x + xs * numpy.cos(phi) - ys * numpy.sin(phi)
    yr = y + xs * numpy.sin(phi) + ys * numpy.cos(phi)

    return pylab.Polygon(zip(xr, yr), **kwargs)
    
# ======================================================================

# If called as a script, the python variable __name__ will be set to 
# "__main__" - so test for this, and execute the main program if so.
# Writing it like this allows the function to be called
# from the python command line as well as from the unix prompt.

if __name__ == '__main__':
  proto_plot_sources(sys.argv[1:])

# ======================================================================


