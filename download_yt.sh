#!/bin/bash
#
# Download all of the files possible in 
#

SUFFIX=ad

for url in `cat ../data/queue-youtube.${SUFFIX} | egrep -v ^\# | awk '{ print $NF }'`; 
do 

IFS=$(echo -en "\n\b")
  cd "/Volumes/Field Photos/sxsw_youtube_dl"
  echo $url
  youtubedown --fmt 18 $url 

  FN=`ls *.mp4 | head -1`
  FNMP3=`echo ${FN} | sed 's/.mp4$/.mp3/'`

  ffmpeg -y -i "${FN}" -f mp3 -ab 192000 -vn "${FNMP3}"

  rm "${FN}"

done
