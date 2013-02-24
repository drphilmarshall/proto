#!/bin/bash

# Setting defaults
help=0
db=ucal_magsqw
format=fits
output=minicat
radius=1
screen=0
setupfile=/a41217d5/LSD/lsd_environment_better
text=0
nlines=1
input=0
nondecimal=0
fields=0

narg=0
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

  if [ "$1" == "-d" ]; then
    shift
    db=$1
    tag=1
  fi
  if [ "$1" == "--database" ]; then
    shift
    db=$1
    tag=1
  fi

  if [ "$1" == "-f" ]; then
    shift
    fields=$1
    tag=1
  fi
  if [ "$1" == "--fields" ]; then
    shift
    fields=$1
    tag=1
  fi

  if [ "$1" == "-i" ]; then
    shift
    input=$1
    tag=1
  fi
  if [ "$1" == "--input" ]; then
    shift
    input=$1
    tag=1
  fi

  if [ "$1" == "-l" ]; then
    shift
    setupfile=$1
    tag=1
  fi
  if [ "$1" == "--lsd-file" ]; then
    shift
    setupfile=$1
    tag=1
  fi

  if [ "$1" == "-n" ]; then
    nondecimal=1
    tag=1
  fi
  if [ "$1" == "--nondecimal" ]; then
    nondecimal=1
    tag=1
  fi

  if [ "$1" == "-o" ]; then
    shift
    output=$1
    tag=1
  fi
  if [ "$1" == "--output" ]; then
    shift
    output=$1
    tag=1
  fi

  if [ "$1" == "-r" ]; then
    shift
    radius=$1
    tag=1
  fi
  if [ "$1" == "--radius" ]; then
    shift
    radius=$1
    tag=1
  fi

  if [ "$1" == "-s" ]; then
    screen=1
    tag=1
  fi
  if [ "$1" == "--screen" ]; then
    screen=1
    tag=1
  fi

  if [ "$1" == "-t" ]; then
    text=1
    tag=1
  fi
  if [ "$1" == "--text" ]; then
    text=1
    tag=1
  fi
  if [ $tag -eq 0 ]; then
    INPUT=( ${INPUT[*]} $1 )
    narg=$(( $narg + 1 ))
  fi

  shift
done


# Shooting out help if no input entered of -r used

if [ $help == 1 ]; then
  echo "proto_minicat.sh ra dec"
  echo "where ra and dec are actual numbers"
  echo "The program produces and executes .lsd command file, which contains a single lsd command; the minicat itself is then stored in the desired format."
  echo "-d --database sets database to averages, ps1_det, ps1_exp or sdss (default averages)"
  echo "-f --fields      sets fields to be retrieved [*]"
  echo "-i --input       sets input file, must be three collumn name, ra, dec"
  echo "-l --lsd-file    sets settings file for LSD (default /a41217d5/LSD/lsd_environment_better)"
  echo "-n --nondecimal  sets input ra dec to nondecimal (hr:m:s d:m:s) format [decimal]"
  echo "-o --output      sets output file name, excluding the extension [minicat]"
  echo "-r --radius      sets radius, in arcseconds [1]"
  echo "-s --screen      sets output to to print to screen [fits]"
  echo "-t --text        sets output to text file [fits]"

  exit
fi

if [ $radius -lt 0 ]; then
  echo "radius must be greater than 0"
  exit
fi

if [ $radius -gt 10000 ]; then
  echo "radius must be less than 10000"
  exit
fi

#converting radius to degrees
radius=`echo $radius | awk '{ print $1/3600.0 }'`

if [ $screen == 0 ]; then
  if [ -e $output ]; then
    echo "$output already exists. Exiting"
    exit
  fi
fi

if [ -e $setupfile ];then
  source $setupfile
else
  echo "ERROR: $setupfile does not exist. Specify an LSD setup file manually."
  exit
fi

dbexists=0
num=0
ndirs=`echo $LSD_DB | sed 's/:/ /g' | wc -w`

while [ $num -lt $ndirs ]; do
  num=$(( $num + 1 ))
  dbdir=`echo $LSD_DB | sed 's/:/\t/g' | awk '{ print $'"$num"' }'`/$db
  echo $dbdir
  if [ -e $dbdir ]; then dbexists=1; fi
done

if [ $dbexists -eq 0 ]; then
  echo "$db not found in $LSD_DB."
  exit
fi

if [ $input == 0 ]; then
  if [ $narg != 2 ]; then
    echo "Must give and ra and dec and no other input other than tags listed in the help."
    exit
  fi
  ra=${INPUT[0]}
  dec=${INPUT[1]}
else
  nlines=`cat $input | wc -l`
  if [ $nlines == 0 ]; then
    echo "Must give valid input file."
    exit
  fi
fi

#Setting output option
outputoption=""
if [ $screen == 0 ]; then
  if [ $text == 1 ]; then
    outputoption="--format=text --output=$output.txt"
  else
    outputoption="--format=fits --output=$output.fits"
  fi
fi

rm -f $output.lsd

for num in `seq $nlines`; do
  if [ $input != 0 ]; then
    blah=`cat $input | head -n $num | tail -n 1`
    output2=`echo $blah | cut -f 1 -d ' '`
    ra=`echo $blah | cut -f 2 -d ' '`
    dec=`echo $blah | cut -f 3 -d ' '`    
    outputoption=""
    if [ $screen == 0 ]; then
      if [ $text == 1 ]; then
        outputoption="--format=text --output=$output2.txt"
      else
        outputoption="--format=fits --output=$output2.fits"
      fi
    fi
  fi
  if [ $nondecimal == 1 ]; then
	  ra=`echo $ra | sed 's/:/ /g' | awk '{ printf("%f",15.0*($1+($2+$3/60.0)/60.0)); }'`
	  dec=`echo $dec | sed 's/:/ /g' | awk '{ printf("%f",$1+($2+$3/60.0)/60.0*(( $1 > 0 ) *2 -1)); }'`    
  fi 
  fail=`echo "$ra $dec" | awk '{if ($1 < 0 || $1 > 360 || $2 < -90 || $2 > 90) print 1; else print 0}'`
  if [ $fail == 1 ]; then
    echo "ERROR: ra, dec outside allowable range: $ra, $dec"
    exit
  fi
  if [ $fields == 0 ]; then
    echo "lsd-query $outputoption --bounds='beam($ra, $dec, $radius)' 'select * from $db'" >> $output.lsd
  else
    echo "lsd-query $outputoption --bounds='beam($ra, $dec, $radius)' 'select $fields from $db'" >> $output.lsd
  fi
done

#actually call lsd
source $output.lsd
