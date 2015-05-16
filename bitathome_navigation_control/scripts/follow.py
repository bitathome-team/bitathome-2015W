#!/usr/bin/env python
# coding=utf-8
# Filename : follow.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标方向,进行移动
# History
#   2015/05/08 18:31 : 创建文件 [刘达远]

import rospy
import math
from bitathome_hardware_control.srv import *
from bitathome_remote_control.msg import Follow
from sensor_msgs.msg import LaserScan


def run1(data):
    global scanData
    scanData = data.ranges


def run2(data):
    global styleData
    styleData = data


def follow_pub():
    global scanData, styleData
    while not rospy.is_shutdown():
        if scanData is None or styleData.s is None or styleData.s == "":
            continue
        rospy.loginfo("%s" % styleData.s)
        i = 0
        flag = False
        for it in scanData:
            if it < 0.50 and it > 0.09 and styleData.s == "back":
                if i < 90:
                    ser(0, 200, (i - 90))
                elif i > 360:
                    ser(0, 0 - 200, (i - 360))
                flag = True
                rospy.sleep(0.5)
            if it < 0.30 and it > 0.09 and styleData.s != "back":
                if i < 270:
                    ser(0, 150, (i - 270) / 3)
                elif i < 360:
                    ser(0, 0 - 150, (i - 270) / 3)
                flag = True
                rospy.sleep(0.5)
                break
            i += 1
        if flag:
            continue

        if styleData.s == "stop":
            ser(0,0,0)
        elif styleData.s == "go":
            ser(300,0,0)
        elif styleData.s == "goRight":
            ser(200,0,0-150)
        elif styleData.s == "goLeft":
            ser(200,0,150)
        elif styleData.s == "right":
            ser(0,0,0-200)
        elif styleData.s == "left":
            ser(0,0,200)
        elif styleData.s == "back":
            ser(-200,0,0)
        rospy.sleep(0.5)


if __name__ == "__main__":
    rospy.init_node("kinect_move")

    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    scanData = list()
    styleData = Follow()
    scan_pub = rospy.Subscriber("/scan", LaserScan, run1)
    point_pub = rospy.Subscriber("/Kinect/Follow_point", Follow, run2)
    follow_pub()

    rospy.spin()
