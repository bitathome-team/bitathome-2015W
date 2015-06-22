#!/usr/bin/env python
# coding=utf-8
# Filename : my_map.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Created Date : 2015/05/23 15:34
# Description : 根据文本文件创建地图, 并根据目标点, 规划路径
# History
#   2015/05/23 15:34 : 创建文件 [刘达远]

import rospy, time, numpy, Queue
from math import pi                                                             # 引入pi
from bitathome_navigation_control.msg import MyPoint                            # 目标点信息
from move_base_msgs.msg import MoveBaseActionFeedback                           # 机器当前位置
from sensor_msgs.msg import LaserScan                                           # 激光数据
from geometry_msgs.msg import Pose                                              # 坐标点
from tf.transformations import quaternion_from_euler, euler_from_quaternion     # tf角度、四元数转换
from nav_msgs.msg import OccupancyGrid                                          # 地图数据


def update_feedbackData(data):
    global feedbackData, Now, Start
    feedbackData = data.feedback.base_position.pose
    Now.position.x = Start.position.x - int(round(feedbackData.position.x * 10))
    Now.position.y = Start.position.y - int(round(feedbackData.position.y * 10))
    Now.orientation = feedbackData.orientation


def update_scanData(data):
    global scanData
    scanData = data.ranges


def update_mapData(data):
    global mapData, Start, Now, width, height
    size = int(0.1 / data.info.resolution + 0.5)
    width = data.info.width / size
    height = data.info.height / size
    Now = data.info.origin
    Now.position.x += width
    Now.position.y += height
    Start = Now
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


def update_goalData(data):
    global goalData, PATH, nowPoint
    goalData = data
    PATH = getPath()
    nowPoint


class tpoint():
    point = Pose()
    id = int
    pa = int
    dir = int

dirs = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]]
euler_angles = [0,pi/2, pi, 0-pi/2, pi/4, 3*pi/4, 0-3*pi/4, 0-pi/4]

def getPath():
    global Now, Start, goalData, width, height
    id = 0
    path = list()
    tpath = list()
    q = Queue.Queue()

    tNow = tpoint()
    tNow.point = Now
    tNow.id = id
    id += 1
    q.put(tNow)
    while q.empty() is not True:
        temp = q.get()
        if temp.point.info.origin.position.x == goalData.x and temp.point.info.origin.position.y == goalData.y:
            while True:
                path.append(tpath[temp.id])
                temp = tpath[temp.pa]
                if temp.id == 0:
                    break
            break

        for i in range(8):
            tson = tpoint
            tson.point.position.x = temp.point.position.x + dirs[i, 0]
            tson.point.position.y = temp.point.position.y + dirs[i, 1]
            if mapData[tson.point.position.y * width + tson.point.position.x] == 0:
                tson.dir = i
                tson.pa = temp.id
                tson.id = id
                id += 1
                q.put(tson)
                tpath.append(tson)

    next = path[0].dir + 1
    for i in len(path):
        if path[i].dir == next:
            path.pop(i)
        else:
            next = path[i].dir
    path.reverse()

    return path


def map_run():
    global feedbackData, scanData, mapData, goalData, PATH, nowPoint
    start = time.time()
    while not rospy.is_shutdown():
        if feedbackData == Pose() or scanData == [] or goalData == MyPoint():
            continue
        if time.time() - start < 10:
            if feedbackData.position.x == PATH[nowPoint].point.position.x and feedbackData.position.y == PATH[nowPoint].point.position.y:
                if nowPoint + 1 == len(PATH):
                    continue
                elif nowPoint + 2 == len(PATH):
                    nowPoint += 1
                    ret = MyPoint()
                    ret.x = PATH[nowPoint].point.position.x
                    ret.y = PATH[nowPoint].point.position.y
                    ret.z = goalData.z
                    ret.say = goalData.say
                    goalPoint_pub.publish(ret)
                else:
                    nowPoint += 1
                    ret = MyPoint()
                    ret.x = PATH[nowPoint].point.position.x
                    ret.y = PATH[nowPoint].point.position.y
                    ret.z = euler_angles[PATH[nowPoint].dir]
                    ret.say = ""
                    goalPoint_pub.publish(ret)


if __name__ == "__main__":
    rospy.init_node("my_map")

    goalPoint_pub = rospy.Publisher("/my_move_base/goalPoint", MyPoint, queue_size=10)

    feedbackData = Pose()
    goalData = MyPoint()
    scanData = list()
    mapData = []
    
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, update_feedbackData)
    scan_pub = rospy.Subscriber("/scan", LaserScan, update_scanData)
    map_pub = rospy.Subscriber("/map", OccupancyGrid, update_mapData)
    goal_pub = rospy.Subscriber("/my_map/goalPoint", MyPoint, update_goalData)

    map_run()

    rospy.spin()
