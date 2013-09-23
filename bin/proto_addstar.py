#! /usr/bin/env python
##!/usr/local/misc/python/Python-2.7.2/bin/python

import sys
if len(sys.argv) != 4:
  print "proto_addstar.py image file format"
  print "Image is a (assumed PS1 postage stamp) fits image. File is a three column ra dec mag table."
  print " format = 0, format is ra dec mag."
  print " format = 1, format is dra ddec mag. dra and ddec are in arcseconds"
  print "Tables can have #-commented headers."
  sys.exit(1)

import pyfits, numpy as np, os

# Opening fits file and getting necessary header values

infitsname=sys.argv[1]
infits=pyfits.open(infitsname)
cra=infits[1].header['RA_DEG']
cdec=infits[1].header['DEC_DEG']
nx=infits[1].header['NAXIS1']; cx=0.5*(nx-1.)
ny=infits[1].header['NAXIS2']; cy=0.5*(ny-1.)
dx=infits[1].header['CDELT1']
dy=infits[1].header['CDELT2']

# Opening text table
inname=sys.argv[2]
intable=np.loadtxt(inname)

# Converting radec to pixels
if int(sys.argv[3]) == 0:
  ras=intable[:,0];  xs=(ras-cra)  /dx+cx
  decs=intable[:,1]; ys=(decs-cdec)/dy+cy
else:
  dras= intable[:,0]; xs=dras /3600./dx +cx
  ddecs=intable[:,1]; ys=ddecs/3600./dy +cy
mags=intable[:,2]; zp= infits[1].header['FPA.ZP'];fluxs=10**(0.4*(zp-mags))*infits[1].header['EXPTIME']

# Opening .psf file and getting necessary header info 
inpsfname=os.path.splitext(infitsname)[0]+'.psf'
inpsf=pyfits.open(inpsfname)

# Figuring out location of source within original image for psf image making 
# This is an estimate and seems to be off by a few arcseconds
sizex=inpsf[1].header['IMAXIS1']; sizey=inpsf[1].header['IMAXIS1'];
offsetx=inpsf[0].header['CRPIX1']-infits[1].header['CRPIX1']; offsety=inpsf[0].header['CRPIX2']-infits[1].header['CRPIX2']
expx=offsetx+cx; expy=offsety+cy
outpsfname=os.path.splitext(infitsname)[0]+'.psf.fits'

# Making PSF image and getting PSF as an array
if os.path.exists(outpsfname):
  os.remove(outpsfname)
psfx=2*nx+1; psfy=2*ny+1
psfcx=nx; psfcy=ny
os.system("dannyVizPSF "+str(sizex)+" "+str(sizey)+" "+str(expx)+" "+str(expy)+" "+str(psfx)+" "+str(psfy)+" "+inpsfname+" "+outpsfname)
psf=pyfits.open(outpsfname)[0].data; 
print np.sum(psf)
psf=psf/np.sum(psf)

# Making Star image
stars=np.zeros([nx,ny])
for num in np.arange(len(xs)):
  xstar=xs[num]+psfcx-cx-nx/2; ystar=ys[num]+psfcy-cy-ny/2; fstar=fluxs[num]
  stars=stars+psf[xstar:xstar+nx,ystar:ystar+ny]*fstar

# Adding star and writing out
outstarname=os.path.splitext(infitsname)[0]+'_star.fits'
if os.path.exists(outstarname):
  os.remove(outstarname)
print np.max(stars)
print "Added "+str(len(xs))+" stars."

hdus = pyfits.HDUList([pyfits.PrimaryHDU(infits[0].data,infits[0].header), pyfits.ImageHDU(infits[1].data+stars,infits[1].header)])
hdus.writeto(outstarname)
