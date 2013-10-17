#!/bin/bash
#===============================================================================
#+
# NAME:
#   proto_make_color_png.bash
#
# PURPOSE:
#   Simple wrapper for HumVI compose.py, to make a color PNG image.
#
# COMMENTS:
#
# INPUTS:
#
# OPTIONAL INPUTS:
#   -f    select filters that will be combined [gri]
#   -o    output PNG filename [color.png] 
#
# OUTPUTS:
#
# EXAMPLES:
#   proto_make_color_png.bash -f gri r.fits g.fits b.fits -o rgb.png
#
# BUGS:
# 
# REVISION HISTORY:
#   2013-10-17  started Marshall (KIPAC)
#-
#===============================================================================

# Default options:
help=0
vb=0
filters=gri
PNG=color.png

# ------------------------------------------------------------------------------

# Getting user options
if [ $# -eq 0 ]; then
  help=1
fi

while (( "$#" )); do
  tag=0

  if [ "$1" == "-h" ]; then
    help=1
    tag=1
  fi
  if [ "$1" == "--help" ]; then
    help=1
    tag=1
  fi

  if [ "$1" == "-f" ]; then
    shift
    filters=$1
    tag=1
  fi
  if [ "$1" == "--filters" ]; then
    shift
    filters=$1
    tag=1
  fi

  if [ "$1" == "-o" ]; then
    shift
    PNG=$1
    tag=1
  fi
  if [ "$1" == "--output" ]; then
    shift
    PNG=$1
    tag=1
  fi

  if [ "$1" == "-v" ]; then
    vb=1
    tag=1
  fi
  if [ "$1" == "--verbose" ]; then
    vb=1
    tag=1
  fi

  if [ $tag -eq 0 ]; then
    red=$1
    shift
    green=$1
    shift
    blue=$1 
  fi
  shift
  
done

if [ $help -eq 1 ]; then
  more `which $0`
  exit
fi

# ------------------------------------------------------------------------------


if [ $filters == 'gri' ]; then

   compose.py  -v -s 0.6,0.8,1.0 -z 0.0 -p 1.7,1e-8 -m -1.0  -o $PNG   $red $green $blue

else

  echo "ERROR: unrecognised filter combination $filters"
  exit

fi      

done


#===============================================================================
