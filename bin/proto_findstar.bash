#!/bin/bash

# Setting defaults
help=0
phot=0
db=averages
format=text
output=findstar
radius=150
screen=0
setupfile=/a41217d5/LSD/lsd_environment_better
text=0
nlines=1
input=0
nondecimal=0
filter=3
guide=1
mag=16
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
    filter=$1
    tag=1
  fi
  if [ "$1" == "--filter" ]; then
    shift
    filter=$1
    tag=1
  fi
 
  if [ "$1" == "-g" ]; then
    shift
    guide=$1
    tag=1
  fi
  if [ "$1" == "--guide" ]; then
    shift
    guide=$1
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

  if [ "$1" == "-m" ]; then
    shift
    mag=$1
    tag=1
  fi
  if [ "$1" == "--mag" ]; then
    shift
    mag=$1
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

  if [ "$1" == "-p" ]; then
    phot=1
    tag=1
  fi
  if [ "$1" == "--phot" ]; then
    phot=1
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

  if [ $tag -eq 0 ]; then
    INPUT=( ${INPUT[*]} $1 )
    narg=$(( $narg + 1 ))
  fi

  shift
done


# Shooting out help if no input entered of -r used

if [ $help == 1 ]; then
  echo "proto_findstar.sh ra dec"
  echo "where ra and dec are actual numbers"
  echo "The program produces and executes .lsd command file, which contains a single lsd command; the minicat itself is then stored in the desired format."
  echo "-d --database sets database to averages, ps1_det, ps1_exp or sdss (default averages)"
  echo "-f --filter      sets filters to be retrieved (12345 = grizy) [3]"
  echo "-g --guide       sets sets guide star to be the nth clostest [1]"
  echo "-i --input       sets input file, must be three collumn name, ra, dec"
  echo "-l --lsd-file    sets settings file for LSD (default /a41217d5/LSD/lsd_environment_better)"
  echo "-m --mag         sets limiting magnitude for star [16]"
  echo "-n --nondecimal  sets input ra dec to nondecimal (hr:m:s d:m:s) format [decimal]"
  echo "-o --output      sets output file name, excluding the extension [minicat]"
  echo "-p --phot        sets photometry to 1 so that source photometry in included [0]"
  echo "-r --radius      sets radius, in arcseconds [240]"
  echo "-s --screen      sets output to to print to screen [text files]"

  exit
fi

fields="ra,dec,median($filter) FROM $db WHERE (nmag_ok($filter) > 1) & (median($filter) < $mag)"
fields2="ra, dec, median(2), err(2), median(3), err(3), median(4), err(4) FROM $db WHERE (nmag_ok($filter) > 1)"

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
ndirs=`echo $LSD_DB | sed 's/:/ /' | wc -w`

while [ $num -lt $ndirs ]; do
  num=$(( $num + 1 ))
  dbdir=`echo $LSD_DB | sed 's/:/\t/' | awk '{ print $'"$num"' }'`/$db
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

rm -f $output.radec
rm -f $output.temp

for num in `seq $nlines`; do
  if [ $input != 0 ]; then
    blah=`cat $input | head -n $num | tail -n 1`
    output2=`echo $blah | cut -f 1 -d ' '`
    ra=`echo $blah | cut -f 2 -d ' '`
    dec=`echo $blah | cut -f 3 -d ' '`    
  fi
  if [ $nondecimal == 1 ]; then
    ra=`echo $ra | sed 's/:/ /g' | awk '{ print 15.0*($1+($2+$3/60.0)/60.0) }'`
    dec=`echo $dec | sed 's/:/ /g' | awk '{ print $1+($2+$3/60.0)/60.0*(( $1 > 0 ) *2 -1) }'`
  fi
  radecmag=`lsd-query --bounds="beam($ra, $dec, 0.0002)" "select $fields2" | head -n 2 | tail -n 1`
  ra=`echo $radecmag | awk '{ print $1 }'`
  dec=`echo $radecmag | awk '{ print $2 }'`
  magn=`echo $radecmag | awk '{ print $3, $4, $5, $6, $7, $8 }'`
  if [ $nondecimal == 1 ]; then
    ran=$ran
    decn=$decn
    ra=`echo $ra | sed 's/:/ /g' | awk '{ print 15.0*($1+($2+$3/60.0)/60.0) }'`
    dec=`echo $dec | sed 's/:/ /g' | awk '{ print $1+($2+$3/60.0)/60.0*(( $1 > 0 ) *2 -1) }'`
  else
    ran=`radecconvert 02 $ra $dec | awk '{ print $1 }'` 
    decn=`radecconvert 02 $ra $dec | awk '{ print $2 }'`
    echo $ran $decn 
  fi 
  fail=`echo "$ra $dec" | awk '{if ($1 < 0 || $1 > 360 || $2 < -90 || $2 > 90) print 1; else print 0}'`
  if [ $fail == 1 ]; then
    echo "ERROR: ra, dec outside allowable range: $ra, $dec"
    exit
  fi
  if [ $phot == 1 ]; then
    echo $magn
  else
    magn="0 0 0 0 0 0"
  fi
  echo $guide
  lsd-query --bounds="beam($ra, $dec, $radius)" "select $fields" | grep -v '#' | grep -v 'ec' | awk '{ dra=($1-'"$ra"')*cos(017453*'"$dec"');ddec=($2-'"$dec"');d=sqrt(dra**2+ddec**2); print d, $1, $2, $3, 3600.0*dra, 3600.0*ddec }' | sort -g | head -n $guide | tail -n 1 | awk '{ print "'"$output2"'", "'"$ran"'", "'"$decn"'", "'"$magn"'",$2, $3, $4, $5, $6 }' >> $output.radec 
  echo $guide
done

for num in `seq $nlines`; do
  cat $output.radec | head -n $num | tail -n 1 | awk '{ print $10, $11 }'
  radecconvert 02 `cat $output.radec | head -n $num | tail -n 1 | awk '{ print $10, $11 }'` >> $output.temp
done

paste $output.radec $output.temp | awk '{ print $1, $2, $3, $4, $5, $6, $7, $8, $9, $15, $16, $12, $13, $14 }' > $output.star

command1="ds9 -geometry 800x800 -view panner no -view buttons no -view magnifier no -view info no -wcs align yes "
command2=" -zscale -view colorbar no -zoom 1 -regions "
command3=" -regions select all -regions width 3 -regions color red -regions select none -invert -saveimage jpeg "
command4=" -exit"
rm -f $output.ds9

for num in `seq $nlines`; do
  blah=`cat $input | head -n $num | tail -n 1`
  output2=`echo $blah | cut -f 1 -d ' '`
  fits=`echo $num | awk '{ print 10000+$1"15.fits" }'`

  echo "physical; compass 200 200 50" > $output2.reg
  cat $output.star | head -n $num | tail -n 1 | awk '{ print "J2000; ruler", $2, $3, $10, $11, "# ruler=arcsec" }' >> $output2.reg
  echo $command1$fits$command2$output2.reg$command3$output2.jpg$command4 >> $output.ds9
done  
