#!/usr/bin/python
#-*- encoding: utf-8 -*-

import cv2
import sys

if len(sys.argv) <= 1:
    print "png2pmg [img path]"
else:
    img = cv2.imread(sys.argv[1])
    flag = []
    for i in range(1024*1024):
        flag.append(0)
    for i in range(1024):
        for j in range(1024):
            if img[i][j][0] == 0:
                for ii in range(max(0, i - 13), min(1023, i + 13)):
                    for jj in range(max(0, j - 13), min(1023, j + 13)):
                        if (int(((abs(i-ii)*2.5)**2.0+(abs(j-jj)*2.5)**2.0)**0.5+0.6) <= 30):
                            flag[ii*1024+jj] = 1
                        elif flag[ii*1024+jj] is not 1:
                            flag[ii*1024+jj] = 2
            elif flag[i*1024+j] == 1 or flag[i*1024+j] == -1:
                continue 
    for i in range(1024):
        for j in range(1024):
            if flag[i*1024+j] == 1:
                img[i][j]=0
            elif flag[i*1024+j]==2:
                img[i][j] = 205
    cv2.imshow("mapshow", cv2.resize(img, (1024, 1024)))
    cv2.imwrite("mapshow.png", img)
    cv2.waitKey(0)
