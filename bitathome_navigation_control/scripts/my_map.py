#!/usr/bin/env python
# coding=utf-8
# Filename : my_map.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Created Date : 2015/05/23 15:34
# Description : 根据文本文件创建地图, 并根据目标点, 规划路径
# History
#   2015/05/23 15:34 : 创建文件 [刘达远]
#   2015/06/27 10:47 : 修改文件 [刘达远]  : 修改BFS中的BUG

import rospy, time, numpy, Queue
from math import pi                                                                                                                        # 引入pi
from bitathome_navigation_control.msg import MyPoint                                                # 目标点信息
from move_base_msgs.msg import MoveBaseActionFeedback                                       # 机器当前位置
from sensor_msgs.msg import LaserScan                                                                                # 激光数据
from geometry_msgs.msg import Pose                                                                                    # 坐标点
from tf.transformations import quaternion_from_euler, euler_from_quaternion     # tf角度、四元数转换
from nav_msgs.msg import OccupancyGrid                                                                           # 地图数据


class tpoint():
    x = int
    y = int
    idd = int
    pa = int
    ddir = int


dirs = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]]
euler_angles = [0, pi/2, pi, 0-pi/2, pi/4, 3*pi/4, 0-3*pi/4, 0-pi/4]


def update_feedbackData(data):
    global feedbackData, Now, Start
    feedbackData = data.feedback.base_position.pose
    Now.x = Start.x - int(round(feedbackData.position.x * 10))
    Now.y = Start.y - int(round(feedbackData.position.y * 10))
    Now.orientation = feedbackData.orientation


def update_scanData(data):
    global scanData
    scanData = data.ranges


def update_goalData(data):
    global goalData, nowPoint, Now
    if goalData != data:
        goalData = data
        goalData.x = Now.x + goalData.x * 10
        goalData.y = Now.y + goalData.y * 10
        getPath()
        nowPoint = 0


def update_mapData(data):
    global mapData, Start, Now, width, height
    size = int(round(0.1 / data.info.resolution))
    width = data.info.width / size
    height = data.info.height / size
    Start.x = int(round(data.info.origin.position.x * 10 + width))
    Start.y = int(round(data.info.origin.position.y * 10 + height))
    mapData = [0 for i in range(width * height)]
    for i in range(height):
        for j in range(width):
            flag = 0
            for ii in range(size):
                for jj in range(size):
                    if data.data[i * width * size * size + j * size + ii * width * size + jj] > 0:
                        flag = 100
                        break
                    elif data.data[i * width * size * size + j * size + ii * width * size + jj] < 0:
                        flag = -1
                        break
                if flag != 0:
                    break
            if flag == 100:
                for ii in range(6):
                    for jj in range(6):
                        if (i - 2 + ii) * width + (j - 2 + jj) > 0 and (i - 2 + ii) * width + (j - 2 + jj) < width * height:
                            mapData[(i - 2 + ii) * width + (j - 2 + jj)] = 100
            elif flag == -1 and mapData[i * width + j] == 0:
                mapData[i * width + j] = -1
    #print(mapData)


def getPath():
    global Now, Start, goalData, width, height, PATH, getKey
    getKey = True
    PATH = []
    idd = 0
    path = list()
    tpath = list()
    q = Queue.Queue()

    tNow = tpoint()
    tNow.x = Now.x
    tNow.y = Now.y
    tNow.idd = idd
    idd += 1
    q.put(tNow)
    tpath.append(tNow)
    while q.empty() is not True:
        temp = q.get()
        if abs(temp.x -  goalData.x) < 0.055 and abs(temp.y - goalData.y) < 0.055:
            while True:
                path.append(tpath[temp.idd])
                temp = tpath[temp.pa]
                if temp.idd == 0:
                    break
            break

        for i in range(8):
            tson = tpoint()
            tson.x = temp.x + dirs[i][0]
            tson.y = temp.y + dirs[i][1]

            if round(tson.y * width + tson.x) < width * height and mapData[int(round(tson.y * width + tson.x))] == 0:
                tson.ddir = i
                tson.pa = temp.idd
                tson.idd = idd
                idd += 1
                q.put(tson)
                tpath.append(tson)
                mapData[int(round(tson.y * width + tson.x))] = 100

    next = -1
    for i in path:
        if i.ddir != next:
            PATH.append(i)
            next = i.ddir
    PATH.reverse()
    print len(PATH)
    print "getPath over"
    getKey = False


def map_run():
    global feedbackData, scanData, mapData, goalData, PATH, nowPoint, getKey
    start = time.time() - 100
    while not rospy.is_shutdown():
        if feedbackData == Pose() or scanData == [] or goalData == MyPoint():
            continue
        if time.time() - start < 100:
            if abs(feedbackData.position.x - (PATH[nowPoint].x - Start.x) / 10.0) < 0.055 and abs(feedbackData.position.y - (PATH[nowPoint].y - Start.y) / 10.0) < 0.055:
                if nowPoint + 1 == len(PATH):
                    continue
                elif nowPoint + 2 == len(PATH):
                    nowPoint += 1
                    ret = MyPoint()
                    ret.x = (PATH[nowPoint].x - Start.x) / 10.0
                    ret.y = (PATH[nowPoint].y - Start.y) / 10.0
                    ret.z = goalData.z
                    ret.say = goalData.say
                    goalPoint_pub.publish(ret)
                else:
                    nowPoint += 1
                    ret = MyPoint()
                    ret.x = (PATH[nowPoint].x - Start.x) / 10.0
                    ret.y = (PATH[nowPoint].y - Start.y) / 10.0
                    ret.z = euler_angles[PATH[nowPoint].ddir]
                    ret.say = ""
                    goalPoint_pub.publish(ret)
        else:
            while getKey:
                pass
            nowPoint = 0
            ret = MyPoint()
            ret.x = (PATH[nowPoint].x - Start.x) / 10.0
            ret.y = (PATH[nowPoint].y - Start.y) / 10.0
            ret.z = euler_angles[PATH[nowPoint].ddir]
            ret.say = ""
            goalPoint_pub.publish(ret)
            start = time.time()


if __name__ == "__main__":
    rospy.init_node("my_map")

    goalPoint_pub = rospy.Publisher("/my_move_base/goalPoint", MyPoint, queue_size=10)

    feedbackData = Pose()
    goalData = MyPoint()
    scanData = []
    mapData = []
    Now = tpoint()
    Start = tpoint()
    
    move_base_feedback_pub = rospy.Subscriber("/tf", tfMessage, update_feedbackData)
    scan_pub = rospy.Subscriber("/scan", LaserScan, update_scanData)
    map_pub = rospy.Subscriber("/map", OccupancyGrid, update_mapData)
    goal_pub = rospy.Subscriber("/my_map/goalPoint", MyPoint, update_goalData)

    map_run()

    rospy.spin()
