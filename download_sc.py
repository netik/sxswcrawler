#!/usr/bin/python
# this is built for python 2.7. I am not dealing with python3 issues yet.
#
import os

DRYRUN=True

f = open("data/download_queue.txt")

os.chdir("music/sc")

for line in f:
    parts = line.split(" ")
    url = parts[2].rstrip()
    paths = url.split("/")

    if DRYRUN:
        print "soundscrape %s -t %s" % (paths[3], paths[4])
    else:
        os.system("soundscrape %s -t %s" % (paths[3], paths[4]))




