#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Point
import socket
import traceback

port = 23333	# server port
links = 1		# max link

if __name__ == '__main__':
	pub = rospy.Publisher('Kinect/Point', Point, queue_size=10)
	rospy.init_node('netPublisher', anonymous=True)
	rate = rospy.Rate(30) 
	rospy.loginfo("Initializing socket...")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('', port))
	rospy.loginfo("Ready!")
	try:
		while not rospy.is_shutdown():
			buf,(r_ip, r_port) = sock.recvfrom(1024)
			print(buf, r_ip, r_port)
			buf = buf.split(" ")
			if buf[0] == "xy":
				ret = Point()
				ret.x = float(buf[1])
				ret.y = float(buf[2])
				pub.publish(ret)
			rate.sleep()
	except Exception,ex:
		rospy.logerr("Socket closed!")
		print(ex)
		traceback.print_exc()		

