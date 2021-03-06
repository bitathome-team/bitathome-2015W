#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Point
import socket
import traceback
import math

port = 23333	# server port
links = 1		# max link

if __name__ == '__main__':
	follow_pub = rospy.Publisher('Kinect/Follow_point', Point, queue_size=10)
        style_pub = rospy.Publisher('Kinect/Style', Point, queue_size=10)
	rospy.init_node('netPublisher', anonymous=True)
        key = "go"
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
			if buf[0] == "xy":
                                key = "go"
				ret = Point()
				ret.x = float(buf[1])
				ret.y = float(buf[2])
				ret.z = float(buf[3])  # z direction is used for theata, which is the angle of the target
				follow_pub.publish(ret)
                                rate.sleep()
                        elif buf[0] == "stop":
                                ret = Point()
                                ret.x = ret.y = ret.z = 1
                                style_pub.publish(ret)
                        elif buf[0] == "turn" or key is not "go":
                                if key == "go":
                                    ret = Point()
                                    ret.x = ret.y = ret.z = 1
                                    style_pub.publish(ret)
                                    rospy.sleep(1)
                                    ret.x = ret.y = ret.z = 0
                                    style_pub.publish(ret)
                                if buf[1] == "left" or key == "left":
                                    key = "left"
                                    ret = Point()
				    ret.x = ret.y = 0.1414
				    ret.z = math.pi / 4 
                                    print("left")
				    follow_pub.publish(ret)
                                    rate.sleep()
                                elif buf[1] == "right" or key == "right":
                                    key = "right"
                                    ret = Point()
				    ret.x = 0.1414
                                    ret.y = 0 - 0.1414
				    ret.z = 0 - math.pi / 4  # z direction is used for theata, which is the angle of the target
				    follow_pub.publish(ret)
                                    rate.sleep()
                                # style_pub.publish(ret)
                        elif buf[0] == "restart":
                                key = "go"
                                ret = Point()
                                ret.x = ret.y = ret.z = 1
                                style_pub.publish(ret)
                                rospy.sleep(1)
                                ret = Point()
                                ret.x = ret.y = ret.z = 0
                                style_pub.publish(ret)
		except Exception,ex:
			rospy.logerr("Exception!")
			print(ex)
			traceback.print_exc()		

