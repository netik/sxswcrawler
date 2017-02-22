#!/bin/bash
#
# stage1: download all of the index files, crawl them for showcases.
#         then download the event pages.
#
./stage1.py > data/crawl_log.txt

# stage 1.5: link the valid HTML files in one directory for easy parsing.
( cd cache; mkdir events; find 2017 -name \*.html -exec ln -s ../{} events \; )

# stage 2: find music links inside of the event files
./stage2.py > data/queue.txt

# none.txt is the failed log for later. 
cat data/queue.txt | grep none > data/none.txt

# these are the files we can actualy download
cat data/queue.txt | grep -v none > data/download_queue.txt

echo "total events:"
cat data/queue.txt | awk '{ print $2 } ' | sort | uniq -c 

# lastly, make sure we have a download dir
if [ ! -d music ]; then
  mkdir music
  mkdir music/sx
  mkdir music/sc
  mkdir music/yt
fi

echo
echo "Now run the download_{sc,sx,yt} scripts as needed." 
echo 
echo "This software is for personal use only. "
echo "Respect the copyrights of the artists."
echo
