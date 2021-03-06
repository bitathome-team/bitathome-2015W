#!/usr/bin/env python
# coding=utf-8
# Filename : nc_shopping_kinect_move_base.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标相对坐标,提供绝对坐标,用于shopping
# History
#   2015/4/30 9:8 : 创建文件 [刘达远]

import rospy
from geometry_msgs.msg import Point
from move_base_msgs.msg import MoveBaseActionFeedback
from tf.transformations import euler_from_quaternion
from bitathome_remote_control.srv import say
from bitathome_navigation_control.msg import *
from bitathome_navigation_control.srv import *
import math


# 更新kinect传过来的follow相对坐标
def run1(data):
    global pointData, points, feedbackData
    if data.time == 0:
    	pointData = data
    elif abs(data.time) < 5:
        it = abs(data.time)
        data.x = feedbackData.feedback.base_position.pose.position.x
        data.y = feedbackData.feedback.base_position.pose.position.y
        data.z = data.time / abs(data.time)
        quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
        z = euler_from_quaternion(quaternion, axes='sxyz')
        data.z = z[2] + data.z * math.pi / 2
        points[it] = data
        rospy.loginfo("Add %d is : X:%f Y:%f Theta:%f" % (it, data.x, data.y, data.z))
    elif data.time == 5:
        data.x = feedbackData.feedback.base_position.pose.position.x
        data.y = feedbackData.feedback.base_position.pose.position.y
        data.z = data.time / abs(data.time)
        quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
        z = euler_from_quaternion(quaternion, axes='sxyz')
        data.z = z[2]
        points[0] = data
        rospy.loginfo("Add home is : X:%f Y:%f Theta:%f" % (data.x, data.y, data.z))
    elif points[data.time-5] is not None:
        pointData.x = points[data.time-5].x
        pointData.y = points[data.time-5].y
        pointData.z = points[data.time-5].z
        pointData.time = data.time
    else:
        rospy.loginfo("I can't find it.")
    #rospy.loginfo("updata pointData")


# 更新move_base返回的机器所在的绝对坐标
def run2(data):
    global feedbackData
    feedbackData = data
    #rospy.loginfo("updata feedbackData")


# 根据pointData 和 feedbackData 计算目标节点坐标,并发布个move_base节点
def shopping_pub():
    global pointData, feedbackData, flag
    while not rospy.is_shutdown():
        if pointData is None or feedbackData is None:
            continue

        elif math.fabs(pointData.x) < 0.01 and math.fabs(pointData.y) < 0.01:
            continue

        elif flag:
            if pointData.time == 0:
                # 和记录的目标节点相距0.2米为目标点
                x = int((pointData.x - 0.5 * math.cos(pointData.z) + feedbackData.feedback.base_position.pose.position.x) * 100) / 100.0
                y = int((pointData.y - 0.5 * math.sin(pointData.z) + feedbackData.feedback.base_position.pose.position.y) * 100) / 100.0
                quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
                # z[0] x轴旋转轴的旋转角度, z[1] y轴, z[2] z轴
                z = euler_from_quaternion(quaternion, axes='sxyz')
                theta = z[2] + pointData.z
                ser(x, y, theta, 15)
                # rospy.loginfo("x:%f y:%f theta:%f" % (x, y, theta * 180 / math.pi))
            elif pointData.time > 5:
                result = 2
                while result == 2:
                    result = int(str(ser(pointData.x, pointData.y, pointData.z, 60))[8])
                if result == 1:
                    rospy.loginfo("I get")
                else:
                    rospy.loginfo("I con't get to there.")


if __name__ == "__main__":
    rospy.init_node("kinect_move_base")

    ser = rospy.ServiceProxy("/nc_move_base_server/goal_speed", MoveBasePoint)
    say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
    pointData = MovePoint()
    feedbackData = MoveBaseActionFeedback()
    flag = True
    points = [None for i in range(5)]
    point_pub = rospy.Subscriber("/Kinect/Shopping_point", MovePoint, run1)
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, run2)

    shopping_pub()

    rospy.spin()
