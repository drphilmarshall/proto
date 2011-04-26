#!/usr/bin/env python
# ======================================================================

# Globally useful modules, imported here and then accessible by all
# functions in this file:

import numpy,getopt,pyfits

# Global variables, used by all functions in this file:

# ======================================================================

def proto_xxxx(argv):

  USAGE = """
  NAME
    proto_xxxx.py

  PURPOSE
    xxxx xxxx xxxx.

  USAGE
    oguri2imsim.py [flags] [options] RA DEC lnsID

  FLAGS
    -x              xxxxx xxxxx
    -x              xxxxx xxxxx

  INPUTS:
    xxx             xxxxx xxxxx
    xxx             xxxxx xxxxx

  FLAGS:
    -x              xxxxx xxxxx
    -x              xxxxx xxxxx

  OPTIONAL INPUTS:
    -x xxxx         xxxxx xxxxx
    -x xxxx         xxxxx xxxxx
    -h --help

  OUTPUTS:
    xxx             xxxxx xxxxx
    xxx             xxxxx xxxxx

  EXAMPLES:
    xxx xxxxxx xxxx:
    >> proto_xxxx.dvo -x xxx -x xxxx

  DEPENDENCIES:
    xxxx            xxxxx xxxxx

  COMMENTS:
    - xxx xxxx xxx xxxx
    - xxx xxxx xxx xxxx

  BUGS:
    - xxx xxxx xxx xxxx
    - xxx xxxx xxx xxxx

  REVISION HISTORY:
    2011-04-XX  started Xxxxxxx (MPIA)
  """

  # --------------------------------------------------------------------

  try:
      opts, args = getopt.getopt(argv, "hvc:",["help","verbose","catalog="])
  except getopt.GetoptError, err:
      # print help information and exit:
      print str(err) # will print something like "option -a not recognized"
      print USAGE
      return

  catalog = 'dummy'
  vb = False
  for o,a in opts:
      if o in ("-v", "--verbose"):
          vb = True
      elif o in ("-h", "--help"):
          print USAGE
          return
      elif o in ("-c", "--catalog"):
          catalog = a
      else:
          assert False, "unhandled option"
   
  # --------------------------------------------------------------------

  if vb: print "All done."

  # --------------------------------------------------------------------

  return

# ======================================================================

# If called as a script, the python variable __name__ will be set to 
# "__main__" - so test for this, and execute the main program if so.
# Writing it like this allows the function proto_xxx to be called
# from the python command line as well as from the unix prompt.

if __name__ == '__main__':
  proto_xxx(sys.argv[1:])

# ======================================================================


