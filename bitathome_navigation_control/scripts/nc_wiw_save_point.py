#!/usr/bin/env python
# coding=utf-8
# Filename : nc_wiw_save_point.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标相对坐标,给move_base提供绝对坐标,用于who is who
# History
#   2015/4/25 10:23 : 创建文件 [刘达远]

import rospy
from geometry_msgs.msg import Point
from move_base_msgs.msg import MoveBaseActionFeedback


def run1(data):
    global feedbackData, points
    people = Point()
    people.x = data.x + feedbackData.feedback.base_position.pose.position.x
    people.y = data.y + feedbackData.feedback.base_position.pose.position.y
    flag = True
    # 进行判断,如果在半米内有已经存的点,则不存
    for it in points:
        if (it.x - people.x) ** 2 + (it.y - people.y) ** 2 < 0.25:
            flag = False
            break
    if flag:
        rospy.loginfo("ADD POS X:%f Y:%f" % (people.x, people.y))
        points.append(people)
        wiw_pub.publish(people)


# 更新move_base返回的机器所在的绝对坐标
def run2(data):
    global feedbackData
    feedbackData = data
    #rospy.loginfo("updata feedbackData")

if __name__ == "__main__":
    rospy.init_node("nc_wiw_sive_point")
    wiw_pub = rospy.Publisher('Kinect/wiw_point_save', Point, queue_size=10)
    pointData = Point()
    feedbackData = MoveBaseActionFeedback()
    points = list()
    save_point_pub = rospy.Subscriber("/Kinect/wiw_point", Point, run1)
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, run2)

    rospy.spin()
