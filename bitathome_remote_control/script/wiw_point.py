#!/usr/bin/env python
# coding=utf-8

import rospy
from geometry_msgs.msg import Point
from bitathome_remote_control.srv import say
from bitathome_navigation_control.srv import *
import socket
import traceback
import datetime

port = 23333	# server port
links = 1		# max link

if __name__ == '__main__':
        ser = rospy.ServiceProxy("/nc_move_base_server/goal_speed", MoveBasePoint)
        say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
        wiw_pub = rospy.Publisher('Kinect/wiw_point', Point, queue_size=10)
        style_pub = rospy.Publisher('Kinect/Style', Point, queue_size=10)
	rospy.init_node('netPublisher', anonymous=True)
        key = False
	rate = rospy.Rate(30) 
	rospy.loginfo("Initializing socket...")
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind(('', port))
	rospy.loginfo("Ready!")
        starttime = datetime.datetime.now()
	while not rospy.is_shutdown():
		try:
                        endtime = datetime.datetime.now()
                        if (endtime - starttime).seconds > 300:
                                while ser(0,0,0,60) == 2:
                                        pass
                                rospy.exit(0)
                            
			buf,(r_ip, r_port) = sock.recvfrom(1024)
			print(buf, r_ip, r_port)
			buf = buf.split(" ")
                        if buf[0] == "open":
                                pass
                                #ser(2,0,0,10)
                        elif buf[0] == "pos":
                                if key:
                                        ret = Point()
				        ret.x = float(buf[1])
				        ret.y = float(buf[2])
				        ret.z = 0.0
                                        rospy.logerr("GET POS X:%f Y:%f" % (ret.x, ret.y))
				        wiw_pub.publish(ret)
                                else:
                                        say_ser("Hi, what's your name?") # say hi, what's your name
                        elif buf[0] == "name":
                                name = ""
                                for it in buf:
                                    name += it + " "
                                say_ser("Is your " + name +"?") # say Is your name ...
                        elif buf[0] == "yes":
                                say_ser("I remember, enter the room please.") # say i remember you
                        elif buf[0] == "no":
                                say_ser("Could you please tell me your name again?") # say can you speak your name again
                        elif buf[0] == "go":
                                rospy.sleep(5)
                                key = True
                                ret = Point()
				ret.x = 2.0
				ret.y = 0.0
				ret.z = 0.0
				wiw_pub.publish(ret)
                                
		except Exception,ex:
			rospy.logerr("Exception!")
			print(ex)
			traceback.print_exc()		

