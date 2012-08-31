#! /usr/local/misc/python/Python-2.7.2/bin/python
import numpy as np, pyfits, os, sys

if len(sys.argv) != 2:
  print "proto_size_convert.py dir"
  sys.exit(1)

def convertdir(indir,stretchfactor=4,shrinkfactor=5):
  fitss=getfits(indir)
  for fits in fitss:
    convertfits(fits) 

def getfits(indir):
  fitslist=[]
  for fits in os.listdir(indir):
    if 'fits' in fits:
      fitslist.append(indir+'/'+fits)
  return fitslist

def convertfits(inname,stretchfactor=4,shrinkfactor=5):
  outname=inname.rpartition('.'); outname=outname[0]+'_resize'+outname[1]+outname[2]
  if os.path.exists(outname):
    print outname+" exists and will not be remade."
    return ''
  infits=pyfits.open(inname)
  x0=infits[1].header['NAXIS1']
  x1=infits[1].header['NAXIS2']
  if x0 % shrinkfactor:
    print "Error: convertfis cannot divide axis 0 ("+str(x0)+") by "+str(shrinkfactor)
    return 1
  if x1 % shrinkfactor:
    print "Error: convertfits cannot divide axis 1 ("+str(x1)+") by "+str(shrinkfactor)
    return 1
  inarr=infits[1].data
  [x0,x1]=inarr.shape
  if x0 % shrinkfactor:
    print "Error: convertfis cannot divide axis 0 ("+str(x0)+") by "+str(shrinkfactor)
    return 1
  if x1 % shrinkfactor:
    print "Error: convertfits cannot divide axis 1 ("+str(x1)+") by "+str(shrinkfactor)
    return 1
  infits[1].header['NAXIS1']=x0*stretchfactor/shrinkfactor
  infits[1].header['NAXIS2']=x1*stretchfactor/shrinkfactor
  infits[1].header['CDELT1']=infits[1].header['CDELT1']*(1.0*shrinkfactor/stretchfactor)
  infits[1].header['CDELT2']=infits[1].header['CDELT2']*(1.0*shrinkfactor/stretchfactor)
  outname=inname.rpartition('.'); outname=outname[0]+'_resize'+outname[1]+outname[2]
  infits[1].data=shrink(stretch(inarr,stretchfactor),shrinkfactor)
  outfits=pyfits.HDUList([pyfits.PrimaryHDU(infits[0].data,infits[0].header), pyfits.ImageHDU(infits[1].data,infits[1].header)])
  outfits.writeto(outname)

def shrink(inarr,factor):
  x0=inarr.shape[0]
  x1=inarr.shape[1]
  if x0 % factor:
    print "Error: shrink cannot divide axis 0  ("+str(x0)+") by "+str(factor)
    return 1
  if x1 % factor:
    print "Error: shrink cannot divide axis 1  ("+str(x1)+") by "+str(factor)
    return 1
  return np.sum(np.sum(inarr.reshape([x0/factor,factor,x1/factor,factor]), axis=3),axis=1)

def stretch(inarr,factor):
  x0=inarr.shape[0]
  x1=inarr.shape[1]
  return (inarr.reshape([x0,1,x1,1])*np.ones([1,factor,1,factor])).reshape([x0*factor,x1*factor])/(1.0*factor*factor)
 
convertdir(sys.argv[1])
