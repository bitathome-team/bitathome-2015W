#!/usr/bin/env python
# coding=utf-8

import rospy
from geometry_msgs.msg import Point
from bitathome_remote_control.srv import say
from bitathome_remote_control.msg import Follow
import socket
import traceback

port = 23333	# server port
links = 1		# max link

if __name__ == '__main__':
        say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
        wiw_pub = rospy.Publisher('Kinect/wiw_point', Point, queue_size=10)
	follow_pub = rospy.Publisher('Kinect/Follow_point', Follow, queue_size=10)
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
                        if buf[0] == "open":
                                ret = Point()
                                ret.x = 1
                                ret.y = 0
                                ret.z = 0.0
                                wiw_pub.publish(ret)
                        elif buf[0] == "pos":
                                ret = Point()
                                ret.x = float(buf[1])
		                ret.y = float(buf[2])
			        ret.z = 0.0
	               	        wiw_pub.publish(ret)
                        elif buf[0] == "name":
                                say_ser("Are you " + buf[1] +"?") # say Is your name ...
                        elif buf[0] == "object":
                                say_ser("Do you need " + buf[1] +"?")
                        elif buf[0] == "yes1":
                                say_ser("I remember you.") # say i remember you
                                say_ser("What do you need?")
                        elif buf[0] == "yes2":
                                say_ser("I remember it.")
                                ret = Follow()
                                ret.s = "yes"
                                follow_pub.publish(ret)
                                rospy.sleep(3)
                        elif buf[0] == "no":
                                say_ser("Could you please tell me again?") # say can you speak your name again
                        elif buf[0] == "go":
                                ret = Follow()
                                ret.s = "go"
                                follow_pub.publish(ret)
                                
		except Exception,ex:
			rospy.logerr("Exception!")
			print(ex)
			traceback.print_exc()		

