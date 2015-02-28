#!/usr/bin/env python
# coding=utf-8
# Filename : nc_kinect_move_base.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标相对坐标,提供绝对坐标
# History
#   2015/2/28 18:16 : 创建文件 [刘达远]

import rospy
from geometry_msgs.msg import Point
from move_base_msgs.msg import MoveBaseActionFeedback
from bitathome_navigation_control.srv import *

def run1(data):
    global pointData
    pointData = data


def run2(data):
    global feedbackData
    feedbackData = data


def pub():
    global pointData, feedbackData
    while not rospy.is_shutdown():
        if pointData is None:
            continue

        else:
            x = 3 + feedbackData.feedback.base_position.pose.position.x
            y = 0 + feedbackData.feedback.base_position.pose.position.y
            z = 0
            ser(x, y, z)

if __name__ == "__main__":
    rospy.init_node("kinect_move_base")

    ser = rospy.ServiceProxy("/nc_move_base_server/goal_speed", MoveBasePoint)

    pointData = Point()
    feedbackData = MoveBaseActionFeedback()
    #cmd_vel_pub = rospy.Subscriber("/kinect/Point", Point, run1)
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, run2)

    pub()

    rospy.spin()
