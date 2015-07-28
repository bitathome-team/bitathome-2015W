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
                for ii in range(max(0, i - 17), min(1023, i + 17)):
                    for jj in range(max(0, j - 17), min(1023, j + 17)):
                        if (int(((abs(i-ii)*2.5)**2.0+(abs(j-jj)*2.5)**2.0)**0.5+0.6) <= 35) and flag[ii*1024+jj] != 1:
                            flag[ii*1024+jj] = 3
                        elif flag[ii*1024+jj] is not 1 and flag[ii*1024+jj] is not 3:
                            flag[ii*1024+jj] = 2
                flag[i * 1024 + j] = 1
            elif flag[i*1024+j] == 1 or flag[i*1024+j] == -1:
                continue 
    for i in range(1024):
        for j in range(1024):
            if flag[i*1024+j] == 1:
                img[i][j]=0
            elif flag[i*1024+j]==2:
                img[i][j][0] = 64
                img[i][j][1] = 220
                img[i][j][2] = 240
            elif flag[i*1024+j]==3:
                img[i][j][0] = 225
                img[i][j][1] = 25
                img[i][j][2] = 25
    cv2.imshow("mapshow", cv2.resize(img, (1024, 1024)))
    cv2.imwrite("mapshow.png", img)
    cv2.waitKey(0)
