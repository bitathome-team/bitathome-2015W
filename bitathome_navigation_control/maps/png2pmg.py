#!/usr/bin/python
#-*- encoding: utf-8 -*-

from cv2 import *
import sys

if len(sys.argv) <= 1:
	print "png2pmg [img path]"
else:
	img = imread(sys.argv[1])
	imwrite(sys.argv[1].split('.')[0]+".pgm", img)


