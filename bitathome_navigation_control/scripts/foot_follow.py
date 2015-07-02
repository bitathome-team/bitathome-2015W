#!/usr/bin/env python
# coding=utf-8
# Filename : follow.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标方向,进行移动
# History
#   2015/05/08 18:31 : 创建文件 [刘达远]

import rospy, math
from bitathome_hardware_control.srv import *
from bitathome_move_control.msg import *
from sensor_msgs.msg import LaserScan


def run1(data):
    global scanData
    scanData = data.ranges

def sf_flag(sf_data):
    global start_follow
    start_follow = sf_data.sff

def run2(data):
    global styleData, speed
    if data.X < 0:
        styleData = "stop"
    elif data.X ** 2 + data.Y ** 2 < 0.09:
        styleData = "back"
    elif data.X ** 2 + data.Y ** 2 < 1.44:
        if data.Y / data.X  > 0.1:
            styleData = "left"
        elif data.Y / data.X < 0 - 0.1:
            styleData = "right"
        else:
            styleData = "stop"
    else:
        if data.Y / data.X  > 0.1:
            styleData = "goLeft"
        elif data.Y / data.X < 0 - 0.1:
            styleData = "goRight"
        else:
            styleData = "go"
    speed = math.atan((data.X ** 2 + data.Y ** 2) ** 0.5) * 10 - 5

def follow_pub():
    global scanData, styleData, start_follow
    while not rospy.is_shutdown():
        if scanData is None or styleData == "" or start_follow == 0:
            ser(0, 0, 0)
            continue
        rospy.loginfo("%s" % styleData)
        i = 0
        flag = False
        for it in scanData:
            if it < 0.50 and it > 0.09 and styleData == "back":
                if i < 90:
                    ser(0, 200, (i - 90))
                elif i > 360:
                    ser(0, 0 - 200, (i - 360))
                flag = True
                rospy.sleep(0.1)
            if it < 0.30 and it > 0.09 and styleData != "back":
                if i < 270:
                    ser(0, 150, (i - 270) / 3)
                elif i < 360:
                    ser(0, 0 - 150, (i - 270) / 3)
                flag = True
                rospy.sleep(0.1)
                break
            i += 1
        if flag:
            continue

        if styleData == "stop":
            ser(0,0,0)
        elif styleData == "go":
            ser(100*speed,0,0)
        elif styleData == "goRight":
            ser(100*speed,0,(0-67)*speed)
        elif styleData == "goLeft":
            ser(100*speed,0,67*speed)
        elif styleData == "right":
            ser(0,0,(0-133)*speed)
        elif styleData == "left":
            ser(0,0,133*speed)
        elif styleData == "back":
            ser(-200,0,0)
        print speed
        rospy.sleep(0.1)


if __name__ == "__main__":
    rospy.init_node("kinect_move")

    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    scanData = list()
    styleData = ""
    speed = 0
    scan_pub = rospy.Subscriber("/scan", LaserScan, run1)
    point_pub = rospy.Subscriber("FootFollow_topic", FootFollow, run2)
    start_follow = rospy.Subscriber("/StartFollow", sf, sf_flag)
    follow_pub()

    rospy.spin()
