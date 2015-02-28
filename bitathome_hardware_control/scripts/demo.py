#!/usr/bin/env python
# coding=utf-8
# Filename : hc_servo_control.py
# Author : Chen Zhizhong
# Created Date : 2014/10/9 21:14
# Description : Servo controls including arms, hands & body lifter

import time
from hc_servo_control import *

node_name = "demo"  # 节点名称


# 延时（毫秒）
def delay(delaytime_ms):
    """
    :param delaytime_ms: 延时时间（毫秒）
    :return:
    """
    time.sleep(float(delaytime_ms)/1000)


if __name__ == "__main__":
    rospy.init_node(node_name)
    # 初始化
    print "初始化"
    set_servo_angle(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    body_down()
    delay(2000)
    while True:
        set_servo_angle(0, 0, 0, 0, 0, 0, 75, -75, 0, 0)
        # 升高
        print "升高"
        body_up()
        delay(6000)
        body_stop()
        delay(7000)
        # 抬左肘
        print "抬肘"
        set_servo_angle(0, 0, 0, 0, 0, 0, 75, -75, 0, 0)
        delay(3000)

        print "抬肩膀"
        set_servo_angle(0, 0, 0, 0, 40, -40, 75, -75, 0, 0)
        delay(3000)

        print "秀爪子"
        # 合拢爪子
        set_servo_angle(0, 0, -30, -45, 40, -40, 75, -75, 0, 0)
        delay(500)
        # 松开爪子
        set_servo_angle(0, 0, 0, 0, 40, -40, 75, -75, 0, 0)
        delay(500)
        # 合拢爪子
        set_servo_angle(0, 0, -30, -45, 40, -40, 75, -75, 0, 0)
        delay(500)
        # 松开爪子
        set_servo_angle(0, 0, 0, 0, 40, -40, 75, -75, 0, 0)
        delay(500)
        # 合拢爪子
        set_servo_angle(0, 0, -30, -45, 40, -40, 75, -75, 0, 0)
        delay(500)
        # 松开爪子
        set_servo_angle(0, 0, 0, 0, 40, -40, 75, -75, 0, 0)
        delay(500)
        # 扭手腕
        set_servo_angle(0, 0, 0, 0, 40, -40, 75, -75, 60, 60)
        delay(600)
        set_servo_angle(0, 0, 0, 0, 40, -40, 75, -75, -60, -60)
        delay(800)
        set_servo_angle(0, 0, 0, 0, 40, -40, 75, -75, 0, 0)
        delay(600)
        # 扭头
        print "扭头"
        set_servo_angle(0, -30, 0, 0, 40, -40, 75, -75, 0, 0)
        delay(800)
        set_servo_angle(0, 30, 0, 0, 40, -40, 75, -75, 0, 0)
        delay(1200)
        set_servo_angle(0, 0, 0, 0, 40, -40, 75, -75, 0, 0)
        delay(800)

        print "放下肩膀"
        set_servo_angle(0, 0, 0, 0, 0, 0, 75, -75, 0, 0)
        delay(3000)
        # 放下肘
        print "放下肘"
        set_servo_angle(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        delay(3000)
        # 降低
        print "降低"
        body_down()
        delay(6000)
        body_stop()
        delay(700)
        print "演示结束。\n"