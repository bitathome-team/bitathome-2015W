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
    arr = rospy.Subscriber("arrive", Arr, run1)
    #使用语音服务
    say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
    #开始监听语音输入,
    rospy.loginfo("Ready!")
    flag = -1  # -1表示准备阶段 0表示确认命令阶段 1表示前往目的地 2表示寻找人 3表示前往人的位置 4表示开始follow 5表示停止follow
    say = ""
    action = []  # 动作集合
    buf = []
    joyKey = False
    cnt = 0
    run_flag = 0
    Input = raw_input("Enter your commond please:")
    while not rospy.is_shutdown():
        if run_flag:
            continue
        if len(Input) == 0:
            continue
        try:
            if joyKey:
                continue
            #获取指令
            if flag == -1:
                '''
                if Input.find('go') > -1 or Input.find('arrive') > -1 or  Input.find('move') > -1 or  Input.find('drive') > -1 :
                    action.append(['go',Input.find('go')])
                '''
                if Input.find('bedroom') > -1:
                    action.append(['bedroom',Input.find('bedroom')])
                if Input.find('livingroom') > -1:
                    action.append(['livingroom',Input.find('livingroom')])
                if Input.find('kichen') > -1:
                    action.append(['kichen',Input.find('kichen')])
                if Input.find('hallway') > -1:
                    action.append(['hallway',Input.find('hallway')])
                '''
                if Input.find('waving') > -1:
                    action.append(['waving',Input.find('waving')])
                if Input.find('find a person') > -1:
                    action.append(['normal',Input.find('find a person')])
                if Input.find('follow') > -1:
                    action.append(['follow',Input.find('follow')])
                if Input.find('tell the time') > -1:
                    action.append(['tellthetime',Input.find('tell the time')])
                if Input.find('tell your name') > -1:
                    action.append(['tellyourname',Input.find('tell your name')])
                if Input.find('answer') > -1:
                    action.append(['answer',Input.find('answer')])
                '''
                action.sort(key=lambda x:x[1])
                print action
                flag = 0
                continue
            # 确认命令
            if flag == 0:
                start = 0
                while start < 3:
                    if joyKey:
                        continue
                    if run_flag == 1:
                        continue
                    #到达指定地点
                    if action[start][0] == "bedroom" or action[start][0] == "livingroom" or action[start][0] == "kitchen" or action[start][0] == "hallway":
                        #start += 1
                        if action[start][0] == "bedroom":
                            print "ok"
                            goal.publish(5.197, -8.0, 0, "i,have,arrived,the,bedroom", 0)
                            start += 1
                            run_flag = 1
                            joyKey = True
                        elif action[start][0] ==  "livingroom":
                            goal.publish(7.438, -3.680, 1.57, "i,have,arrived,the,livingroom", 0)
                            start += 1
                            run_flag = 1
                            joyKey = True

                        elif action[start][0] ==  "kichen":
                            goal.publish(3.60, 0.23, 0, "i,have,arrived,the,kichen", 0)
                            start += 1
                            run_flag = 1
                            joyKey = True

                        elif action[start][0] ==  "hallway":
                            goal.publish(0.637, -8.40, 0, "i,have,arrived,the,hallway", 0)
                            start += 1
                            run_flag = 1
                            joyKey = True
                    #寻找一个挥手的人
                    elif action[start][0] == "waving":
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
                    elif action[start][0] == "normal":
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
                    elif action[start][0] == "follow":
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
                    elif action[start][0] == "tellthetime":
                        say_ser(time.strftime('The,time,is,%H,clock,%M,minutes',time.localtime(time.time())))
                        start += 1
                    elif action[start][0] == "tellyourname":
                        say_ser("My,name,is,bangbang")
                        start += 1
                    elif action[start][0] == "answer":
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
