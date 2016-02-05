#!/bin/sh

# this path is relative to the scripts dir
SDGET="../../soundcloud-downloader.py"

# make sure we have a place to work.
if [ ! -d music/sc ]; then
  mkdir music/sc
fi

for URL in `cat data/queue.txt | grep soundcloud | awk '{ print $3 }'`; 
do
   /bin/echo -n ${URL}
   ( cd ./music/sc; ${SDGET} ${URL} ) >> data/sc_download_log.txt 
   echo
done
