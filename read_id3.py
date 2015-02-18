#!/usr/bin/python

from mutagen.id3 import ID3
id3info = ID3("music/sx/10421.mp3")

for k, v in id3info.items():
  print k, ":", v[0]
