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
from nav_msgs.msg import OccupancyGrid                      # 地图数据


def update_feedbackData(data):
    global feedbackData
    feedbackData = data.feedback.base_position.pose


def update_scanData(data):
    global scanData
    scanData = data.ranges


def update_mapData(data):
    global mapData
    size = int(0.1 / data.info.resolution + 0.5)
    width = data.info.width / size
    height = data.info.height / size
    print(size)
    print(width)
    print(height)
    mapData = [0 for i in range(width * height)]
    for i in range(height):
        for j in range(width):
            flag = False
            for ii in range(size):
                for jj in range(size):
                    if data.data[i * width * size * size + j * size + ii * width * size + jj] > 0:
                        flag = True
                        break
                if (flag):
                    break
            if (flag):
                for ii in range(9):
                    for jj in range(9):
                        if (i - 4 + ii) * width + (j - 4 + jj) > 0 and (i - 4 + ii) * width + (j - 4 + jj) < width * height:
                            mapData[(i - 4 + ii) * width + (j - 4 + jj)] = 100
    #print(mapData)


def map_run():
    global feedbackData, scanData, mapData
    while not rospy.is_shutdown():
        rospy.sleep(1)


if __name__ == "__main__":
    rospy.init_node("my_map")

    goalPoint_pub = rospy.Publisher("/my_move_base/goalPoint", MyPoint, queue_size=10)

    feedbackData = Pose()
    scanData = list()
    mapData = []
    
    #move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, update_feedbackData)
    #scan_pub = rospy.Subscriber("/scan", LaserScan, update_scanData)
    map_pub = rospy.Subscriber("/map", OccupancyGrid, update_mapData)

    map_run()

    rospy.spin()
