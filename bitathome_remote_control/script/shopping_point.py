#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Point
from bitathome_remote_control.srv import say
from bitathome_navigation_control.srv import *
import socket
import traceback

port = 23333	# server port
links = 1		# max link
things = ["", "big apple", "English book", "black tea", "small cup"]
goal = list()

if __name__ == '__main__':
	shopping_pub = rospy.Publisher('Kinect/Shopping_point', MoveBasePoint, queue_size=10)
        style_pub = rospy.Publisher('Kinect/Style', Point, queue_size=10)
        say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
	rospy.init_node('netPublisher', anonymous=True)
        key = False
        count = 0
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
                        ret = MoveBasePoint()
                        rep = Point()
			if buf[0] == "xy":
				ret.x = float(buf[1])
				ret.y = float(buf[2])
				ret.z = float(buf[3])
                                ret.time = 0
				shopping_pub.publish(ret)
                                rate.sleep()
                        elif buf[0] == "stop":
                                rep.x = rep.y = rep.z = 1
                                style_pub.publish(rep)
                                say_ser("Why you stop me?")
                        elif buf[0] == "left":
                                ret.x = ret.y = ret.z = ret.time = int(buf[1])
                                say_ser("Did you say " + things[int(buf[1])] + "to my left?")
                        elif buf[0] == "right":
                                ret.x = ret.y = ret.z = ret.time = 0 - int(buf[1])
                                say_ser("Did you say " + things[int(buf[1])] + "to my right?")
                        elif buf[0] == "yes1":
                                shopping_pub.publish(ret)
                                say_ser("Okey, I remember it.")
                        elif buf[0] == "no":
                                say_ser("Could you speak again?")
                        elif buf[0] == "restart":
                                rep.x = rep.y = rep.z = 0
                                style_pub.publish(rep)
                        elif buf[0] == "go":
                                ret.x = ret.y = ret.z = int(buf[1])
                                ret.time = 5
                                say_ser("Did you order me to take the " + things[ret.x] + "?")
                        elif buf[0] == "yes2":
                                goal.append(ret)
                                count += 1
                                if count == 3:
                                        say_ser("I will come back soon.")
                                        rospy.sleep(1)
                                        shopping_pub.publish(goal[0])
                                        shopping_pub.publish(goal[1])
                                        shopping_pub.publish(goal[2])
                                else:
                                        say_ser("Okey, I remember it.")
		except Exception,ex:
			rospy.logerr("Exception!")
			print(ex)
			traceback.print_exc()		

