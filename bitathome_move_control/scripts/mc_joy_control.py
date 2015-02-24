#!/usr/bin/env python
#-*-encoding:utf-8-*-

temp_speed = 1000

import rospy
from sensor_msgs.msg import *
from bitathome_hardware_control.srv import *


def joy_callback(data):
    global joyData
    joyData = data


def joy_loop():
    global joyData
    while not rospy.is_shutdown():
        if joyData is None or len(joyData.axes) == 0:
            continue

        else:
            x = int(joyData.axes[1] * temp_speed + joyData.axes[6] * temp_speed)
            y = int(joyData.axes[5] * temp_speed)
            theta = int(- joyData.axes[0] * temp_speed)
            ser(x, y, theta)
            rospy.loginfo("x:%d y:%d theta:%d" % (x, y, theta))

        rospy.sleep(0.5)

if __name__ == "__main__":
    rospy.init_node("joy_test")

    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    joyData = Joy()
    pub = rospy.Subscriber("/joy", Joy, joy_callback)

    joy_loop()

    rospy.spin()
