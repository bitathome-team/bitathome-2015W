#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Point
from bitathome_remote_control.srv import say
from bitathome_navigation_control.msg import *
import socket
import traceback

port = 23333	# server port
links = 1		# max link
things = ["", "big apple", "English book", "black tea", "small cup"]
goal = list()

if __name__ == '__main__':
	shopping_pub = rospy.Publisher('Kinect/Shopping_point', MovePoint, queue_size=10)
        style_pub = rospy.Publisher('Kinect/Style', Point, queue_size=10)
        say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
	rospy.init_node('netPublisher', anonymous=True)
        key = True
        count = 0
        ret = MovePoint()
        rep = Point()
	rate = rospy.Rate(30) 
	rospy.loginfo("Initializing socket...")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('', port))
	rospy.loginfo("Ready!")
	while not rospy.is_shutdown():
		try:
			buf,(r_ip, r_port) = sock.recvfrom(1024)
			# print(buf, r_ip, r_port)
			buf = buf.split(" ")
			if buf[0] == "xy" and key:
                                # rospy.loginfo("xy")
				ret.x = float(buf[1])
				ret.y = float(buf[2])
				ret.z = float(buf[3])
                                ret.time = 0
				shopping_pub.publish(ret)
                                rate.sleep()
                        elif buf[0] == "stop" and key:
                                # rospy.loginfo("stop")
                                rep.x = rep.y = rep.z = 1
                                style_pub.publish(rep)
                                rate.sleep()
                        elif buf[0] == "stop1" and key:
                                # rospy.loginfo("stop1")
                                rep.x = rep.y = rep.z = 1
                                style_pub.publish(rep)
                                say_ser("Why you stop me?")
                                rate.sleep()
                        elif buf[0] == "turn" and key:
                                if buf[1] == "left":
                                    # rospy.loginfo("turn left")
                                    rep.x = rep.y = rep.z = 2
                                else:
                                    # rospy.loginfo("turn right")
                                    rep.x = rep.y = rep.z = -2
                                style_pub.publish(rep)
                        elif buf[0] == "left" and key:
                                rospy.loginfo("left " + buf[1])
                                ret.x = ret.y = ret.z = ret.time = int(buf[1])
                                say_ser("the " + things[int(buf[1])] + " on my left?")
                        elif buf[0] == "right" and key:
                                rospy.loginfo("right " + buf[1])
                                ret.x = ret.y = ret.z = ret.time = 0 - int(buf[1])
                                say_ser("the " + things[int(buf[1])] + " on my right?")
                        elif buf[0] == "yes1" and key:
                                rospy.loginfo("yes1")
                                shopping_pub.publish(ret)
                                say_ser("OK, I remember it.")
                                rospy.sleep(1)
                                rep.x = rep.y = rep.z = 0
                                style_pub.publish(rep)
                        elif buf[0] == "no" and key:
                                rospy.loginfo("no")
                                say_ser("Could you speak again?")
                        elif buf[0] == "restart":
                                # rospy.loginfo("restart")
                                rep.x = rep.y = rep.z = 0
                                style_pub.publish(rep)
                                rate.sleep()
                        elif buf[0] == "go" and key:
                                rospy.loginfo("go" + buf[1])
                                ret.x = ret.y = ret.z = int(buf[1])
                                ret.time = int(buf[1]) + 5
                                say_ser("the " + things[ret.x] + " for you?")
                        elif buf[0] == "yes2" and key:
                                rospy.loginfo("yes2")
                                goal.append(ret)
                                ret = MovePoint()
                                count += 1
                                if count == 3:
                                        key = False
                                        say_ser("OK, I will come back soon.")
                                        rospy.sleep(1)
                                        rep.x = rep.y = rep.z = 0
                                        style_pub.publish(rep)
                                        ret.x = ret.y = ret.z = 0
                                        ret.time = 5
                                        print("%f,%f,%f,%d" % (ret.x,ret.y,ret.z,ret.time))
                                        shopping_pub.publish(ret)
                                        print("%f,%f,%f,%d" % (goal[0].x,goal[0].y,goal[0].z,goal[0].time))
                                        shopping_pub.publish(goal[0])
                                        print("%f,%f,%f,%d" % (goal[1].x,goal[1].y,goal[1].z,goal[1].time))
                                        shopping_pub.publish(goal[1])
                                        print("%f,%f,%f,%d" % (goal[2].x,goal[2].y,goal[2].z,goal[2].time))
                                        shopping_pub.publish(goal[2])
                                        ret.time = 6
                                        print("%f,%f,%f,%d" % (ret.x,ret.y,ret.z,ret.time))
                                        shopping_pub.publish(ret)
                                else:
                                        say_ser("OK, I remember it.")
                        else:
                            pass
		except Exception,ex:
			rospy.logerr("Exception!")
			print(ex)
			traceback.print_exc()		

