#!/usr/bin/env python
# coding=utf-8
# Filename : nc_kinect_move_base.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标相对坐标,提供绝对坐标
# History
#   2015/2/28 18:16 : 创建文件 [刘达远]
#   2015/3/25 15:48 : 修改文件 : 添加注释 [刘达远]
#   2015/4/5  20:30 : 修改文件 : 适用于国内赛 [刘达远]
#   2015/4/27 13:21 : 修改文件 : 修改注释 [刘达远]

import rospy
from geometry_msgs.msg import Point
from move_base_msgs.msg import MoveBaseActionFeedback
from tf.transformations import euler_from_quaternion
from bitathome_navigation_control.srv import *
import math


# 更新kinect传过来的follow相对坐标
def run1(data):
    global pointData
    pointData = data
    #rospy.loginfo("updata pointData")


# 更新move_base返回的机器所在的绝对坐标
def run2(data):
    global feedbackData
    feedbackData = data
    #rospy.loginfo("updata feedbackData")


# 根据pointData 和 feedbackData 计算目标节点坐标,并发布个move_base节点
def follow_pub():
    global pointData, feedbackData
    while not rospy.is_shutdown():
        if pointData is None or feedbackData is None:
            continue

        else:
            # 和记录的目标节点相距0.2米为目标点
            x = int((pointData.x - 0.2 * math.cos(pointData.z) + feedbackData.feedback.base_position.pose.position.x) * 100) / 100.0
            y = int((pointData.y - 0.2 * math.sin(pointData.z) + feedbackData.feedback.base_position.pose.position.y) * 100) / 100.0
            quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
            # z[0] x轴旋转轴的旋转角度, z[1] y轴, z[2] z轴
            z = euler_from_quaternion(quaternion, axes='sxyz')
            theta = z[2] + pointData.z
            rospy.loginfo("x:%f y:%f theta:%f" % (x, y, theta * 180 / math.pi))
            ser(x, y, theta, 1)


if __name__ == "__main__":
    rospy.init_node("kinect_move_base")

    ser = rospy.ServiceProxy("/nc_move_base_server/goal_speed", MoveBasePoint)
    pointData = Point()
    feedbackData = MoveBaseActionFeedback()
    save_point_pub = rospy.Subscriber("/Kinect/Follow_point", Point, run1)
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, run2)

    follow_pub()

    rospy.spin()
