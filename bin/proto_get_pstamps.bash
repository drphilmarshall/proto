#!/bin/bash
#===============================================================================
#+
# NAME:
#   proto_get_pstamps.bash
#
# PURPOSE:
#   Downloads postage stamps requested by proto_start_project.bash. Also puts 
#   them into appriate directories. 
#
# COMMENTS:
# 
#   Starting point is a directory produced by proto_start_project.bash. It is
#   assumed that you are in that directory, and that the directory was made 
#   correctly. This program waits for the postage stamp survey to make its
#   stamps. So this program could take a very long time, and should probably
#   be run within a screen. 
#   
# INPUTS:
#
# OPTIONAL INPUTS:
#
# OUTPUTS:
#
# EXAMPLES:
#   proto_get_pstamps.bash directory
#
# BUGS:
#    - is not parallelized and takes forever
# 
# REVISION HISTORY:
#   2012-08-22  started Morganson (MPIA)
#-
#===============================================================================
# All files created should be group-writable:
# umask 112

# Default options:
help=0
vb=0

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

  if [ "$1" == "-v" ]; then
    vb=1
    tag=1
  fi
  if [ "$1" == "--verbose" ]; then
    vb=1
    tag=1
  fi

  if [ $tag -eq 0 ]; then
    INPUT=$1 
  fi
  shift
done

if [ $help -eq 1 ]; then
  echo "proto_start_project.bash coord.txt"
  echo "-h --help: displays this menu"
  echo "-v --verbose: turns on verbosity"
  exit
fi

# Formatting project catalog
HOMEDIR=`pwd`
if [ ! -e $INPUT ]; then
  echo "$INPUT does not exist. Exiting."
  return 1 
fi

CAT=`echo $INPUT | sed 's\/\ \g' | awk '{ print $NF }'`
CAT=$CAT.txt

if [ ! -e ${INPUT}/$CAT ]; then
  echo "${INPUT}/$CAT does not exist. Exiting."
  return 1 
fi

cd $INPUT
HOMEDIR2=`pwd`
nlines=`cat $CAT | wc -l`
for num in `seq $nlines`; do
  DIR=`cat $CAT | head -n  $num | tail -n 1 | awk '{ print $4"/"$3 }'`
  cd $DIR
  for link in `cat *log`; do pstamp_retrieve.bash $link; done
  cd $HOMEDIR2 
done

cd $HOMEDIR

#===============================================================================
