#!/usr/bin/env python
# coding=utf-8
# Filename : mc_joy_control.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 手柄操控
# History
#   2014/11/16 21:44 : 创建文件 [刘达远]

import rospy
from sensor_msgs.msg import *
from bitathome_hardware_control.srv import *


def joy_callback(data):
    global joyData
    joyData = data


def joy_loop():
    global joyData
    while not rospy.is_shutdown():
        if joyData is None or len(joyData.axes) == 0:
            continue

        else:
            x = int(joyData.axes[1] * 300 + joyData.axes[6] * 300)
            y = int(joyData.axes[5] * 300)
            theta = int(joyData.axes[0] * 200)
            ser(x, y, theta)
            rospy.loginfo("x:%d y:%d theta:%d" % (x, y, theta))

        rospy.sleep(0.5)

if __name__ == "__main__":
    rospy.init_node("joy_test")

    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    joyData = Joy()
    pub = rospy.Subscriber("/joy", Joy, joy_callback)

    joy_loop()

    rospy.spin()
