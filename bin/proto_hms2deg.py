#!/usr/local/misc/python/Python-2.7.2/bin/python
import sys
if len(sys.argv) != 2:
  print "proto_hms2deg.py file"
  print "file is a text table of hms format radecs"
  sys.exit(1)
sys.path.append('/a41217h/morganson/bin/')

import proto_utils
proto_utils.hms2deg(sys.argv[1])
