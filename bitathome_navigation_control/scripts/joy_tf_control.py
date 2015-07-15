#!/usr/bin/env python
# coding=utf-8
# Filename : shopping.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标相对坐标,进行运动
# History
#   2015/05/10 00:03 : 创建文件 [刘达远]

import rospy
import roslib
import tf
from sensor_msgs.msg import Joy


def run(data):
    global joyData, x, y, theta
    change = 0.1
    change_th = 0.1
    if data.buttons[4] == 1 or data.buttons[5] == 1:
        change = 0.025
        change_th = 0.01
    x += change * data.buttons[3] - change * data.buttons[0]
    y += change * data.buttons[2] - change * data.buttons[1]
    theta += change_th * data.axes[6]

def tf_pub():
    global x, y, theta
    while not rospy.is_shutdown():
        br = tf.TransformBroadcaster()
        br.sendTransform((x, y, 0),tf.transformations.quaternion_from_euler(0, 0, theta),rospy.Time.now(),"map_map","map")

if __name__ == "__main__":
    rospy.init_node("joy_tf_control")
    joyData = Joy()
    x = 0.0
    y = 0.0
    theta = 0.0
    joy_pub = rospy.Subscriber("/joy", Joy, run)

    tf_pub()

    rospy.spin()
