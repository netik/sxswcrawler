#!/bin/bash
#
# fire off stage one to download the header pages and the detail pages. 
#

./stage1.py > data/crawl_log.txt

( cd cache; mkdir events; find 2016 -name \*.html -exec mv {} events \; )

# now run stage2.py !
./stage2.py > data/queue.txt

# move a bunch of shit around so we have separated logs 

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
