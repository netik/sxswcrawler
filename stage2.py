#!/usr/bin/python
#
# stage2.py
#
# SXSW Post-crawl Parser
# J. Adams <jna@retina.net> 
# Last update 2/7/2016
#
# Once we've finished a crawl, this script will read the HTML cache
# and the to find music files. Output should be placed in
# data/queue.txt by the caller of this script
#


import io
import re
import os

BASE_URL='http://schedule.sxsw.com'
CACHE_DIR="cache/events"

ytRE = re.compile('(//www.youtube.com/embed/[a-zA-Z0-9_-]+)\'')
scRE = re.compile('(http(s)*://(www.)*soundcloud.com/[a-zA-Z0-9_-]+)\"')
mpRE = re.compile('(http://audio.sxsw.com/\d+/mp3_by_artist_id/(\d+).mp3)')

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
        



