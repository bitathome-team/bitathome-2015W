#!/usr/bin/env python
# coding=utf-8
# Filename : ldy_speak.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Created Date : 2015/07/09 08:48
# Description : 根据命令, 进行说话或找人, 适应国际赛项目
# History
#   2015/07/09 08:48 : 创建文件 [刘达远]


import rospy, math, time
from bitathome_hardware_control.srv import VectorSpeed  # 电机
from bitathome_remote_control.srv import say            # 语音（说）
from sensor_msgs.msg import LaserScan                   # 激光数据
from bitathome_remote_control.msg import Follow
from bitathome_move_control.msg import FootFollow


def updata_speakData(data):
    global speakData, speakKey
    speakData = data.s
    speakKey = True

def update_scanData(data):
    global scanData
    scanData = data.ranges


def updata_footData(data):
    global footData
    footData = data


def ldy_speak():
    global speakData, speakKey, footData
    while not rospy.is_shutdown():
        if footData == FootFollow() or speakData == "":
            continue
        if footData.X == -100:
            motor_ser(0,0,300)
            speakKey = False
        elif footData.Y < 0-0.25:
            motor_ser(0,0,-300)
            speakKey = False
        elif footData.Y > 0.15:
            motor_ser(0,0,300)
            speakKey = False
        else:
            motor_ser(0,0,0)
            if speakKey:
                say_ser(speakData)
            else:
                say_ser("Can you speak again?")
            speakData = ""
        continue
        '''
        i = 0 
        mind = 1.5
        mini = -1
        for it in scanData:
            if it < mind and it > 0.5 and 20 < i < 520:
                mind = it
                mini = i
            i += 1
        print "over"
        if mini == -1:
            print "find"
            motor_ser(0,0,0-300)
            speakKey = False
        elif mini < 260:
            print "right"
            motor_ser(0,0,0-300)
            speakKey = False
        elif mini > 280:
            print "left"
            motor_ser(0,0,300)
            speakKey = False
        else:
            print "speak"
            motor_ser(0,0,0)
            if speakKey:
                say_ser(speakData)
            else:
                say_ser("Can you speak again?")
            speakData = ""
        continue
        '''


if __name__ == "__main__":
    rospy.init_node("ldy_speak")
    
    motor_ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
    
    scanData = list()
    speakData = ""
    speakKey = False
    footData = FootFollow()
    
    scan_pub = rospy.Subscriber("/scan", LaserScan, update_scanData)
    say_pub = rospy.Subscriber("/speak", Follow, updata_speakData)
    foot_pub = rospy.Subscriber("/FootFollow_topic", FootFollow, updata_footData)
    
    ldy_speak()

    rospy.spin()
