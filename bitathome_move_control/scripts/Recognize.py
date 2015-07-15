#!/usr/bin/env python

import rospy
from bitathome_move_control.msg import Recoginze
import socket
import traceback

port = 23333    # server port
links = 1		# max link

if __name__ == '__main__':
    FootFollow_reco_pub = rospy.Publisher('FootFollow_Reco', Recoginze, queue_size=10)
    rospy.init_node('FootFollow_Reco_Publisher', anonymous=True)
    rate = rospy.Rate(30)
    rospy.loginfo("Initializing socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    rospy.loginfo("Ready!")
    while not rospy.is_shutdown():
        try:
            buf, (r_ip, r_port) = sock.recvfrom(1024)
            print(buf, r_ip, r_port)
            buf = buf.split(" ")

            ret = Recoginze()
            if buf[0] == "Recoginze":
                cnt = int(buf[1])
                for i in range(cnt):
                    ret.reco.append(buf[i + 2])

            FootFollow_reco_pub.publish(ret)
        except Exception, ex:
            rospy.logerr("Exception!")
            print(ex)
            traceback.print_exc()

