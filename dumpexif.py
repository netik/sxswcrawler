#!/usr/bin/python

import mutagen.mp3 
from mutagen.mp3 import * 
import sys

audio = mutagen.File(sys.argv[1])

print audio

print audio.get("\xa9ART")
                  
