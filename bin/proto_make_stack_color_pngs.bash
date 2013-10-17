#!/bin/bash
#===============================================================================
#+
# NAME:
#   proto_make_stack_color_pngs.bash
#
# PURPOSE:
#   Use HumVI to make gri color PNG images of all targets in a search, using 
#   the stacked images.
#
# COMMENTS:
#   Script is to be run in a project directory, or to be given a project name.
#   The workhorse script is proto_make_color_png.bash, which actually calls
#   HumVI with the standard settings.
#
# INPUTS:
#
# OPTIONAL INPUTS:
#   -i    choose just one object to make a PNG for [all]
#   -f    select filters that will be combined [gri]
#   -p    project name [pwd] 
#
# OUTPUTS:
#
# EXAMPLES:
#   proto_make_stack_color_pngs.bash -p kbs-stripe82 -f gri -i 52
#
# BUGS:
# 
# REVISION HISTORY:
#   2013-10-17  started Marshall (KIPAC)
#-
#===============================================================================
# All files created should be group-writable:
# umask 112

# Default options:
project = `pwd`
help = 0
vb = 0
filters = 'gri'
index = 'all'

# ------------------------------------------------------------------------------

# Getting user options
if [ $# -eq 0 ]; then
  help = 1
fi

while (( "$#" )); do
  tag = 0

  if [ "$1" == "-h" ]; then
    help = 1
    tag = 1
  fi
  if [ "$1" == "--help" ]; then
    help = 1
    tag = 1
  fi

  if [ "$1" == "-f" ]; then
    shift
    filters = $1
    tag = 1
  fi
  if [ "$1" == "--filters" ]; then
    shift
    filters = $1
    tag = 1
  fi

  if [ "$1" == "-i" ]; then
    shift
    index = $1
    tag = 1
  fi
  if [ "$1" == "--index" ]; then
    shift
    index = $1
    tag = 1
  fi

  if [ "$1" == "-p" ]; then
    shift
    project = $1
    tag = 1
  fi
  if [ "$1" == "--project" ]; then
    shift
    project = $1
    tag = 1
  fi

  if [ "$1" == "-v" ]; then
    vb = 1
    tag = 1
  fi
  if [ "$1" == "--verbose" ]; then
    vb = 1
    tag = 1
  fi

  if [ $tag -eq 0 ]; then
    INPUT = $1 
  fi
  shift
  
done

if [ $help -eq 1 ]; then
  more `which $0`
  exit
fi

# ------------------------------------------------------------------------------

# Read target names from project catalog, find FITS files, and pass to HumVI:

chdir $project
MAINCAT = $project.txt

if [ -e $MAINCAT ]; then
  echo "$MAINCAT exists - reading targets from it."
else  
  echo "$MAINCAT does not exist, exiting"
  exit
fi

if [ $index -eq 'all' ]; then
  ntargets = `cat $MAINCAT | wc -l`
  index = `seq $ntargets`
else
  ntargets = 1
fi

for num in $index; do

  line = `cat $MAINCAT | head -n $num | tail -n 1`
  radec = `echo $line | cut -d ' ' -f 1-2`
  name = `echo $line | cut -d ' ' -f 3`
  dir = `echo $line | cut -d ' ' -f 4`

  IMAGEDIR = ${dir}/${name}/${name}_STACK
  
  PNG = ${dir}/${name}/${name}_STACK_${filters}.png
  
  echo "Located FITS images:"
  ls *unconv.fits

  if [ $filters -eq 'gri' ]; then
  
     set red   = *_i_*unconv.fits
     set green = *_r_*unconv.fits
     set blue  = *_g_*unconv.fits
     
     proto_make_color_png.bash -f $filters $red $green $blue -o $PNG
     
  else
  
    echo "ERROR: unrecognised filter combination $filters"
    exit
 
  fi      

done


#===============================================================================
