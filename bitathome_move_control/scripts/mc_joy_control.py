#!/usr/bin/env python
# coding=utf-8
# Filename : mc_joy_control.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 手柄操控
# History
#   2014/11/16 21:44 : 创建文件 [刘达远]
#   2015/02/28 14:06 : 完善手柄功能
#   2015/05/24 15:06 : 完善手柄功能 [马俊邦]

import rospy
import serial
from sensor_msgs.msg import *
from bitathome_hardware_control.srv import *


def joy_callback(data):
    global joyData
    joyData = data

# 判断是否超出范围
def constrain(val, v_min, v_max):
    if val < v_min:
        return v_min
    elif val > v_max:
        return v_max
    else:
        return val
# 抬高身体
def body_up():
    #rospy.wait_for_service('/hc_servo_control/body_control')
    try:
        body_control = rospy.ServiceProxy('/hc_servo_control/body_control', BodyUpDownStatus)
        body_control(1)
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e
        print "无法进行升降操作，请检查串口是否打开"


# 降低身体
def body_down():
    #rospy.wait_for_service('/hc_servo_control/body_control')
    try:
        body_control = rospy.ServiceProxy('/hc_servo_control/body_control', BodyUpDownStatus)
        body_control(-1)
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e
        print "无法进行升降操作，请检查串口是否打开"


# 停止升降身体
def body_stop():
    #rospy.wait_for_service('/hc_servo_control/body_control')
    try:
        body_control = rospy.ServiceProxy('/hc_servo_control/body_control', BodyUpDownStatus)
        body_control(0)
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e
        print "无法进行升降操作，请检查串口是否打开"


def set_servo_angle(head, neck, r_claw, l_claw, r_shoulder, l_shoulder, r_elbow, l_elbow, r_wrist, l_wrist, speed=0x7f):
    """
    设置所有舵机的角度
    :param head: 低头&抬头[-28, 22]
    :param neck: 颈部 左转&右转[-50, 50]
    :param r_claw: 右爪 合拢&松开[-30, 0]
    :param l_claw: 左爪 合拢&松开[-45, 0]
    :param r_shoulder: 右肩 放下&抬起[0, 70]
    :param l_shoulder: 左肩 抬起&放下[-70, 0]
    :param r_elbow: 右肘 抬起&放下[-75, 0]
    :param l_elbow: 左肘 抬起&放下[-75, 0]
    :param r_wrist: 右腕 左转&右转[-60, 60]
    :param l_wrist: 左腕 左转&右转[-60, 60]
    """
    #rospy.wait_for_service('/hc_servo_control/servo_control')
    try:
        servo_control = rospy.ServiceProxy('/hc_servo_control/servo_control', ServoAngle)
        servo_control(head, neck, r_claw, l_claw, r_shoulder, l_shoulder, r_elbow, l_elbow, r_wrist, l_wrist, speed)
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e
        print "无法进行手臂操作，请检查串口是否打开"
