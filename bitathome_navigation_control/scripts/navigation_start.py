#!/usr/bin/env python
# coding=utf-8
# Filename : navigation.py
# Author : Majunbang
# E-mail : 2803650957@qq.com
# Description : navigation启动比赛的程序
# History
#    2015/07/18 18:23 : 创建文件 [马俊邦]
import rospy
from sensor_msgs.msg import LaserScan
import os

def run(data):
    global scanData
    scanData = data.ranges

if __name__ == "__main__":
    rospy.init_node("navigation_test")
    scan_pub = rospy.Subscriber("/scan", LaserScan, run)
    scanData = []
    start_flag = 0
    while not rospy.is_shutdown():
       # print "2222"
        if scanData == [] or scanData[270] < 1.0:
            '''
            print "3333"
            if scanData != []:
                print scanData[270]
            rospy.sleep(0.5)
            '''
            continue
        #print "111"
        if scanData[270] > 1.0 and start_flag == 0:
            print "ok"
            os.system("roslaunch bitathome_navigation_control GPSR.launch")
            rospy.sleep(4)
            start_flag = 1
            print "start_flag %d" % start_flag
        rospy.sleep(0.5)
