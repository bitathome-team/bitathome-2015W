#!/usr/bin/env python
# coding=utf-8
# Filename : navigation_test.py
# Author : Majunbang
# E-mail : 2803650957@qq.com
# Description : GPSR 的总控程序
# History
#    2015/07/19 22:55 : 创建文件 [马俊邦]
import rospy
from bitathome_hardware_control.srv import VectorSpeed
from bitathome_navigation_control.msg import *
from bitathome_remote_control.srv import say            # 语音（说）
import socket
import time
import traceback

port = 23333    # server port
links = 1		# max link

def run(data):
    global person_data
    person_data = data.reco[:]

def run1(data):
    global run_flag, joyKey
    joyKey = True
    if data.data == 1:
        run_flag = 0
        print run_flag
    joyKey = False

def run2(data):
    global buf
    buf = []
    for i in range(0, len(data.order)):
        buf.append(data.order[i])

if __name__ == "__main__":
    global flag, buf, person_data
    rospy.init_node("navigation_test")
    motor_ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    print "navigation_test总控程序"
    #控制启动follow
    follow = rospy.Publisher("/StartFollow", sf, queue_size=10)
    goal = rospy.Publisher("/my_map/goalPoint", MyPoint, queue_size=10)
    local = rospy.Publisher("/my_map/localPoint", MyPoint, queue_size=10)
    rate = rospy.Rate(10) # 10hz
    #获取kinect的数据
    person = rospy.Subscriber("person_position", person, run)
    person_data = []
    #获取语音命令
    voice_order = rospy.Subscriber("order", order, run2)
    arr = rospy.Subscriber("arrive", Arr, run1)
    #使用语音服务
    say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
    #开始监听语音输入,
    rospy.loginfo("Ready Go!")
    flag = -1  # -1表示准备阶段 0表示确认命令阶段 1表示前往目的地 2表示寻找人 3表示前往人的位置 4表示开始follow 5表示停止follow
    say = ""
    action = []  # 动作集合
    buf = []
    joyKey = False
    cnt = 0
    run_flag = 0
    #前往目标位置
    print "haha"
    rospy.sleep(3)
    goal.publish(2.239, -4.704, 1.57, "please,go,closer,to,me,and,tell,me,the,commond", 0)
    print "wuwu"
    run_flag = 1
    while not rospy.is_shutdown():
        if run_flag:
            continue
        if len(buf) == 0:
            continue
        try:
            if joyKey:
                continue
            #获取指令
            if buf[0] == "order" and flag == -1:
                cnt = int(buf[1])
                action = []
                #拆出动作集
                for i in range(0, cnt):
                    action.append(buf[i + 2])
                #拆出需要说的话
                say = "Do,you,want,me,to"
                for i in range(cnt + 2, len(buf)):
                    say += "," + buf[i]
                say += "? Please,answer,me, yes,you,are,right,or,no,you,are,wrong"
                say_ser(say)
                flag = 0
                rospy.sleep(20)
                continue
            # 确认命令
            if flag == 0:
                #print buf
                if buf[0] == "confirm":
                    #命令识别不成功
                    if buf[1] == "2":
                        #重新识别命令
                        flag = -1
                        say_ser("please,tell,me,again")
                        rospy.sleep(5)
                        continue
                    if buf[1] == "1":
                        '''
                        #前往目的地
                        flag = 1
                        #room的坐标
                        print "go room"
                        if action[1] == "bedroom":
                            goal.publish(4.5, -4, 3.14, "", 0)
                            joyKey = True
                        '''
                        say_ser("ok,i,know")
                        rospy.sleep(3)
                        start = 0
                        while start < cnt:
                            if joyKey:
                                continue
                            if run_flag:
                                continue
                            #到达指定地点
                            if action[start] == "go":
                                start += 1
                                if action[start] == "bedroom":
                                    goal.publish(5.197, -8.0, 0, "", 0)
                                    start += 1
                                    run_flag = 1
                                    joyKey = True
                                if action[start] ==  "livingroom":
                                    goal.publish(7.438, -3.680, 1.57, "", 0)
                                    start += 1
                                    run_flag = 1
                                    joyKey = True

                                if action[start] ==  "kichen":
                                    goal.publish(3.60, 0.23, 0, "", 0)
                                    start += 1
                                    run_flag = 1
                                    joyKey = True

                                if action[start] ==  "hallway":
                                    goal.publish(2.239, -4.704, 1.57, "", 0)
                                    start += 1
                                    run_flag = 1
                                    joyKey = True
                            #寻找一个挥手的人
                            elif action[start] == "waving":
                                if len(person_data) == 0:
                                    follow.publish(2)
                                    motor_ser(0,0,333)
                                    rospy.sleep(1)
                                    continue
                                else:
                                    follow.publish(0)
                                    for i in range(0, len(person_data), 3):
                                        if person_data[i + 2] == "waving":
                                            print "go waving"
                                            print float(person_data[i]) / 1000.0
                                            print float(person_data[i + 1]) / 1000.0
                                            local.publish(float(person_data[i]) / 1000.0, float(person_data[i + 1]) / 1000.0, 0, "", 1.0)
                                            joyKey = True
                                            start += 1
                                            run_flag = 1
                            #寻找一个普通人
                            elif action[start] == "normal":
                                if len(person_data) == 0:
                                    follow.publish(2)
                                    motor_ser(0,0,333)
                                    rospy.sleep(1)
                                    continue
                                else:
                                    follow.publish(0)
                                    follow.publish(0)
                                    print "go normal"
                                    print float(person_data[i]) / 1000.0
                                    print float(person_data[i + 1]) / 1000.0
                                    local.publish(float(person_data[i]) / 1000.0, float(person_data[i + 1]) / 1000.0, 0, "", 1.0)
                                    joyKey = True
                                    start += 1
                                    run_flag = 1
                            elif action[start] == "follow":
                                say_ser("when,you,say,please,follow,me, i,will,follow. And,if,you,say,stop,and,waiting, i,will,stop")
                                rospy.sleep(13)
                                if buf[0] == "state" and buf[1] == "1":
                                    print "start follow"
                                    follow.publish(1)
                                    start += 1
                                elif buf[0] == "state" and buf[1] == "0":
                                    print "stop folow"
                                    follow.publish(0)
                                    start += 1
                            elif action[start] == "tellthetime":
                                say_ser(time.strftime('The,time,is,%H,clock,%M,minutes',time.localtime(time.time())))
                                start += 1
                            elif action[start] == "tellyourname":
                                say_ser("My,name,is,bangbang")
                                start += 1
                            elif action[start] == "answer":
                                if buf == []:
                                    say_ser("Please,tell,me,your,question")
                                    rospy.sleep(8)
                                    continue
                                if buf[0] == "answer":
                                    cnt = int(buf[1])
                                    #拆出需要说的话
                                    say = "The,answer,is"
                                    for i in range(2, len(buf)):
                                        say += "," + buf[i]
                                    say_ser(say)
                                    start += 1
                                    rospy.sleep(20)
                                    continue
                            else:
                                start += 1
                else:
                    say_ser(say)
                    rospy.sleep(20)
            '''
            #寻找人
            if flag == 2:
                if len(person_data) == 0:
                    follow.publish(2)
                    motor_ser(0,0,333)
                    rospy.sleep(1)
                    continue
                elif action[2] == "waving":
                    follow.publish(0)
                    for i in range(0, len(person_data), 3):
                        if person_data[i + 2] == "waving":
                            print "go waving"
                            print float(person_data[i]) / 1000.0
                            print float(person_data[i + 1]) / 1000.0
                            local.publish(float(person_data[i]) / 1000.0, float(person_data[i + 1]) / 1000.0, 0, "", 1.0)
                            joyKey = True
                            flag = 3
                elif action[2] == "normal":
                    follow.publish(0)
                    print "go normal"
                    print float(person_data[i]) / 1000.0
                    print float(person_data[i + 1]) / 1000.0
                    local.publish(float(person_data[i]) / 1000.0, float(person_data[i + 1]) / 1000.0, 0, "", 1.0)
                    joyKey = True
                    flag = 3
            # follow
            if flag == 4:
                say_ser("when you say please follow me, i will follow. And if you say stop and waiting, i will stop")
                rospy.sleep(13)
                if buf[0] == "state" and buf[1] == "1":
                    print "start follow"
                    follow.publish(1)
                    flag = 5
            if flag == 5:
                if buf[0] == "state" and buf[1] == "0":
                    print "stop folow"
                    follow.publish(0)
                    flag = 6
            '''
        except Exception, ex:
            rospy.logerr("Exception!")
            print(ex)
            traceback.print_exc()

    rospy.spin()
