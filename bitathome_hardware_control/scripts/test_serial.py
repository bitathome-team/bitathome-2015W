#!/usr/bin/env python
# coding=utf-8
# Filename : hc_cmd_interface.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 电机驱动和码盘数据的发布
# History
#   2014/11/16 21:44 : 创建文件 [刘达远]
#   2015/2/27 14:00 : 修改文件 [刘达远] : 将电机驱动参数修改成移动速度


import rospy
from bitathome_hardware_control.srv import *
import math


if __name__ == '__main__':
    rospy.init_node("test_serial")
    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)

    test()

    rospy.spin()
