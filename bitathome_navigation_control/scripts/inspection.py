#!/usr/bin/env python
# coding=utf-8
# Filename : navigation.py
# Author : Majunbang
# E-mail : 2803650957@qq.com
# Description : inspection的程序
# History
#    2015/07/13 20:23 : 创建文件 [马俊邦]
import rospy
import math
from bitathome_navigation_control.msg import *
from bitathome_remote_control.srv import say            # 语音（说）
import traceback
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import *

port = 23333    # server port
links = 1		# max link
def run(data):
    global scanData
    scanData = data.ranges
def run1(data):
    global flag, run_flag, joyKey
    joyKey = True
    if data.data == 1:
        flag += 1
        run_flag = 0
        print flag
        print run_flag
    joyKey = False
def run2(data):
    global buf
    buf = []
    for i in range(0, len(data.order)):
        buf.append(data.order[i])

def joy_callback(data):
    global joyData
    joyData = data

if __name__ == "__main__":
    global flag, buf, person_data, joyKey
    rospy.init_node("navigation_test")
    print "navigation_test总控程序"
    #控制启动follow
    follow = rospy.Publisher("StartFollow", sf, queue_size=10)
    goal = rospy.Publisher("/my_map/goalPoint", MyPoint, queue_size=10)
    local = rospy.Publisher("/my_map/localPoint", MyPoint, queue_size=10)
    rate = rospy.Rate(10) # 10hz
    #获取kinect的数据
    scan_pub = rospy.Subscriber("/scan", LaserScan, run)
    scanData = []
    #获取语音命令
    voice_order = rospy.Subscriber("order", order, run2)
    arr = rospy.Subscriber("arrive", Arr, run1)
    #使用语音服务
    say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
    joyData = Joy()
    pub = rospy.Subscriber("/joy", Joy, joy_callback)
    #开始监听语音输入,
    rospy.loginfo("Ready!")
    flag = -1  # -1表示等待阶段 0路径点1 1路径点3 2路径点4 3表示前往人的位置 4表示开始follow 5表示停止follow
    joyKey = False
    say = ""
    action = []  # 动作集合
    buf = []
    run_flag = 0
    while not rospy.is_shutdown():
        if joyData == Joy() or (flag == -1 and math.fabs(joyData.axes[0]) < 0.1 and math.fabs(joyData.axes[1]) < 0.1):
            continue
        try:
            if joyKey:
                continue
            #路径点1
            if flag == -1 and run_flag == 0:
                goal.publish(7, -4.5, 1.57, "I have arrived point ", 0)
                print "point 1"		
                run_flag = 1   
                joyKey = True
            # 路径点2
            if flag == 0 and run_flag == 0:
                rospy.sleep(2)
                goal.publish(-1, 0, 3.14, "", 0)
                print "point 2"
                run_flag = 1
                joyKey = True
            '''
            # 路径点3
            if flag == 1 and run_flag == 0:
                #goal.publish(4, -4, 3.14, "I have arrived point three", 0)
                print "point 3"
                run_flag = 1
                joyKey = True
            # follow
            if flag == 2:
                say_ser("when you say please follow me, i will follow. And if you say stop and waiting, i will stop")
                rospy.sleep(13)
                if buf[0] == "state" and buf[1] == "1":
                    print "start follow"
                    follow.publish(1)
                    flag = 3
            if flag == 3:
                if buf[0] == "state" and buf[1] == "0":
                    print "stop folow"
                    follow.publish(0)
                    flag = 4
                    say = "I have arrived point four"
            if flag == 4 and run_flag == 0:
                goal.publish(4, -4, 3.14, "", 0)
                run_flag = 1
            '''
        except Exception, ex:
            rospy.logerr("Exception!")
            print(ex)
            traceback.print_exc()

    rospy.spin()
