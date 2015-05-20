#!/usr/bin/env python
# coding=utf-8
# Filename : my_move_base.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Created Date : 2015/05/18 14:17
# Description : 根据给定的目标点，进行移动
# History
#   2015/05/18 14:17 : 创建文件 [刘达远]


import rospy, math, time
from bitathome_hardware_control.srv import VectorSpeed  # 电机
from bitathome_remote_control.srv import say            # 语音（说）
from bitathome_navigation_control.msg import MyPoint
from move_base_msgs.msg import MoveBaseActionFeedback   # 机器当前位置
from sensor_msgs.msg import LaserScan                   # 激光数据
from tf.transformations import euler_from_quaternion    # tf角度、四元数转换
from geometry_msgs.msg import Pose                      # 坐标点


def update_feedbackData(data):
    global feedbackData
    feedbackData = data.feedback.base_position.pose


def update_scanData(data):
    global scanData
    scanData = data.ranges


def update_goalPointData(data):
    global goalPointData
    goalPointData = data


def my_move_base():
    global feedbackData, scanData, goalPointData
    while not rospy.is_shutdown():
        if feedbackData == Pose() or scanData == [] or goalPointData == MyPoint():
            continue

        if (feedbackData.position.x - goalPointData.x) ** 2 + (feedbackData.position.y - goalPointData.y) ** 2 < 0.09:
            quaternion = (feedbackData.orientation.x, feedbackData.orientation.y, feedbackData.orientation.z, feedbackData.orientation.w)
            z = euler_from_quaternion(quaternion, axes='sxyz')
            theta = z[2] - goalPointData.z
            if theta < 0 - 0.1:
                if theta < 0 - 176 / 333:
                    motor_ser(0, 0, 0 - 333)
                else:
                    motor_ser(0, 0, 0 - 176)
            elif theta > 0.1:
                if theta > 176 / 333:
                    motor_ser(0, 0, 333)
                else:
                    motor_ser(0, 0, 176)
            else:
                say_ser(goalPointData.say)

        nowx = goalPointData.x - feedbackData.position.x
        nowy = goalPointData.y - feedbackData.position.y
        if math.fabs(nowx) < 0.01:
            if nowy < 0:
                theta = 0 - math.pi / 2
            else:
                theta = math.pi / 2
        elif nowx > 0:
            theta = math.atan(nowy / nowx)
        else:
            if nowy > 0:
                theta = math.atan(nowy / nowx) + math.pi
            else:
                theta = math.atan(nowy / nowx) - math.pi

        if theta < 0 - 0.1:
            if theta < 0 - 176 / 333:
                motor_ser(0, 0, 0 - 333)
            else:
                motor_ser(0, 0, 0 - 176)
        elif theta > 0.1:
            if theta > 176 / 333:
                motor_ser(0, 0, 333)
            else:
                motor_ser(0, 0, 176)
        else:
            i = 0
            flag = False
            for it in scanData:
                if it < 0.30 and it > 0.09:
                    flag = True
                    if i < 270:
                       ser(0, 150, (i - 270) / 2)
                    else:
                       ser(0, 0 - 150, (i - 270) / 2)
                i += 1
            
            if flag:
                continue

            ser(333, 0, 0)
            rospy.sleep(0.1)            
                       

if __name__ == "__main__":
    rospy.init_node("my_move_base")
    
    motor_ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    say_ser = rospy.ServiceProxy("AudioPaly/TTS", say)
    
    feedbackData = Pose()
    scanData = list()
    goalPointData = MyPoint()
    
    move_base_feedback_pub = rospy.Subscriber("/move_base/feedback", MoveBaseActionFeedback, update_feedbackData)
    scan_pub = rospy.Subscriber("/scan", LaserScan, update_scanData)
    goalPoint_pub = rospy.Subscriber("/my_move_base/goalPoint", MyPoint, update_goalPointData)
    
    my_move_base()

    rospy.spin()
