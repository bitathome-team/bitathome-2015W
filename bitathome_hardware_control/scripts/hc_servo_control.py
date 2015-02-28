#!/usr/bin/env python
# coding=utf-8
# Filename : hc_servo_control.py
# Author : Chen Zhizhong
# Created Date : 2014/10/9 21:14
# Description : Servo controls including arms, hands & body lifter

import rospy
from bitathome_hardware_control.srv import *
from hc_serialport_communication import Communtcation
from hc_motor_cmd import solve_sum

node_name = "hc_servo_control"  # 节点名称
serial_name = "/dev/ttyUSB1"  # 串口名称
link = Communtcation(serial_name, 19200, 8)  # 串口链接


# 限制数值范围
def constrain(val, v_min, v_max):
    """
    :param val: 数值
    :param v_min: 下限
    :param v_max: 上限
    """
    if val < v_min:
        return v_min
    elif val > v_max:
        return v_max
    else:
        return val


# 抬高身体
def handle_body_up_down(srv):
    if srv.up_down_status < 0:  # 降低
        key_byte = 0xf0
    elif srv.up_down_status > 0:  # 抬高
        key_byte = 0x0f
    else:
        key_byte = 0x00

    # 设置16路IO全为输出模式
    buf = [0x55, 0xaa, 0x71, 0x02, 0x03]
    buf.extend([0xff, 0xff])
    buf.append(solve_sum(buf))
    if link.write(buf):

        # IO输出，4~7位为1,其余位为0
        buf = [0x55, 0xaa, 0x71, 0x02, 0x04]
        buf.extend([0x00, key_byte])
        buf.append(solve_sum(buf))
        if link.write(buf):
            return True
        return False

    return False


# 操控关节
def handle_servo_control(srv):
    """
    设置舵机的目标角度和运动速度
    :param srv: 头, 颈, 右爪, 左爪, 右肩, 左肩, 右肘, 左肘, 右腕, 左腕
    """
    speed = constrain(srv.speed, 0, 0xff)
    buf = [0x55, 0xaa, 0x71, 0x18, 0x01]
    data = [constrain(srv.head, -28, 22) + 128, srv.speed,
            constrain(srv.neck, -50, 50) + 77, srv.speed,
            constrain(srv.r_claw, -30, 0) + 100, srv.speed,
            constrain(srv.l_claw, -45, 0) + 120, srv.speed,
            90, srv.speed,
            90, srv.speed,
            constrain(srv.r_shoulder, 0, 70) + 90, srv.speed,
            constrain(srv.l_shoulder, -70, 0) + 90, srv.speed,
            constrain(srv.r_elbow, -75, 0) + 117, srv.speed,
            constrain(srv.l_elbow, -75, 0) + 134, srv.speed,
            constrain(srv.r_wrist, -60, 60) + 85, srv.speed,
            constrain(srv.l_wrist, -60, 60) + 80, srv.speed]
    buf.extend(data)
    buf.append(solve_sum(buf))
    if link.write(buf):
        return True
    return False


# 抬高身体
def body_up():
    rospy.wait_for_service('/hc_servo_control/body_control')
    try:
        body_control = rospy.ServiceProxy('/hc_servo_control/body_control', BodyUpDownStatus)
        body_control(1)
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e


# 降低身体
def body_down():
    rospy.wait_for_service('/hc_servo_control/body_control')
    try:
        body_control = rospy.ServiceProxy('/hc_servo_control/body_control', BodyUpDownStatus)
        body_control(-1)
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e


# 停止升降身体
def body_stop():
    rospy.wait_for_service('/hc_servo_control/body_control')
    try:
        body_control = rospy.ServiceProxy('/hc_servo_control/body_control', BodyUpDownStatus)
        body_control(0)
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e


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
    rospy.wait_for_service('/hc_servo_control/servo_control')
    try:
        servo_control = rospy.ServiceProxy('/hc_servo_control/servo_control', ServoAngle)
        servo_control(head, neck, r_claw, l_claw, r_shoulder, l_shoulder, r_elbow, l_elbow, r_wrist, l_wrist, speed)
    except rospy.ServiceException, e:
        print "Service call failed: %s" % e


if __name__ == "__main__":
    # 初始化节点
    rospy.init_node(node_name)
    link = Communtcation(serial_name, 19200, 8)  # 串口链接
    if link.open():
        rospy.Service('/hc_servo_control/servo_control', ServoAngle, handle_servo_control)  # 舵机控制服务
        rospy.Service('/hc_servo_control/body_control', BodyUpDownStatus, handle_body_up_down)
        print "Ready to set servo angle.\n"
    else:
        rospy.loginfo("Open serialport %s fail" % serial_name)
        exit(0)

    rospy.spin()
