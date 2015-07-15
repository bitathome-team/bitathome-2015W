#!/usr/bin/env python
# coding=utf-8
# Filename : my_get_path.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Created Date : 2015/07/05 15:00
# Description : 根据文本文件创建地图, 并根据目标点, 规划路径
# History
#   2015/07/05 15:00 : 创建文件 [刘达远]

import rospy, time, numpy, Queue
from math import pi                                                                                                                        # 引入pi
from bitathome_navigation_control.msg import MyPoint, Arr                                                # 目标点信息
from tf.msg import tfMessage                                                                                                     # 机器当前位置
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
    global feedbackData, Now, Start, pointSize
    if data.transforms[0].header.frame_id == "odom" and data.transforms[0].child_frame_id == "base_link" and Start != tpoint() and pointSize != 0:
        feedbackData.position.x = data.transforms[0].transform.translation.x
        feedbackData.position.y = data.transforms[0].transform.translation.y
        feedbackData.orientation = data.transforms[0].transform.rotation
        Now.x = Start.x + int(round(feedbackData.position.x / pointSize))
        Now.y = Start.y - int(round(feedbackData.position.y / pointSize))


def update_goalData(data):
    global goalData, Start, Goal, pointSize
    if goalData != data and Start != tpoint and pointSize != 0:
        goalData = data
        Goal.x = Start.x + int(round(goalData.x / pointSize))
        Goal.y = Start.y - int(round(goalData.y / pointSize))
        getPath()


def update_mapData(data):
    global mapDataInit, Start, width, height, pointSize
    pointSize = data.info.resolution
    width = data.info.width
    height = data.info.height
    Start.x = int(round(data.info.origin.position.x / pointSize + width))
    Start.y = int(round(data.info.origin.position.y / pointSize + height))
    mapDataInit = data.data
    #print(mapDataInit)


def getPath():
    global Now, Goal, width, height, PATH, getKey, mapDataInit, nowPoint
    getKey = True
    while Start == tpoint() and Goal == tpoint() and mapDataInit == []:
        continue
    print Now.x, Now.y
    print Goal.x, Goal.y
    PATH = []
    idd = 0
    path = list()
    tpath = list()
    q = Queue.Queue()
    mapData = []
    for i in mapDataInit:
        mapData.append(i)

    tNow = tpoint()
    tNow.x = Now.x
    tNow.y = Now.y
    tNow.idd = idd
    idd += 1
    q.put(tNow)
    tpath.append(tNow)
    while q.empty() is not True:
        temp = q.get()
        if temp.x ==  Goal.x and temp.y == Goal.y:
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
                mapData[tson.y * width + tson.x] = 100

    next = -1
    for i in path:
        if i.ddir != next:
            PATH.append(i)
            next = i.ddir
    PATH.reverse()
    mapData = mapDataInit[:]
    print "getPath over"
    getKey = False
    return len(PATH)


def map_run():
    global feedbackData, goalData, PATH, nowPoint, getKey, pointSize, Start
    start = time.time() 
    while not rospy.is_shutdown():
        if feedbackData == Pose() or goalData == MyPoint() or getKey:
            continue
        if time.time() - start < 100:
            #print Now.x, Now.y, nowPoint, PATH[nowPoint].x, PATH[nowPoint].y
            if abs(Now.x - PATH[nowPoint].x) < 3 and abs(Now.y - PATH[nowPoint].y) < 3:
                if nowPoint + 1 == len(PATH):
                    continue
                elif nowPoint + 2 == len(PATH):
                    nowPoint += 1
                    ret = MyPoint()
                    ret.x = (PATH[nowPoint].x - Start.x) * pointSize
                    ret.y = (PATH[nowPoint].y - Start.y) * pointSize
                    ret.z = goalData.z
                    ret.say = goalData.say
                    goalPoint_pub.publish(ret)
                else:
                    nowPoint += 1
                    ret = MyPoint()
                    ret.x = (PATH[nowPoint].x - Start.x) * pointSize
                    ret.y = (PATH[nowPoint].y - Start.y) * pointSize
                    ret.z = euler_angles[PATH[nowPoint].ddir]
                    ret.say = ""
                    goalPoint_pub.publish(ret)
            else:
                nowPoint += 1
                ret = MyPoint()
                ret.x = (PATH[nowPoint].x - Start.x) * pointSize
                ret.y = (PATH[nowPoint].y - Start.y) * pointSize
                ret.z = goalData.z
                ret.say = goalData.say
                goalPoint_pub.publish(ret)
        else:
            start = time.time()
            if getKey:
                continue
            pathLen = getPath()
            while getKey:
                print "continue2"
                continue
            if pathLen == 0:
                print "i can't get there"
            elif pathLen == 1:
                ret = MyPoint()
                ret.x = (PATH[nowPoint].x - Start.x) * pointSize
                ret.y = (PATH[nowPoint].y - Start.y) * pointSize
                ret.z = goalData.z
                ret.say = goalData.say
                goalPoint_pub.publish(ret)
            else :
                ret = MyPoint()
                ret.x = (PATH[nowPoint].x - Start.x) * pointSize
                ret.y = (PATH[nowPoint].y - Start.y) * pointSize
                ret.z = euler_angles[PATH[nowPoint].ddir]
                ret.say = ""
                goalPoint_pub.publish(ret)


if __name__ == "__main__":
    rospy.init_node("my_map")

    goalPoint_pub = rospy.Publisher("/my_move_base/goalPoint", MyPoint, queue_size=10)

    # feedbackData, goalData, scanData 单位是m
    feedbackData = Pose()
    goalData = MyPoint()
    scanData = []
    # Now, Start, Goal 存对应mapData中的下标 
    Now = tpoint()
    Start = tpoint()
    Goal = tpoint()
    # mapDataInit 一个格代表0.025m
    mapDataInit = []
    pointSize = 0
    getKey = False
    nowPoint = 0
    
    move_base_feedback_pub = rospy.Subscriber("/tf", tfMessage, update_feedbackData)
    map_pub = rospy.Subscriber("/map", OccupancyGrid, update_mapData)
    goal_pub = rospy.Subscriber("/my_map/goalPoint", MyPoint, update_goalData)

    map_run()

    rospy.spin()
