#!/usr/bin/env python
# coding=utf-8
# Filename : mc_move_base_control.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据move-base提供的运动参数,控制移动
# History
#   2015/2/27 21:44 : 创建文件 [刘达远]

import rospy
from geometry_msgs.msg import Twist
from bitathome_hardware_control.srv import *

def run(data):
    x = int(data.linear.x * 1000)
    y = int(data.linear.y * 1000)
    theta = int(data.angular.z * 150)
    ser(x,y,theta)

if __name__ == "__main__":
    rospy.init_node("move_base_control")

    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)

    pub = rospy.Subscriber("/cmd_vel", Twist, run)

    rospy.spin()
