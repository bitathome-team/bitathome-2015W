#!/usr/bin/env python
# coding=utf-8
# Filename : nc_wiw_kinect_move_base.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标相对坐标,提供绝对坐标,用于who is who
# History
#   2015/2/28 18:16 : 创建文件 [刘达远]
#   2015/3/25 15:48 : 修改文件 : 添加注释 [刘达远]
#   2015/4/5  20:30 : 修改文件 : 适用于国内赛 [刘达远]

import rospy
from geometry_msgs.msg import Point
from move_base_msgs.msg import MoveBaseActionFeedback
from tf.transformations import euler_from_quaternion
from bitathome_navigation_control.srv import *
import math


# 更新kinect传过来的follow相对坐标
def run1(data):
    global feedbackData, points
    people = Point()
    people.x = data.x + feedbackData.feedback.base_position.pose.position.x
    people.y = data.y + feedbackData.feedback.base_position.pose.position.y
    flag = True
    for it in points:
        if (it.x - people.x) ** 2 + (it.y - people.y) ** 2 < 0.25:
            flag = False
    if flag:
        points.append(people)


# 更新move_base返回的机器所在的绝对坐标
def run2(data):
    global feedbackData
    feedbackData = data
    #rospy.loginfo("updata feedbackData")


# 根据pointData 和 feedbackData 计算目标节点坐标,并发布个move_base节点
def wiw_pub():
    global points, feedbackData, count
    while not rospy.is_shutdown():
        num = len(points)
        if count < num:
            nowx = points.x - feedbackData.feedback.base_position.pose.position.x
            nowy = points.y - feedbackData.feedback.base_position.pose.position.y
            if nowx >= 0:
                theta = math.atan(nowx / nowy)
            else :
                if nowy >= 0:
                    theta = math.pi + math.atan(nowx / nowy)
                else:
                    theta = math.atan(nowx / nowy) - math.pi
            x = int((nowx - 0.2 * math.cos(theta) + feedbackData.feedback.base_position.pose.position.x) * 100) / 100.0
            y = int((nowy - 0.2 * math.sin(theta) + feedbackData.feedback.base_position.pose.position.y) * 100) / 100.0
            theta = int(theta * 100) / 100.0
            result = 2
            while result == 2:
            	result = ser(x, y, theta, 60)
                rospy.loginfo("x:%f y:%f theta:%f" % (x, y, theta * 180 / math.pi))
            if result == 1:
                rospy.loginfo("I find you")
                pass # say i find you
            elif result == 0:
                continue


if __name__ == "__main__":
    rospy.init_node("kinect_move_base")

    ser = rospy.ServiceProxy("/nc_move_base_server/goal_speed", MoveBasePoint)
    pointData = Point()
    feedbackData = MoveBaseActionFeedback()
    points = list()
    count = 0
    cmd_vel_pub = rospy.Subscriber("/Kinect/wiw_point", Point, run1)
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, run2)

    wiw_pub()

    rospy.spin()
