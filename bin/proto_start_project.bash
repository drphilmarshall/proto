#!/bin/bash
#===============================================================================
#+
# NAME:
#   proto_start_project.bash
#
# PURPOSE:
#   Start a search for rare objects.   
#
# COMMENTS:
# 
#   Starting point is an initial catalog containing ra, dec and optionally a 
#   name. This script does three things:
#      1) Build a directory structure to hold all data
#      2) Call pstamp and start downloading postage stamp images
#      3) Make small catalogs of PS1 detections to correspond to the images
#   
#   Here's the plan for the directory structure:
#
#      $PS1QLS_DATA_DIR/$search/catalogs  - contains search catalog, and then refinements
#                                           including rabin, decbin of each target
# 
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target - contains all products for each target
#
#   Nb. skypatches should be "square" and named ra1_dec1_ra2_dec2, eg 330_-20_340_-10
#   These can be of any size, with the patch width given as an argument to this script.
#   We need a lookup table with target ra,dec,target,skypatch, placed in catalogs.
# 
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target/raw  - downloaded from pstamp, with long names
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target/raw/*.fits     Science images
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target/raw/*.cmf      Detection catalogs
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target/raw/*.wt.fits  Variance images
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target/raw/*.psf      PSF images (?)
#
#   Nb. pstamp will download into a directory called morganson.20120702113542
#   or something - this needs emptying into raw and removing.
#
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target/cutouts - smaller cutouts, or links, 
#                                                           named $target_$mjd_$filter_sci[var].fits
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target/sex     - SExtractor outputs
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target/models  - LensTractor outputs
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target/www     - pngs,html etc
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target/log     - progress reports
#
#
# INPUTS:
#   field         IAU name of HAGGLeS field for which to prepare workspace     
#
# OPTIONAL INPUTS:
#   -w         skypatch width in degrees [10]
#
# OUTPUTS:
#
# EXAMPLES:
#   proto_start_project.bash -w 20 SDSSknownlenses.txt
#
# BUGS:
#
#
# REVISION HISTORY:
#   2012-07-04  started Marshall and Morganson (MPIA)
#-
#===============================================================================
# All files created should be group-writable:
# umask 112

# Default options:

set help = 0
set vb = 0
set w = 10

# ------------------------------------------------------------------------------

FINISH:
  
#===============================================================================
