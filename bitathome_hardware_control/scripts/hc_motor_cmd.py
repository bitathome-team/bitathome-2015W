#!/usr/bin/env python
# coding=utf-8
# Filename : hc_cmd_interface.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 电机驱动和码盘数据的发布
# History
#   2014/11/16 21:44 : 创建文件 [刘达远]


import rospy
from hc_serialport_communication import Communtcation
from bitathome_hardware_control.srv import *
import math


node_name = "hc_motor_cmd"  # 节点名称
serial_name = "/dev/ttyUSB0"  # 串口名称
max_wheel_speed = 1500  # 最大电机转速


def run():

    rospy.init_node(node_name)  # 初始化节点
    r = rospy.Rate(50)  # 50Hz

    # 开启服务
    # rospy.Service("/hc_cmd_interface/motor_speed", MotorSpeed, handler_motor)  # 电机
    # rospy.loginfo("Open /hc_cmd_interface/motor_speed successful ^_^")
    rospy.Service("/hc_motor_cmd/vector_speed", VectorSpeed, handler_vector)  # 向量
    rospy.loginfo("Open /hc_motor_cmd/vector_speed successful ^_^")

    rospy.spin()



# 以三个转速控制机器运动
'''
def handler_motor(data):
    """
    :param data: 三个轮子的速度
    :return: 成功命令返回True, 速度过大或失败返回False
    """
    sv1 = data.left
    sv2 = data.right
    sv3 = data.behind
    buf = [0x55, 0xaa, 0x38, 0x0a, 0x08, 0x70]
    rospy.loginfo("left:%d right:%d behind:%d" % (sv1, sv2, sv3))
    #55 AA 38 0A 08 70 1H 1L 2H 2L 3H 3L 4H 4L 5H 5L

    if math.fabs(sv1) > max_wheel_speed or math.fabs(sv2) > max_wheel_speed or math.fabs(sv3) > max_wheel_speed:
        rospy.loginfo("You fly too low!!! ⊙_⊙")
        return False

    buf.extend(split_hl(sv1))
    buf.extend(split_hl(sv2))
    buf.extend(split_hl(sv3))
    buf.extend([0, 0, 0, 0])
    buf.append(solve_sum(buf))
    if link.write(buf):
        return True
    return False
'''


# 以向量和角速度控制机器运动
def handler_vector(data):
    """
    :param data: 三个轮子的速度
    :return: 成功命令返回True, 速度过大或失败返回False
    """
    sx = data.x
    sy = data.y
    theta = data.theta
    sv1 = int((sx * math.sqrt(3) - sy + theta) / 3)
    sv2 = int(- (sx * math.sqrt(3) + sy - theta) / 3)
    sv3 = int((2 * sy + theta) / 3)
    buf = [0x55, 0xaa, 0x38, 0x0a, 0x08, 0x70]
    rospy.loginfo("X:%d Y:%d Theta:%d" % (sx, sy, theta))
    #55 AA 38 0A 08 70 1H 1L 2H 2L 3H 3L 4H 4L 5H 5L

    if math.fabs(sv1) > max_wheel_speed or math.fabs(sv2) > max_wheel_speed or math.fabs(sv3) > max_wheel_speed:
        rospy.loginfo("You fly too low!!! ⊙_⊙")
        return False

    buf.extend(split_hl(sv1))
    buf.extend(split_hl(sv2))
    buf.extend(split_hl(sv3))
    buf.extend([0, 0, 0, 0])
    buf.append(solve_sum(buf))
    if link.write(buf):
        return True
    return False


# 将一个16位的int型数拆成两个8位的
def split_hl(item):
    item &= 0xffff
    result = [(item & 0xff00) >> 8, item & 0xff]
    return result


# 求校验和
def solve_sum(buf):
    sum_m = 0
    for it in buf:
        sum_m += it
    sum_m &= 0xff
    return sum_m


if __name__ == '__main__':

    link = Communtcation(serial_name, 2000000, 8)  # 串口链接

    if link.open():
        run()
    else:
        rospy.loginfo("Open serialport %s fail" % (serial_name))
        exit(0)
        link.close()
