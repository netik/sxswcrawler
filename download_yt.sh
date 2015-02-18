#!/bin/bash
#
# Downloads all of the videos in the youtube queue. 
# Converts mp4s to mp3s
#

SUFFIX=ad

for url in `cat data/download_queue.txt | grep youtube | egrep -v ^\# | awk '{ print $NF }'`; 
do 

IFS=$(echo -en "\n\b")
  cd "music/yt"
  echo $url
  youtubedown --fmt 18 $url 

  FN=`ls *.mp4 | head -1`
  FNMP3=`echo ${FN} | sed 's/.mp4$/.mp3/'`

  ffmpeg -y -i "${FN}" -f mp3 -ab 192000 -vn "${FNMP3}"

  rm "${FN}"

done
