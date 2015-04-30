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
from bitathome_remote_control.srv import say
from bitathome_navigation_control.srv import *
import math


# 更新kinect传过来的wiw相对坐标, 并将绝对坐标存起来
def run1(data):
    global feedbackData, points
    points.append(data)
    rospy.loginfo("Add person : x:%f y:%f" % (data.x, data.y))


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
            # 计算相对坐标
            nowx = points[count].x - feedbackData.feedback.base_position.pose.position.x
            nowy = points[count].y - feedbackData.feedback.base_position.pose.position.y
            count += 1
            # print("count is %d" % count)
            if nowx >= 0:
                theta = math.atan(nowy / nowx)
            else :
                if nowy >= 0:
                    theta = math.pi + math.atan(nowy / nowx)
                else:
                    theta = math.atan(nowy / nowx) - math.pi

            # 计算目标点,距离目标前0.5米, 角度皆为弧度
            x0 = int((nowx - 0.8 * math.fabs(math.cos(theta)) + feedbackData.feedback.base_position.pose.position.x) * 100) / 100.0
            y0 = int((nowy - 0.8 * math.fabs(math.sin(theta)) + feedbackData.feedback.base_position.pose.position.y) * 100) / 100.0
            quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
            z = euler_from_quaternion(quaternion, axes='sxyz')
            theta0 = int(theta * 100) / 100.0 + z[2]

            x1 = int((nowx + 0.8 * math.sin(theta) + feedbackData.feedback.base_position.pose.position.x) * 100) / 100.0
            y1 = int((nowy + 0.8 * math.cos(theta) + feedbackData.feedback.base_position.pose.position.y) * 100) / 100.0
            theta1 = int((theta - math.pi / 2) * 100) / 100.0 + z[2]

            x2 = int((nowx - 0.8 * math.sin(theta) + feedbackData.feedback.base_position.pose.position.x) * 100) / 100.0
            y2 = int((nowy - 0.8 * math.cos(theta) + feedbackData.feedback.base_position.pose.position.y) * 100) / 100.0
            theta2 = int((theta + math.pi / 2) * 100) / 100.0 + z[2]

            x3 = int((nowx + 0.8 * math.cos(theta) + feedbackData.feedback.base_position.pose.position.x) * 100) / 100.0
            y3 = int((nowy + 0.8 * math.sin(theta) + feedbackData.feedback.base_position.pose.position.y) * 100) / 100.0
            theta3 = int(theta + math.pi * 100) / 100.0 + z[2]

            # 返回2为没有走到目标点, 1为以达到, 0为目标点不可达放弃
            result = int
            result = 2
            while result > 1.5:
                rospy.logerr("MOVE0 POS X:%f Y:%f" % (x0, y0))
                result = int(str(ser(x0, y0, theta0, 60))[8])
                # rospy.loginfo("x:%f y:%f theta:%f" % (x0, y0, theta0 * 180 / math.pi))
                # rospy.loginfo("result is %d" % result)
            if result > 0.5 and count is not 1:
                rospy.loginfo("I found you")# say i find you
                say_ser("I I found you!")
                rospy.sleep(2)
            elif count is not 1:
                # 尝试目标左侧的点
                result = 2
                while result > 1.5:
                    rospy.logerr("MOVE1 POS X:%f Y:%f" % (x1, y1))
                    result = int(str(ser(x1, y1, theta1, 60))[8])
                    # rospy.loginfo("x:%f y:%f theta:%f" % (x1, y1, theta1 * 180 / math.pi))
                    # rospy.loginfo("result is %d" % result)
                if result > 0.5 and count is not 1:
                    rospy.loginfo("I found you")# say i find you
                    say_ser("I I found you!")
                    rospy.sleep(2)
                else:
                    # 尝试目标右侧的点
                    result = 2
                    while result > 1.5:
                        rospy.logerr("MOVE3 POS X:%f Y:%f" % (x3, y3)
                        result = int(str(ser(x3, y3, theta2, 60))[8])
                        # rospy.loginfo("x:%f y:%f theta:%f" % (x3, y3, theta3 * 180 / math.pi))
                        # rospy.loginfo("result is %d" % result)
                    if result > 0.5 and count is not 1:
                        rospy.loginfo("I found you")# say i find you
                        say_ser("I I found you!")
                        rospy.sleep(2)
                    else:
                        # 尝试目标后侧的点
                        result = 2
                        while result > 1.5:
                            rospy.logerr("MOVE2 POS X:%f Y:%f" % (x2, y2))
                            result = int(str(ser(x2, y2, theta3, 60))[8])
                            # rospy.loginfo("x:%f y:%f theta:%f" % (x2, y2, theta2 * 180 / math.pi))
                            # rospy.loginfo("result is %d" % result)
                        if result > 0.5 and count is not 1:
                            rospy.loginfo("I found you")# say i find you
                            say_ser("I I found you!")
                            rospy.sleep(2)
                        else:
                            rospy.loginfo("I con't find it")

            # 输出所有已经记录的点
            no = 1
            for p in points:
                print ("%d : x:%f y:%f" % (no, p.x, p.y))
                no += 1
        
        elif num > 1:
            nx = feedbackData.feedback.base_position.pose.position.x
            ny = feedbackData.feedback.base_position.pose.position.y
            quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
            z = euler_from_quaternion(quaternion, axes='sxyz')
            ntheta = z[2] + math.pi / 4
            ser(nx, ny, ntheta % (2 * math.pi), 10)


if __name__ == "__main__":
    rospy.init_node("kinect_move_base")

    ser = rospy.ServiceProxy("/nc_move_base_server/goal_speed", MoveBasePoint)
    say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
    pointData = Point()
    feedbackData = MoveBaseActionFeedback()
    points = list()
    count = 0
    save_point_pub = rospy.Subscriber("/Kinect/wiw_point_save", Point, run1)
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, run2)

    wiw_pub()

    rospy.spin()
