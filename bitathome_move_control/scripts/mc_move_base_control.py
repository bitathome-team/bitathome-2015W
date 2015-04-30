#!/usr/bin/env python
# coding=utf-8
# Filename : mc_move_base_control.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据move-base提供的运动参数,控制移动
# History
#   2015/2/27 21:44 : 创建文件 [刘达远]

import rospy
from geometry_msgs.msg import Twist, Point
from bitathome_hardware_control.srv import *

def run1(data):
    global go_stop
    # rospy.loginfo("go_stop = %d" % go_stop)
    if go_stop == 1:
        ser(0,0,0)
    elif go_stop == 0:
        x = int(data.linear.x * 1000)
        y = int(data.linear.y * 1000)
        theta = int(data.angular.z * 300) # 150
        ser(x,y,theta)
    else:
        theta = go_stop * 50
        ser(0,0,theta)


def run2(data):
    global go_stop
    go_stop = data.x


if __name__ == "__main__":
    global go_stop
    go_stop = 0
    rospy.init_node("move_base_control")

    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)

    movebase_pub = rospy.Subscriber("/cmd_vel", Twist, run1)
    kinect_pub = rospy.Subscriber("/Kinect/Style", Point, run2)

    rospy.spin()
