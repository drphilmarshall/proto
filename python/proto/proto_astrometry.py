# ======================================================================
# General-purpose astrometry functions.

# Required modules:

import numpy

# ======================================================================
# Return pixel scale in arcsec:

def pixscale(hdr):

  cd = numpy.zeros([2,2])
  
# eg PS1 data:
  if hdr.has_key('CDELT1') :
    cell = numpy.sqrt(hdr['CDELT1']*hdr['CDELT1'])
# eg SDSS data:
  else :
    cd[0,0] = hdr['CD1_1']
    cd[0,1] = hdr['CD1_2']
    cd[1,0] = hdr['CD2_1']
    cd[1,1] = hdr['CD2_2']
    cell = numpy.sqrt(abs(numpy.linalg.det(cd)))
    
  cell *= 3600.0  

  return cell

# ======================================================================
# From http://www.ariel.com.au/a/python-point-int-poly.html

def point_inside_polygon(x,y,polygon):

  n = len(polygon)
  inside = False

  p1x,p1y = polygon[0]
  
  for i in range(n+1):
    
    p2x,p2y = polygon[i % n]
    
    if y > min(p1y,p2y):
      if y <= max(p1y,p2y):
        if x <= max(p1x,p2x):
          if p1y != p2y:
            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
            if p1x == p2x or x <= xinters:
              inside = not inside
    p1x,p1y = p2x,p2y

  return inside

# ======================================================================
