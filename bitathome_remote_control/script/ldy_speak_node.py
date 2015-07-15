#!/usr/bin/env python

import rospy
import socket
import traceback
from bitathome_remote_control.msg import Follow

port = 23333	# server port
links = 1		# max link

if __name__ == '__main__':
        speak_pub = rospy.Publisher('/speak', Follow, queue_size=10)
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
			
			ret = Follow()
			ret.s = ""
			for i in buf:
				ret.s += i + " "
			print ret.s
			speak_pub.publish(ret)
		except Exception,ex:
			rospy.logerr("Exception!")
			print(ex)
			traceback.print_exc()		

