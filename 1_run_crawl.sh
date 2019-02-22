#!/bin/bash
#
# stage1: download all of the index files, crawl them for showcases.
#         then download the event pages.
#
# can be skipped. 
./stage1.py > data/crawl_log.txt

# stage 2: find music links inside of the event files
./stage2.py > data/queue.txt

# none.txt is the failed log for later. 
cat data/queue.txt | grep " none" > data/none.txt

# these are the files we can actualy download
cat data/queue.txt | grep -v " none" > data/download_queue.txt

# and this is a map of artist to sound source based on the html
./create_mp3_map.py > data/map.txt

echo "total events:"
cat data/queue.txt | awk '{ print $2 } ' | sort | uniq -c
echo "----"
cat data/queue.txt | awk '{ print $2 } ' | sort | uniq -c | awk 'BEGIN { t = 0 } { t = t + $1 } END { print t }'

# lastly, make sure we have a download dir
if [ ! -d music ]; then
  mkdir music
  mkdir music/sx
  mkdir music/sc
  mkdir music/yt
fi

echo
echo "Now run:"
echo " ./download_mp3.py"
echo
echo "followed by the get_sc_data to get top tracks from soundcloud for soundcloud entries"
echo "then ./download_sc.py to download those songs"
echo "then ./download_yt.py for youtube which may be very messy/unreliable."
echo 
echo "This software is for personal use only. "
echo "Respect the copyrights of the artists."
echo
