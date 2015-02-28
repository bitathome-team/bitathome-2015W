#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Point
import socket

port = 23333	# server port
links = 1		# max link

if __name__ == '__main__':
	pub = rospy.Publisher('Kinect/Point', Point, queue_size=10)
	rospy.init_node('netPublisher', anonymous=True)
	rate = rospy.Rate(30) 
	rospy.loginfo("Initializing socket...")
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('localhost', port))
	sock.listen(links)
	try:
		rospy.loginfo("Waiting for client...")
		connection,address = sock.accept()
		rospy.loginfo("Connected!")
		while not rospy.is_shutdown():
			buf = connection.recv(1024).split(" ")
			if buf[0] == "xy":
				ret = Point()
				ret.x = float(buf[1])
				ret.y = float(buf[2])
				pub.publish(ret)
			rate.sleep()
	except:
		rospy.logerr("Connection closed!")
		connection.close()
