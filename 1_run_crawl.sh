#!/bin/bash
#
# download everything, produce statistics, and then dedupe in preperation for stage2.
#

function dtcreate {
   if [ -f data/$1 ]; 
   then 
     rm data/$1
     touch data/$1
   fi
}


# actully crawls sxsw , takes a long time.
#./stage1.py > data/crawl_log.txt
# ( cd cache; mkdir events; find 2015 -name \*.html -exec mv {} events \; )


cat data/crawl_log.txt | egrep ^cache/ > data/queue.txt

cat data/queue.txt | grep none > data/none.txt
cat data/queue.txt | grep -v none > data/download_queue.txt
cat data/queue.txt | awk '{ print $2 } ' | sort | uniq -c 

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
