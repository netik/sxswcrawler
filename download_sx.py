#!/usr/bin/python
#
# download mp3s from SXSW
#

import os
import re
import requests

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)

    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                print ".",
                f.write(chunk)
                f.flush()
    return local_filename


f = open("data/mp3_missed.txt")
os.chdir("music/sx")

for line in f:
   m = re.search("file=(.*\.mp3)",line) 

   if m:
     print m.group(1)
     download_file(m.group(1))
     
