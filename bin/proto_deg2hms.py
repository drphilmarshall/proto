#!/usr/local/misc/python/Python-2.7.2/bin/python
import sys
if len(sys.argv) != 2:
  print "proto_deg2hms2hms.py file"
  print "file is a text table of decimal ra and decs"
  sys.exit(1)
sys.path.append('/a41217h/morganson/bin/')

import proto_utils
proto_utils.deg2hms(sys.argv[1])
