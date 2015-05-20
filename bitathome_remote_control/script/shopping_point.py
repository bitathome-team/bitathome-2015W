#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Point
from bitathome_remote_control.srv import say
from bitathome_navigation_control.msg import *
from bitathome_remote_control.msg import Follow
import socket
import traceback
import math

port = 23333	# server port
links = 1		# max link
goal = list()

if __name__ == '__main__':
	shopping_pub = rospy.Publisher('Kinect/Shopping_point', Follow, queue_size=10)
        say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
        things = [None for i in range(2)]
        count = 0
	rem = 0
        key = True
	rospy.init_node('netPublisher', anonymous=True)
	rate = rospy.Rate(30) 
	rospy.loginfo("Initializing socket...")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('', port))
	rospy.loginfo("Ready!")
	while not rospy.is_shutdown():
		try:
			buf,(r_ip, r_port) = sock.recvfrom(1024)
			print(buf, r_ip, r_port)
			buf = buf.split(" ")
                        if buf[0] == "object":
				things[count] = buf[1]
				say_ser(buf[1] + " ,right?")
			elif buf[0] == "get":
				if things[0] == buf[1]:
					rem = 0
				else:
					rem = 1
				say_ser("Do you need " + buf[1] + "?")
			elif buf[0] == "stop1":
                 	        ret = Follow()
                        	ret.s = "stop"
                       	 	shopping_pub.publish(ret)
                                say_ser("Why stop me?")
                                key = False
			elif buf[0] == "yes1" or buf[0] == "yes2":
				ret = Follow()
				ret.s = "save"
				shopping_pub.publish(ret)
				say_ser("OK, I remember.")
                                rospy.sleep(3)
                                key = True
                                count += 1
			elif buf[0] == "no":
				say_ser("Could you tell me again?")
			elif key:
				ret = Follow()
                        	ret.s = buf[0]
                       	 	shopping_pub.publish(ret)

		except Exception,ex:
			rospy.logerr("Exception!")
			print(ex)
			traceback.print_exc()		

