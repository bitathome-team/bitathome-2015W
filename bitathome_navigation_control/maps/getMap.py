#!/usr/bin/python
#-*- encoding: utf-8 -*-

import sys
import cv2
import numpy as np

if __name__ == "__main__":
    fin = None
    try:
        fin = open(sys.argv[1]).read().split(",")
    except IndexError as index:
        print("mapshow [filename]")
        exit(-1)
    except Exception as exp:
        print("file open error")
        exit(-1)
    img = np.zeros((1024, 1024, 3), np.uint8)
    n = 0
    for i in range(1024):
        for j in range(1024):
            if int(fin[n]) == 0:
                img[i][j] = 255
            elif int(fin[n]) == -1:
                img[i][j] = 203
            n += 1

    cv2.imshow("mapshow", cv2.resize(img, (1024, 1024)))
    cv2.imwrite("mapshow.png",  cv2.resize(img, (1024, 1024)))
    cv2.waitKey(0)
