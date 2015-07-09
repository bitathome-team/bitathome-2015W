#!/usr/bin/env python
# coding=utf-8
# Filename : joy_start_follow.py
# Author : Majunbang
# E-mail : 2803650957@qq.com
# Description : 手柄控制follow启动
# History
#   2015/06/30 16:38 : 创建文件 [马俊邦]
import rospy
from sensor_msgs.msg import *
from bitathome_move_control.msg import *

def joy_callback(data):
    global joyData
    joyData = data

def joy_loop():
    global joyData
    while not rospy.is_shutdown():
        if joyData is None or len(joyData.axes) is 0:
            continue
        #控制follow
        if joyData.buttons[0] == 1:
            follow.publish(1)
        if joyData.buttons[1] == 1:
            follow.publish(0)
        rospy.sleep(0.2)

if __name__ == "__main__":
    rospy.init_node("StartFollow")
    print "手柄控制follow,A键启动,Ｂ键停止"
    joyData = Joy()
    pub = rospy.Subscriber("/joy", Joy, joy_callback)
    follow = rospy.Publisher("StartFollow", sf, queue_size=10)
    rate = rospy.Rate(10) # 10hz
    joy_loop()

    rospy.spin()
