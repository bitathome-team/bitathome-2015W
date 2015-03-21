#!/usr/bin/env python
# coding=utf-8
# Filename : nc_kinect_move_base.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标相对坐标,提供绝对坐标
# History
#   2015/2/28 18:16 : 创建文件 [刘达远]

import rospy
import threading
from geometry_msgs.msg import Point
from move_base_msgs.msg import MoveBaseActionFeedback
from bitathome_navigation_control.srv import *

def run1(data):
    global pointData
    pointData = data
    rospy.loginfo("updata pointData")


def run2(data):
    global feedbackData
    feedbackData = data
    rospy.loginfo("updata feedbackData")


def pub():
    global pointData, feedbackData
    while not rospy.is_shutdown():
        if pointData is None or feedbackData is None:
            continue

        else:
            x = int((pointData.x + feedbackData.feedback.base_position.pose.position.x)*10)/10.0
            y = int((pointData.y + feedbackData.feedback.base_position.pose.position.y)*10)/10.0
            z = 0
            ser(x, y, z)
            rospy.loginfo("x:%f y:%f theta:%f" % (x, y, z) )
        rospy.sleep(1)

if __name__ == "__main__":
    rospy.init_node("kinect_move_base")

    ser = rospy.ServiceProxy("/nc_move_base_server/goal_speed", MoveBasePoint)
    pointData = Point()
    feedbackData = MoveBaseActionFeedback()
    cmd_vel_pub = rospy.Subscriber("/Kinect/Point", Point, run1)
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, run2)

    pub()

    rospy.spin()