def joy_loop():
    global joyData,bodyflag
    # 左肩
    l_shoulder = 0
    # 右肩
    r_shoulder = 0
    # 左肘
    l_elbow = 0
    # 右肘
    r_elbow = 0
    # 左腕
    l_wrist = 0
    # 右腕
    r_wrist = 0
    # 左爪
    l_claw = 0
    # 右爪
    r_claw = 0
    while not rospy.is_shutdown():
        if joyData is None or len(joyData.axes) is 0:
            continue
        if joyData.axes[0] != 0 or joyData.axes[1] != 0 or joyData.axes[6] != 0 or joyData.axes[7] != 0 or joyData.buttons[5] == 1:
            #控制机器行进
            if joyData.axes[1] == 0:
                x = int((joyData.axes[7] * 300 ) * (1 - joyData.axes[5]) / 2)
            else:
                x = int((joyData.axes[1] * 300 ) * (1 - joyData.axes[5]) / 2)
            y = int(joyData.axes[6] * 300)
            theta = int(joyData.axes[0] * 300)
            #L2急停
            if joyData.buttons[5] == 1:
                try:
                    ser(0, 0, 0)
                    print "stop"
                except rospy.ServiceException, e:
                    print "Service call failed: %s" % e
                    print "无法进行移动1操作，请检查串口是否打开"
            else:
                try:
                    ser(x, y, theta)
                    rospy.loginfo("x:%d y:%d theta:%d" % (x, y, theta))
                except rospy.ServiceException, e:
                    print "Service call failed: %s" % e
                    print "无法进行移动2操作，请检查串口是否打开"
        #控制手臂身体运动
        if joyData.buttons[0]+joyData.buttons[1]+joyData.buttons[2] +joyData.buttons[3] > 0:
            l_shoulder += joyData.buttons[2] * joyData.buttons[4] * 5 + joyData.buttons[2] * (1-joyData.axes[2])/2 * -5
            r_shoulder += joyData.buttons[2] * joyData.buttons[5] * 5 + joyData.buttons[2] * (1-joyData.axes[5])/2 * -5
            l_elbow += joyData.buttons[3] * joyData.buttons[4] * 5 + joyData.buttons[3] * (1-joyData.axes[2])/2 * -5
            r_elbow += joyData.buttons[3] * joyData.buttons[5] * 5 + joyData.buttons[3] * (1-joyData.axes[5])/2  * -5
            l_wrist += joyData.buttons[1] * joyData.buttons[4] * 5 + joyData.buttons[1] * (1-joyData.axes[2])/2 * -5
            r_wrist += joyData.buttons[1] * joyData.buttons[5] * 5 + joyData.buttons[1] * (1-joyData.axes[5])/2  * -5
            l_claw += joyData.buttons[0] * joyData.buttons[4] * 5 + joyData.buttons[0] * (1-joyData.axes[2])/2 * -5
            r_claw += joyData.buttons[0] * joyData.buttons[5] * 5 + joyData.buttons[0] * (1-joyData.axes[5])/2  * -5
            #复位
            if joyData.buttons[8] is 1:
                l_shoulder = 0
                r_shoulder = 0
                l_elbow = 0
                r_elbow = 0
                l_wrist = 0
                r_wrist = 0
                l_claw = 0
                r_claw = 0
            #判断角度有没有超出限制
            r_claw = constrain(r_claw, -30, 0)
            l_claw = constrain(l_claw, -45, 0)
            r_shoulder = constrain(r_shoulder, 0, 70)
            l_shoulder = constrain(l_shoulder, -70, 0)
            r_elbow = constrain(r_elbow, -75, 0)
            l_elbow = constrain(l_elbow, -75, 0)
            r_wrist = constrain(r_wrist, -60, 60)
            l_wrist = constrain(l_wrist, -60, 60)
            #手臂进行运动
            set_servo_angle(0, 0, r_claw, l_claw, r_shoulder, l_shoulder, r_elbow, l_elbow, r_wrist, l_wrist)
        #机器升降
        #升降条件为按键触发，或者是机器正处于升降状态
        if joyData.buttons[6] + joyData.buttons[7] > 0 or bodyflag is 1:
            if joyData.buttons[6] is 1:
                body_up()
                bodyflag = 1
            elif joyData.buttons[7] is 1:
                body_down()
                bodyflag = 1
            else:
                body_stop()
                bodyflag = 0
        rospy.sleep(0.2)

if __name__ == "__main__":
    rospy.init_node("joy_test")
    print "手柄控制：方向键控制前进后退左右平移，左摇杆控制前进后退左右旋转，R2为油门，L1/L2+x/y/b/a控制左肩肘腕爪，R1/R2+x/y/b/a控制右" \
          "肩肘腕爪，back控制上升，start控制下降，电源键控制复位,L2急停"
    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    joyData = Joy()
    pub = rospy.Subscriber("/joy", Joy, joy_callback)
    bodyflag = 0
    joy_loop()

    rospy.spin()
