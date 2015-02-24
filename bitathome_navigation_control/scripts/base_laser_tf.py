#!/usr/bin/env python
# coding=utf-8
# Filename : base_laser_tf.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 机器主体与激光扫描仪的坐标转换
# History
# 2015/2/24 10:29 : 创建文件[刘达远]

import roslib
import rospy
import tf

#全局变量
node_name = "base_laser_tf"

#主函数
if __name__ == "__main__":
	rospy.init_node(node_name) #初始化节点

	# 广播 tf
	r = rospy.Rate(100)
	br = tf.TransformBroadcaster()
	while True:
		br.sendTransform((1, 0, 0), tf.transformations.quaternion_from_euler(0, 0, 0), rospy.Time.now(), "base_link", "laser")
		r.sleep()

	rospy.spin()
