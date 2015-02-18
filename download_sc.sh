#!/bin/sh

SDGET="../soundcloud-downloader.py"

for URL in `cat data/sc_data.txt | sort | uniq | egrep -v ^\# | awk -F\| '{ print $(NF-1) }'`;
do
   /bin/echo -n ${URL}
   ( cd music; ${SDGET} ${URL} ) 
   echo
done
