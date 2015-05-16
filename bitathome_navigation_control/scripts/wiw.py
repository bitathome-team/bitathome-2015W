#!/usr/bin/env python
# coding=utf-8
# Filename : wiw.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标相对坐标,进行运动
# History
#   2015/05/09 16:58 : 创建文件 [刘达远]

import rospy
from geometry_msgs.msg import Point
from move_base_msgs.msg import MoveBaseActionFeedback
from tf.transformations import euler_from_quaternion
from bitathome_remote_control.srv import say
import math
from bitathome_hardware_control.srv import *
from sensor_msgs.msg import LaserScan
from bitathome_remote_control.msg import Follow
import time


# 更新kinect传过来的wiw相对坐标, 并将绝对坐标存起来
def run1(data):
    global feedbackData, points, key
    points.append(data)
    rospy.loginfo("Add person : x:%f y:%f" % (data.x, data.y))


# 更新move_base返回的机器所在的绝对坐标
def run2(data):
    global feedbackData
    feedbackData = data
    #rospy.loginfo("updata feedbackData")


def run3(data):
    global scanData
    scanData = data.ranges


def run4(data):
    global key
    if data.s == "yes":
        key = True
    elif data.s == "go":
	style = 2
        count = 0
        points = list()
        # 厨房坐标
        ret = Point()
        ret.x = 3
        ret.y = 2
        points.append(ret)
        # 卧室坐标
        ret = Point()
        ret.x = 5
        ret.y = 4
        points.append(ret)


# 根据pointData 和 feedbackData 计算目标节点坐标,并发布个move_base节点
def wiw_pub():
    global points, feedbackData, count, key, style
    style = 1
    time1 = time.time()
    while not rospy.is_shutdown():
        time2 = time.time()
        if time2 - time1 > 120 and style == 1:
            style = 2
            count = 0
            points = list()
            # 厨房坐标
            ret = Point()
            ret.x = 4.03
            ret.y = 0-4.01
            points.append(ret)
            ret = Point()
            ret.x = 5.18
            ret.y = 0-5.36
            points.append(ret)
            ret = Point()
            ret.x = 5.03
            ret.y = -8.08
            points.append(ret)
            # 卧室坐标
            ret = Point()
            ret.x = 6.12
            ret.y = 0-4.18
            points.append(ret)
        elif time2 - time1 > 360 and style == 2:
            style = 3
            count = 0
            points = list()
            # 门外坐标
            ret = Point()
            ret.x = 5.03
            ret.y = 0-8.08
            points.append(ret)
            ret = Point()
            ret.x = 6.12
            ret.y = 0-4.18
            points.append(ret)
            ret = Point()
            ret.x = 7.24
            ret.y = 0-6.41
            points.append(ret)
            ret = Point()
            ret.x = 7.36
            ret.y = 0-8.82
            points.append(ret)

        num = len(points)
        if count < num:
            flag = False
            while key:
                # 计算相对坐标
                nowx = points[count].x - feedbackData.feedback.base_position.pose.position.x
                nowy = points[count].y - feedbackData.feedback.base_position.pose.position.y

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
                    if time2 - time1 > 120 and style == 1:
                   	style = 2
        	   	count = 0
	           	points = list()
        	   	# 厨房坐标
        	   	ret = Point()
        	   	ret.x = 4.03
        	   	ret.y = 0-4.01
        	   	points.append(ret)
        	   	ret = Point()
        	  	ret.x = 5.18
        	    	ret.y = 0-5.36
        	    	points.append(ret)
        	    	ret = Point()
        	    	ret.x = 5.03
        	    	ret.y = -8.08
        	    	points.append(ret)
        	    	# 卧室坐标
        	    	ret = Point()
        	    	ret.x = 6.12
        	    	ret.y = 0-4.18
        	    	points.append(ret)
                        break
        	    elif time2 - time1 > 360 and style == 2:
        		style = 3
        	    	count = 0
       	 	    	points = list()
            		# 门外坐标
            		ret = Point()
            		ret.x = 5.03
            		ret.y = 0-8.08
           		points.append(ret)
           		ret = Point()
            		ret.x = 6.12
            		ret.y = 0-4.18
            		points.append(ret)
            		ret = Point()
            		ret.x = 7.24
            		ret.y = 0-6.41
            		points.append(ret)
            		ret = Point()
            		ret.x = 7.36
            		ret.y = 0-8.82
            		points.append(ret)
                        break
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
                            ser(0,0,333 * (goal_theta-z[2]))
                        rospy.sleep(0.1)
                        rospy.loginfo("right")
                    else:
                        for i in range(6):
                            if (feedbackData.feedback.base_position.pose.position.x - points[count].x) ** 2 + (feedbackData.feedback.base_position.pose.position.y - points[count].y) ** 2 < 0.25:
                                ser(0,0,0)
                                rospy.loginfo("get")
                                flag = True
                                if style == 1 and count > 0:
                                    key = False
                                else:
                                    rospy.sleep(3)
                                count += 1
                                break

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
        
        elif num > 0:
            nx = feedbackData.feedback.base_position.pose.position.x
            ny = feedbackData.feedback.base_position.pose.position.y
            quaternion = (feedbackData.feedback.base_position.pose.orientation.x, feedbackData.feedback.base_position.pose.orientation.y, feedbackData.feedback.base_position.pose.orientation.z, feedbackData.feedback.base_position.pose.orientation.w)
            z = euler_from_quaternion(quaternion, axes='sxyz')
            ntheta = z[2] + math.pi / 4
            ser(0, 0, 0-176)
            rospy.sleep(0.5)


if __name__ == "__main__":
    rospy.init_node("kinect_move_base")

    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
    pointData = Point()
    feedbackData = MoveBaseActionFeedback()
    scanData = list()
    points = list()
    count = 0
    key = True
    styleData = Follow()
    save_point_pub = rospy.Subscriber("/Kinect/wiw_point_save", Point, run1)
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, run2)
    scan_pub = rospy.Subscriber("/scan", LaserScan, run3)
    point_pub = rospy.Subscriber("/Kinect/Follow_point", Follow, run4)

    wiw_pub()

    rospy.spin()
