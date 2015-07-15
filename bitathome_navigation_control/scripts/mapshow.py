#!/usr/bin/env python
# coding=utf-8
# Filename : mapshow.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Created Date : 2015/07/12 17:00
# Description : 根据提供的地图信息, 显示图片
# History
#   2015/07/12 14:17 : 创建文件 [刘达远]

import cv2
import rospy
import numpy as np
from bitathome_navigation_control.msg import MyMap


def updata_mapData(data):
    global mapData
    mapData = data.data


def mapShow():
    while not rospy.is_shutdown():
        if len(mapData) == 0:
            continue
        img = np.zeros((1024, 1024, 3), np.uint8)
        n = 0
        for i in range(1024):
            for j in range(1024):
                if mapData[n] == 0:
                    img[j][i] = 255
                elif mapData[n] == -1:
                    img[j][i] = 203
                n += 1
        cv2.imshow("mapshow", cv2.resize(img, (1024, 1024)))
        cv2.waitKey(0)


if __name__ == "__main__":
    rospy.init_node("mapShow")
    
    mapData = []
    
    map_pub = rospy.Subscriber("/my_map_show", MyMap, updata_mapData)
    
    mapShow()

    rospy.spin()
