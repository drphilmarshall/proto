#!/usr/bin/env python
# ======================================================================

# Globally useful modules:

import numpy,sys,os,getopt,atpy

import proto

# BUG: this import fails
from astrometry.libkd.spherematch import *
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "/Users/marshallp/work/astrometry/python/astrometry/libkd/spherematch.py", line 1, in <module>
#     from astrometry.libkd import spherematch_c
# ImportError: dlopen(/Users/marshallp/work/astrometry/python/astrometry/libkd/spherematch_c.so, 2): Symbol not found: _dl_append
#   Referenced from: /Users/marshallp/work/astrometry/python/astrometry/libkd/spherematch_c.so
#   Expected in: flat namespace
#  in /Users/marshallp/work/astrometry/python/astrometry/libkd/spherematch_c.so

# ======================================================================

def proto_apcluster(argv):

  USAGE = """
  NAME
    proto_apcluster.py

  PURPOSE
    Read in a catalogue, including ra and dec, and find clusters of objects.
    Write these clustered objects out in a new catalogue, preserving old 
    information.

  COMMENTS
    Works best when clusters are well-separated, as there is no iteration 
    of clusters. 
    
  USAGE
    proto_apcluster.py [flags] [options]  radius  catfile

  FLAGS
          -h             Print this message
          -v             Be verbose

  INPUTS
          radius         Separation of objects, in arcsec
          catfile        Object catalog (plain text)

  OPTIONAL INPUTS
          -o newfile     Name of output catalog [clusters.fits]
  OUTPUTS
          newfile        Catalog of clustered objects

  EXAMPLES

    proto_apcluster.py -v -o ref_lenses.fits  5  ref_lensedqsos.fits
  
  
  DEPENDENCIES
    astrometry,atpy
  
  BUGS

  HISTORY
    2010-08-17 started Marshall (Oxford)      
  """

  # --------------------------------------------------------------------

  try:
      opts, args = getopt.getopt(argv, "hvo:", ["help","verbose","output="])
  except getopt.GetoptError, err:
      # print help information and exit:
      print str(err) # will print something like "option -a not recognized"
      print USAGE
      return

  vb = False
  output = 'clusters.fits'
  for o,a in opts:
      if o in ("-v", "--verbose"):
          vb = True
      elif o in ("-h", "--help"):
          print USAGE
          return
      elif o in ("-o", "--output"):
          output = a
      else:
          assert False, "unhandled option"
   
  if len(args) == 2 :
      radius = float(args[0])
      degrad = radius/3600.0
      input = args[1]
      if vb: 
        print " "
        print "Making catalog of clusters of objects separated by under",radius,"arcsec"
        print "from the file:",input
        print "The output file will be:",output
  else :
      print USAGE
      return

  # --------------------------------------------------------------------

  # Read in table:

  t = atpy.Table(input,type='fits')
  
  # Add an empty column, for the cluster ID:
  
  t.add_empty_column('clusID', numpy.int32)

  # Extract ra and dec, and call matching routine:

#   indices,dists = match_radec(t.ra,t.dec, t.ra,t.dec, degrad, notself=True)
  N = len(t)
  xy = numpy.append(t.ra,t.dec).reshape(2,N).T
  indices,dists = match(xy,xy, degrad, notself=True)

  # Now loop through indices, pulling together clusters and filling up 
  # the clusIDs, starting from 1:
  
  clustered = numpy.unique(indices[:,:].reshape(2*len(indices)))
  
  ID0 = 100000
  ID = ID0 + 1
  for i in clustered:
    # Find matches involving ith clustered object:
    a = numpy.where(indices[:,0] == i)
    b = numpy.unique(indices[a[0],:].reshape(2*len(a[0])))
    if vb: print ID,b
    # Set these objects to have the current cluster ID:
    t.clusID[b] = ID
    ID += 1
  
  # Check clustered objects are in clusters:
  
  Nclusters = len(numpy.unique(t.clusID[numpy.where(t.clusID > 0)[0]]))

  if vb: print "Found",Nclusters,"clusters of objects"

  # Create cluster table, that only contains those objects that made it 
  # into a cluster:
  
  c = t.rows(clustered)
  
  # Write out cluster table, after sorting by clusID:

  c.sort('clusID')

  if vb: print "Writing objects to file, with cluster IDs..."
  c.write(output,type='fits')
    
  return

# ======================================================================

# If called as a script, the python variable __name__ will be set to 
# "__main__" - so test for this, and execute the main program if so.
# Writing it like this allows the function to be called
# from the python command line as well as from the unix prompt.

if __name__ == '__main__':
  proto_apcluster(sys.argv[1:])

# ======================================================================


