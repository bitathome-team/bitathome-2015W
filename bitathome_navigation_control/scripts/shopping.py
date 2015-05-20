#!/usr/bin/env python
# coding=utf-8
# Filename : shopping.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标相对坐标,进行运动
# History
#   2015/05/10 00:03 : 创建文件 [刘达远]

import rospy
from geometry_msgs.msg import Point
from move_base_msgs.msg import MoveBaseActionFeedback
from tf.transformations import euler_from_quaternion
from bitathome_remote_control.srv import say
from bitathome_remote_control.msg import Follow
from sensor_msgs.msg import LaserScan
from bitathome_hardware_control.srv import *
import math


def run1(data):
    global scanData
    scanData = data.ranges


def run2(data):
    global styleData
    styleData = data
    print data.s


def run3(data):
    global feedbackData
    feedbackData = data


# 根据pointData 和 feedbackData 计算目标节点坐标,并发布个move_base节点
def shopping_pub():
    global pointData, feedbackData, flag, points
    while not rospy.is_shutdown():
        if scanData is None or styleData.s is None or styleData.s == "":
            continue
	
	rospy.loginfo("%s" % styleData.s)
        i = 0
        flag = False
        for it in scanData:
            if it < 0.50 and it > 0.09 and styleData.s == "back":
                if i < 90:
                    ser(0, 200, (i - 90))
                elif i > 360:
                    ser(0, 0 - 200, (i - 360))
                flag = True
                rospy.sleep(0.5)
            if it < 0.30 and it > 0.09 and styleData.s != "back":
                if i < 270:
                    ser(0, 150, (i - 270) / 3)
                elif i < 360:
                    ser(0, 0 - 150, (i - 270) / 3)
                flag = True
                rospy.sleep(0.5)
                break
            i += 1
        if flag:
            continue

	if styleData.s == "stop":
            ser(0,0,0)
        elif styleData.s == "go":
            ser(300,0,0)
        elif styleData.s == "goRight":
            ser(200,0,0-150)
        elif styleData.s == "goLeft":
            ser(200,0,150)
        elif styleData.s == "right":
            ser(0,0,0-200)
        elif styleData.s == "left":
            ser(0,0,200)
        elif styleData.s == "back":
            ser(-200,0,0)
	elif styleData.s == "save":
            ret = Point()
            ret.x = feedbackData.feedback.base_position.pose.orientation.x
            ret.y = feedbackData.feedback.base_position.pose.orientation.y
            points.append(ret)
        elif styleData.s == "get0":
            points[1] = points[2]
            points[2] = None
            flag = True
        elif styleData.s == "get1":
            points[0] = points[1]
            points[1] = points[2]
            points[2] = None
            flag = True
        if flag:
            nowx = points[0].x - feedbackData.feedback.base_position.pose.position.x
            nowy = points[0].y - feedbackData.feedback.base_position.pose.position.y

            # print("count is %d" % count)
            if math.fabs(nowx) < 0.01:
                    theta = 0
            elif nowx >= 0:
                theta = math.atan(nowy / nowx)
            else :
                if nowy >= 0:
                    theta = math.pi + math.atan(nowy / nowx)
                else:
                    theta = math.atan(nowy / nowx) - math.pi
            quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
            z = euler_from_quaternion(quaternion, axes='sxyz')
            goal_theta = theta + z[2]
            if goal_theta > math.pi:
                goal_theta = goal_theta - 2 * math.pi

            while True:
                quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
                z = euler_from_quaternion(quaternion, axes='sxyz')
                if z[2] - goal_theta < 0 - 0.1:
                    if goal_theta - z[2] > 176 /333:
                        ser(0,0,176)
                    else:
                        ser(0,0,333 * (goal_theta-z[2]))
                    rospy.sleep(0.1)
                    rospy.loginfo("left")
                elif z[2] - goal_theta > 0.1:
                    if z[2] - goal_theta > 176 /333:
                        ser(0,0,176)
                    else:
                        ser(0,0,333 * (z[2]-goal_theta))
                    rospy.sleep(0.1)
                    rospy.loginfo("right")
                else:
                    for i in range(6):
                        if (feedbackData.feedback.base_position.pose.position.x - points[count].x) ** 2 + (feedbackData.feedback.base_position.pose.position.y - points[count].y) ** 2 < 0.25:
                            ser(0,0,0)
                            say_ser("I get it")
                            flag = True
                            count += 1
                            rospy.sleep(3)

                            j = 0
                            flag0 = False
                            for it in scanData:
                                if it < 0.50 and it > 0.09 and styleData.s == "back":
                                    if j < 90:
                                        ser(0, 200, (j - 90))
                                    elif j > 360:
                                        ser(0, 0 - 200, (j - 360))
                                    flag0 = True
                                    rospy.sleep(0.5)
                                    break
                                if it < 0.30 and it > 0.09 and styleData.s != "back":
                                    if j < 270:
                                        ser(0, 150, (j - 270) / 3)
                                    elif j < 360:
                                        ser(0, 0 - 150, (j - 270) / 3)
                                    flag0 = True
                                    rospy.sleep(0.5)
                                    break
                                j += 1
                            if flag0:
                                continue

                            ser(333,0,0)
                            rospy.sleep(0.5)
                            rospy.loginfo("go")
                    if flag:
                        break
                if flag:
                    break
        
            nowx = points[1].x - feedbackData.feedback.base_position.pose.position.x
            nowy = points[1].y - feedbackData.feedback.base_position.pose.position.y

            # print("count is %d" % count)
            if math.fabs(nowx) < 0.01:
                    theta = 0
            elif nowx >= 0:
                theta = math.atan(nowy / nowx)
            else :
                if nowy >= 0:
                    theta = math.pi + math.atan(nowy / nowx)
                else:
                    theta = math.atan(nowy / nowx) - math.pi
            quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
            z = euler_from_quaternion(quaternion, axes='sxyz')
            goal_theta = theta + z[2]
            if goal_theta > math.pi:
                goal_theta = goal_theta - 2 * math.pi

            while True:
                quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
                z = euler_from_quaternion(quaternion, axes='sxyz')
                if z[2] - goal_theta < 0 - 0.1:
                    if goal_theta - z[2] > 176 /333:
                        ser(0,0,176)
                    else:
                        ser(0,0,333 * (goal_theta-z[2]))
                    rospy.sleep(0.1)
                    rospy.loginfo("left")
                elif z[2] - goal_theta > 0.1:
                    if z[2] - goal_theta > 176 /333:
                        ser(0,0,176)
                    else:
                        ser(0,0,333 * (z[2]-goal_theta))
                    rospy.sleep(0.1)
                    rospy.loginfo("right")
                else:
                    for i in range(6):
                        if (feedbackData.feedback.base_position.pose.position.x - points[count].x) ** 2 + (feedbackData.feedback.base_position.pose.position.y - points[count].y) ** 2 < 0.25:
                            ser(0,0,0)
                            rospy.loginfo("get")
                            flag = True
                            count += 1
                            rospy.sleep(3)

                            j = 0
                            flag0 = False
                            for it in scanData:
                                if it < 0.50 and it > 0.09 and styleData.s == "back":
                                    if j < 90:
                                        ser(0, 200, (j - 90))
                                    elif j > 360:
                                        ser(0, 0 - 200, (j - 360))
                                    flag0 = True
                                    rospy.sleep(0.5)
                                    break
                                if it < 0.30 and it > 0.09 and styleData.s != "back":
                                    if j < 270:
                                        ser(0, 150, (j - 270) / 3)
                                    elif j < 360:
                                        ser(0, 0 - 150, (j - 270) / 3)
                                    flag0 = True
                                    rospy.sleep(0.5)
                                    break
                                j += 1
                            if flag0:
                                continue

                            ser(333,0,0)
                            rospy.sleep(0.5)
                            rospy.loginfo("go")
                    if flag:
                        break
                if flag:
                    break
        rospy.sleep(0.5)


if __name__ == "__main__":
    rospy.init_node("kinect_move_base")

    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
    scanData = list()
    styleData = Follow()
    points = list()
    scan_pub = rospy.Subscriber("/scan", LaserScan, run1)
    point_pub = rospy.Subscriber("/Kinect/Shopping_point", Follow, run2)
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, run3)

    shopping_pub()

    rospy.spin()
