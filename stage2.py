#!/usr/bin/python
#
# Given our cache dir, let's go find all the music by parsing files
#

import io
import re
import os

BASE_URL='http://schedule.sxsw.com'
CACHE_DIR="cache/events"

ytRE = re.compile('(//www.youtube.com/embed/[a-zA-Z0-9_-]+)\'')
scRE = re.compile('(http(s)*://(www.)*soundcloud.com/.+)\" ')
mpRE = re.compile('(http://audio.sxsw.com/2016/mp3_by_artist_id/(\d+).mp3)')

for filename in os.listdir(CACHE_DIR):

    cachefn=os.path.join("cache/events",filename)
    dfh = open(cachefn, "r")
    detailpage = dfh.read()
    dfh.close()

    scM = scRE.search(detailpage)
    ytM = ytRE.search(detailpage)
    mpM = mpRE.search(detailpage)
    
    if scM != None: 
        scurl = scM.group(1)
        print "%s soundcloud %s" % (cachefn, scurl.replace('\'',''))
        
    if ytM != None:
        yturl = ytM.group(1)
        print "%s youtube http:%s" % (cachefn, yturl)
        
    if mpM != None:
        mpurl = mpM.group(1)
        print "%s mp3 %s" % (cachefn, mpurl)

    if scM == None and ytM == None and mpM == None:
        print "%s none" % cachefn
        



