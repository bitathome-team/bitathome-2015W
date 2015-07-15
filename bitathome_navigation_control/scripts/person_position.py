#!/usr/bin/env python
# coding=utf-8
# Filename : navigation_test.py
# Author : Majunbang
# E-mail : 2803650957@qq.com
# Description : 获取识别的人的坐标与状态
# History
#    2015/07/13 20:23 : 创建文件 [马俊邦]

import rospy
from bitathome_navigation_control.msg import person
import socket
import traceback

port = 23333    # server port
links = 1		# max link

if __name__ == '__main__':
    person_position_pub = rospy.Publisher('person_position', person, queue_size=10)
    rospy.init_node('person_position_Publisher', anonymous=True)
    rate = rospy.Rate(30)
    rospy.loginfo("Initializing socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    rospy.loginfo("Ready!")
    while not rospy.is_shutdown():
        try:
            buf, (r_ip, r_port) = sock.recvfrom(1024)
            #print(buf, r_ip, r_port)
            buf = buf.split(" ")
            print buf
            ret = person()
            if buf[0] == "person":
                cnt = int(buf[1])
                for i in range(2, cnt * 3 + 2):
                    ret.reco.append(buf[i])
            print ret.reco
            person_position_pub.publish(ret)
        except Exception, ex:
            rospy.logerr("Exception!")
            print(ex)
            traceback.print_exc()

