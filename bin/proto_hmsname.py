#!/usr/local/misc/python/Python-2.7.2/bin/python
import sys
if len(sys.argv) != 3:
  print "proto_hmsname.py file project"
  print "file is a text table of hms format radecs. Project is a string that will be added to source names."
  sys.exit(1)
sys.path.append('/a41217h/morganson/bin/')

import proto_utils
proto_utils.hmsname(sys.argv[1],sys.argv[2])
