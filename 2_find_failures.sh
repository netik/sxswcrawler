#!/bin/sh
# Run this only after 1_run_crawl.sh has finished

function dtcreate {
   if [ -f data/$1 ]; 
   then 
     rm data/$1
     touch data/$1
   fi
}

# generate the download work queues
echo "==="
echo "soundcloud in none state:"
   dtcreate "sc_missed.txt"

   for i in `cat data/none.txt | awk '{ print $1 }'`; 
   do
      grep -H soundcloud cache/events/`basename $i` | uniq >> data/sc_missed.txt
   done


echo
echo "==="
echo

echo "youtube in none state:"
   dtcreate "yt_missed.txt"

   for i in `cat data/none.txt | awk '{ print $1 }'`; 
   do
      grep -H youtube cache/events/`basename $i` | uniq >> data/yt_missed.txt
   done

echo
echo "==="
echo

echo "mp3 in none state:"
   dtcreate "mp3_missed.txt"
   for i in `cat data/none.txt | awk '{ print $1 }'`; 
   do
      grep -H mp3 cache/events/`basename $i` | uniq >> data/mp3_missed.txt
   done

echo
echo "==="
echo
