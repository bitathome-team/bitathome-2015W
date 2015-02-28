#!/usr/bin/env python
# coding=utf-8
# Filename : nc_move_base_server.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 接受目标点,调用move_base
# History
# 2015/2/28 11:30 : 创建文件[刘达远]

import roslib
import rospy
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion, Twist
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler
from visualization_msgs.msg import Marker
from math import radians, pi
from bitathome_navigation_control.srv import MoveBasePoint

markers = Marker()
move_base = None
cmd_vel_pub = None
marker_pub = None


def move_base_run(data):
    theta = data.z
    data.z = 0.0;
    q_angle = quaternion_from_euler(0, 0, theta, axes='sxyz')
    q = Quaternion(*q_angle)

    waypoint = Pose(data, q)
    p = waypoint.position
    markers.points.append(p)

    cmd_vel_pub = rospy.Publisher('cmd_vel', Twist)
    marker_pub = rospy.Publisher('waypoint_markers', Marker)
    
    marker_pub.publish(markers)
            
    # Intialize the waypoint goal
    goal = MoveBaseGoal()
            
    # Use the map frame to define goal poses
    goal.target_pose.header.frame_id = 'map'
            
    # Set the time stamp to "now"
    goal.target_pose.header.stamp = rospy.Time.now()
            
    # Set the goal pose to the i-th waypoint
    goal.target_pose.pose = waypoint
            
    # Start the robot moving toward the goal
    return move(goal)


def move(goal):
    # Send the goal pose to the MoveBaseAction server
    move_base.send_goal(goal)
            
    # Allow 1 minute to get there
    finished_within_time = move_base.wait_for_result(rospy.Duration(60)) 
            
    # If we don't get there in time, abort the goal
    if not finished_within_time:
        move_base.cancel_goal()
        rospy.loginfo("Timed out achieving goal!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return False
    else:
        # We made it!
        state = move_base.get_state()
        if state == GoalStatus.SUCCEEDED:
            rospy.loginfo("Goal succeeded!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            return True


def init_markers():
    # Set up our waypoint markers
    marker_scale = 0.2
    marker_lifetime = 0 # 0 is forever
    marker_ns = 'waypoints'
    marker_id = 0
    marker_color = {'r': 1.0, 'g': 0.7, 'b': 1.0, 'a': 1.0}
    
    # Define a marker publisher.
    

    # Initialize the marker points list.
    markers.ns = marker_ns
    markers.id = marker_id
    markers.type = Marker.CUBE_LIST
    markers.action = Marker.ADD
    markers.lifetime = rospy.Duration(marker_lifetime)
    markers.scale.x = marker_scale
    markers.scale.y = marker_scale
    markers.color.r = marker_color['r']
    markers.color.g = marker_color['g']
    markers.color.b = marker_color['b']
    markers.color.a = marker_color['a']
    
    markers.header.frame_id = 'odom'
    markers.header.stamp = rospy.Time.now()
    markers.points = list()


if __name__ == '__main__':
    rospy.init_node('goal_point', anonymous=False)

    move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)

    rospy.Service("/nc_move_base_server/goal_speed", MoveBasePoint, move_base_run)
    rospy.loginfo("Open /nc_move_base_server/goal_speed successful ^_^")

    init_markers()
        
    rospy.loginfo("Waiting for move_base action server...")
        
    # Wait 60 seconds for the action server to become available
    move_base.wait_for_server(rospy.Duration(60))
        
    rospy.loginfo("Connected to move base server")
    rospy.loginfo("Starting navigation test")
    
    rospy.spin()
