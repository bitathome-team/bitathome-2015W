#!/usr/bin/env python
# coding=utf-8
# Filename : my_map.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Created Date : 2015/05/23 15:34
# Description : 根据文本文件创建地图, 并根据目标点, 规划路径
# History
#   2015/05/23 15:34 : 创建文件 [刘达远]

import rospy, math, time, numpy
from bitathome_navigation_control.msg import MyPoint    # 目标点信息
from move_base_msgs.msg import MoveBaseActionFeedback   # 机器当前位置
from sensor_msgs.msg import LaserScan                   # 激光数据
from geometry_msgs.msg import Pose                      # 坐标点
from tf.transformations import euler_from_quaternion    # tf角度、四元数转换


def update_feedbackData(data):
    global feedbackData
    feedbackData = data.feedback.base_position.pose


def update_scanData(data):
    global scanData
    scanData = data.ranges


def read_file():
    global my_map
    map_file = open("../maps/myMap.txt")
    line = map_file.readline()
    buf = buf.split(" ")
    my_map = numpy.zeros((int(buf[0]), int(buf[1])), numpy.uint8)

def my_map():
    global map_file
    read_file()
    


if __name__ == "__main__":
    rospy.init_node("my_map")

    goalPoint_pub = rospy.Publisher("/my_move_base/goalPoint", MyPoint, queue_size=10)

    feedbackData = Pose()
    scanData = list()
    
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, update_feedbackData)
    scan_pub = rospy.Subscriber("/scan", LaserScan, update_scanData)

    my_map()

    rospy.spin()
