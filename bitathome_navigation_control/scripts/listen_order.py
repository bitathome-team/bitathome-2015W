#!/usr/bin/env python
# coding=utf-8
# Filename : navigation_test.py
# Author : Majunbang
# E-mail : 2803650957@qq.com
# Description : 获取语音命令
# History
#    2015/07/13 20:23 : 创建文件 [马俊邦]

import rospy
from bitathome_navigation_control.msg import order
import socket
import traceback

port = 23334    # server port
links = 1		# max link

if __name__ == '__main__':
    order_pub = rospy.Publisher('order', order, queue_size=10)
    rospy.init_node('order_Publisher', anonymous=True)
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
            ret = order()
            if buf[0] == "order" or buf[0] == "confirm" or buf[0] == "state" or buf[0] == "answer":
                for i in buf:
                    ret.order.append(i)
                order_pub.publish(ret)
        except Exception, ex:
            rospy.logerr("Exception!")
            print(ex)
            traceback.print_exc()

