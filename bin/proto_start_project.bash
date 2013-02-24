#!/bin/bash
#===============================================================================
#+
# NAME:
#   proto_start_project.bash
#
# PURPOSE:
#   Start a search for rare objects: set up workspace, download postage stamps,
#   organise stuff as it comes in.
#
# COMMENTS:
# 
#   Starting point is an initial catalog containing ra, dec and optionally a 
#   name. This script does three things:
#      1) Build a directory structure to hold all data
#      2) Call pstamp and start downloading postage stamp images
#      3) Make small catalogs of PS1 detections to correspond to the images
#   
#   Here's the plan for the directory structure - note the assumption of a correctly
#   set up environment:
#
#      $PS1QLS_DATA_DIR/$search/catalogs  - contains search catalog, and then refinements
#                                           including rabin, decbin of each target
# 
#      $PS1QLS_DATA_DIR/$search/$skypatch/$target - contains all products for each target
#
#   Nb. skypatches will be "square" and named ra1_dec1_ra2_dec2, eg 330_-20_340_-10
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
#   catalog       Catalog of targets, plain text.      
#
# OPTIONAL INPUTS:
#   -c            convert input from hms to radec (required if input is hms)
#   -f            select filters that will be examined [grizy]
#   -p            change project name [PSO] 
#   -s            skypatch width in degrees [30]
#   -w            stamp width in arcseconds [10]
#
# OUTPUTS:
#
# EXAMPLES:
#   proto_start_project.bash -w 20 examples/SDSSknownlenses.txt -p KNOWNLENSES
#
# BUGS:
#    - very large searches should have initial catalogs in FITS table format - in which case this script
#      should really be in python.
#    - Does not add lsd catalogs
# 
# REVISION HISTORY:
#   2012-07-04  started Marshall and Morganson (MPIA)
#   2012-07-20  made half functional by Morganson (MPIA)
#-
#===============================================================================
# All files created should be group-writable:
# umask 112

# Default options:
convert=0
project=PSO
help=0
vb=0
size=30
filter=grizy
stack=0
all=0
width=10

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

  if [ "$1" == "-c" ]; then
    convert=1
    tag=1
  fi
  if [ "$1" == "--convert" ]; then
    convert=1
    tag=1
  fi

  if [ "$1" == "-f" ]; then
    shift
    filter=$1
    tag=1
  fi
  if [ "$1" == "--filter" ]; then
    shift
    filter=$1
    tag=1
  fi

  if [ "$1" == "-p" ]; then
    shift
    project=$1
    tag=1
  fi
  if [ "$1" == "--project" ]; then
    shift
    project=$1
    tag=1
  fi

  if [ "$1" == "-s" ]; then
    shift
    size=$1
    tag=1
  fi
  if [ "$1" == "--size" ]; then
    shift
    size=$1
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

  if [ "$1" == "-w" ]; then
    shift
    width=$1
    tag=1
  fi
  if [ "$1" == "--width" ]; then
    shift
    width=$1
    tag=1
  fi

  if [ "$1" == "-A" ]; then
    shift
    all=1
    tag=1
  fi
  if [ "$1" == "--All" ]; then
    shift
    all=1
    tag=1
  fi

  if [ "$1" == "-S" ]; then
    shift
    stack=1
    tag=1
  fi
  if [ "$1" == "--Stack" ]; then
    shift
    stack=1
    tag=1
  fi

  if [ $tag -eq 0 ]; then
    INPUT=$1 
  fi
  shift
done

if [ $help -eq 1 ]; then
  echo "proto_start_project.bash coord.txt"
  echo "coord.txt is either a two column 'ra dec' table"
  echo "All columns n > 2 are ignored"
  echo "-c --convert: convert to from 'hms+dms' format to decimal radec (required if you use hms table)"
  echo "-f --filter: select filters that will be examined [grizy]"
  echo "-h --help: displays this menu"
  echo "-p --project: specifies project name (PSO)"
  echo "-s --size: size of sky region (30 degrees)"
  echo "-w --width: stamp width in arcseconds [10]"
  echo "-A --All: get all images of candidate"
  echo "-S --Stacks: get stacked images of candidates"
  exit
fi

# Formatting project catalog
mkdir -p $project
MAINCAT=$project/$project.txt
if [ -e $MAINCAT ]; then
  echo "$MAINCAT already exists. Not remaking."
else  
  if [ $convert -eq 1 ]; then
    if [ $vb -eq 1 ]; then echo "Converting hms to degrees."; fi
    proto_hms2deg.py $INPUT
    extension="${INPUT##*.}"
    filename="${INPUT%.*}"
    mv ${filename}_deg.$extension $project/$project.radec
  else
    cat $INPUT | awk '{ print $1, $2 }' > $project/$project.radec
  fi
  
  if [ $vb -eq 1 ]; then echo "Making $MAINCAT."; fi
  proto_degname.py $project/$project.radec $project
  cat $project/${project}_name.radec | awk '{ printf("%s %s %s '$project'_%i_%i\n",$1,$2,$3,$1-$1%'$size',$2-$2%'$size'-'$size'*($2<0)) }' > $project/${project}_dir.radec
  proto_deg2hms.py $project/${project}.radec
  rm $project/${project}_name.radec $project/$project.radec
  proto_hmsname.py $project/${project}_hms.radec $project
  paste $project/${project}_dir.radec $project/${project}_hms_name.radec > $MAINCAT
  rm $project/${project}_dir.radec $project/${project}_hms_name.radec $project/${project}_hms.radec 
fi

HOMEDIR=`pwd`
nlines=`cat $MAINCAT | wc -l`
for num in `seq $nlines`; do
  line=`cat $MAINCAT | head -n $num | tail -n 1`
  radec=`echo $line | cut -d ' ' -f 1-2`
  name=`echo $line | cut -d ' ' -f 3`
  dir=`echo $line | cut -d ' ' -f 4`
  OBJDIR=$project/$dir/$name
  mkdir -p $OBJDIR
  OBJRADEC=$OBJDIR/$name.radec
  echo $radec > $OBJRADEC
  cd $OBJDIR
  w1=$((4 * $width))
  w2=$((5 * $width))
  STACKFITS=${name}_stack.fits
  ALLFITS=${name}_V3.fits
  if [ $stack ]; then 
    if [ -e $STACKFITS ]; then 
      echo "$STACKFITS already exists. Not remaking (or submitting new stamps)."	  
    else  
      pstamp.bash -a -f $filter -n $w1 -o ${name}_STACK -P -C -W -U -r LAP.ThreePi.20120706%final% -d stack -c  $name.radec
    fi
  fi

  if [ $all ]; then
    if [ -e $ALLFITS ]; then 
      echo "$ALLFITS already exists. Not remaking (or submitting new stamps)."	  
    else  
      pstamp.bash -a -f $filter -n $w2 -o ${name}_V3 -P -C -W $name.radec
    fi
  fi
  cd $HOMEDIR 
done


#===============================================================================
