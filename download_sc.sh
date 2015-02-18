#!/bin/sh

touch scdl-secondpull.log

SDCL="/Users/jna/Dropbox/sxsw_crawler/scripts/soundcloud-downloader.py"
SDGETURL="/Users/jna/Dropbox/sxsw_crawler/scripts/soundcloud-downloader.py -n"

for URL in `cat sc_detail_dedupe.log | egrep -v ^\# | awk -F\| '{ print $(NF-1) }'`;
do
   /bin/echo -n ${URL}
   /bin/echo ${URL} >> scdl-second-pull.log
   ${SDGETURL} ${URL}
   echo
done
