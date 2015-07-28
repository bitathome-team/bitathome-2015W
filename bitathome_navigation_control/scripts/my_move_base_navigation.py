#!/usr/bin/env python
# coding=utf-8
# Filename : my_move_base.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Created Date : 2015/05/18 14:17
# Description : 根据给定的目标点，进行移动
# History
#   2015/05/18 14:17 : 创建文件 [刘达远]
#   2015/07/05 18:12 : 修改文件 [刘达远] : 更改获取世界坐标方式


import rospy, math, time
from bitathome_hardware_control.srv import VectorSpeed  # 电机
from bitathome_remote_control.srv import say            # 语音（说）
from bitathome_navigation_control.msg import MyPoint, Arr, sf    # 目标点信息
from tf.msg import tfMessage   # 机器当前位置
from sensor_msgs.msg import LaserScan                   # 激光数据
from tf.transformations import euler_from_quaternion    # tf角度、四元数转换
from geometry_msgs.msg import Pose                      # 坐标点
from nav_msgs.msg import OccupancyGrid


def update_feedbackData(data):
    global feedbackData
    feedbackData.position.x = data.position.x
    feedbackData.position.y = data.position.y
    feedbackData.orientation = data.orientation


def update_scanData(data):
    global scanData
    scanData = data.ranges


def update_goalPointData(data):
    global goalPointData, say_key, goalSize
    goalSize = 0.01
    goalPointData = data
    say_key = True


def updata_mapData(data):
    global mapData, pointSize, width, height, Startx, Starty
    if data.header.frame_id == "map":
        pointSize = data.info.resolution
        width = data.info.width
        height = data.info.height
        Startx = int(round(data.info.origin.position.x / pointSize + width))
        Starty = int(round(data.info.origin.position.y / pointSize + height))
        mapData = data.data[:]


def update_moveKey(data):
    global moveKey
    moveKey = data.sff

def my_move_base():
    global feedbackData, scanData, goalPointData, say_key, goalSize, mapData, pointSize, width, height, Startx, Starty, moveKey
    while not rospy.is_shutdown():
        if feedbackData == Pose() or scanData == [] or goalPointData == MyPoint() or mapData == [] or moveKey is not 0:
            continue

        continueKey = True
        # 如果已经走到目标点, 调整朝向
        if (feedbackData.position.x - goalPointData.x) ** 2 + (feedbackData.position.y - goalPointData.y) ** 2 < goalSize:
            goalSize = 0.25
            quaternion = (feedbackData.orientation.x, feedbackData.orientation.y, feedbackData.orientation.z, feedbackData.orientation.w)
            z = euler_from_quaternion(quaternion, axes='sxyz')
            if z[2] > math.pi:
                z[2] %= math.pi
                z[2] -= 2 * math.pi
            elif z[2] < 0 - math.pi:
                z[2] %= math.pi
                z[2] += 2 * math.pi
            #print z[2], goalPointData.z
            theta = z[2] - goalPointData.z
            if theta > math.pi:
                theta %= math.pi
                theta -= 2 * math.pi
            elif theta < 0 - math.pi:
                theta %= math.pi
                theta += 2 * math.pi

            #print theta
            speed = theta * 1000
            if speed < 0:
                speed = max(speed, -333)
            else:
                speed = min(speed, 333)
            if theta < 0 - 0.10:
                motor_ser(0, 0, 0-speed)
            elif theta > 0.10:
                motor_ser(0, 0, 0-speed)
            elif say_key:
                motor_ser(0, 0, 0)
                if goalPointData.say != "":
                    say_ser(goalPointData.say)
                    arrive_pub.publish(1)
                say_key = False
            else:
                motor_ser(0, 0, 0)
            continueKey = False
            continue

        if continueKey:
            # 更新目标点的相对坐标
            nowx = goalPointData.x - feedbackData.position.x
            nowy = goalPointData.y - feedbackData.position.y
            theta = 0
            if math.fabs(nowx) < 0.01:
                if nowy < 0:
                    theta = 0 - math.pi / 2
                else:
                    theta = math.pi / 2
            elif nowx > 0:
                theta = math.atan(nowy / nowx)
            else:
                if nowy > 0:
                    theta = math.atan(nowy / nowx) + math.pi
                else:
                    theta = math.atan(nowy / nowx) - math.pi
            
            quaternion = (feedbackData.orientation.x, feedbackData.orientation.y, feedbackData.orientation.z, feedbackData.orientation.w)
            z = euler_from_quaternion(quaternion, axes='sxyz')
            theta = theta - z[2]
            if theta > math.pi:
                theta %= math.pi
                theta -= 2 *math.pi
            elif theta < 0 - math.pi:
                theta %= math.pi
                theta += 2 * math.pi
    
            # 调整朝向为目标点方向
            #print theta
            speed = theta * 1000
            if speed < 0:
                speed = max(speed, -500)
            else:
                speed = min(speed, 500)
            if True:
                flag = True
                while flag:
                    i = 0
                    flag = False
                    nowx = goalPointData.x - feedbackData.position.x
                    nowy = goalPointData.y - feedbackData.position.y
                    Nowx = Startx + int(feedbackData.orientation.x / pointSize)
                    Nowy = Starty + int(feedbackData.orientation.y / pointSize)
                    for it in scanData:
                        if 140 < i < 400:
                            if 0.09 < it < 0.5 and mapData[int(Nowy + it * math.sin((i - 270) * 0.00999999977648 + z[2]) * width / pointSize) + int(Nowx + it * math.cos((i-270) * 0.00999999977648 + z[2]) / pointSize)] != 100:
                                #print mapData[int(Nowy + it * math.cos((i - 270) * 0.00999999977648)) * width + int(Nowx + it * math.sin((i-270) * 0.00999999977648))], it, i
                                flag = True
                                if i < 270:
                                    motor_ser(0, 250, speed / 2)
                                else:
                                    motor_ser(0, 0 - 250, speed / 2)
                                break
                            elif 0.09 < it < 0.30:
                                flag = True
                                if nowy > 0:
                                    motor_ser(0, 250, speed / 2)
                                else:
                                    motor_ser(0, 0 - 250, speed / 2)
                                break
                        elif 90 < i < 220:
                            if 0.09 < it < 0.35:
                                flag = True
                                motor_ser(250, 250, speed / 2)
                                break
                        elif 320 < i < 450:
                            if 0.09 < it < 0.35:
                                flag = True
                                motor_ser(250, 0 - 250, speed / 2)
                                break
                        i += 1
    
		if theta < 0 - 0.05:
                	motor_ser(250, 0, speed)
               	 	#print speed
            	elif theta > 0.03:
                	motor_ser(250, 0, speed)
                	#print speed
                else:
			motor_ser(500, 0, 0)
            rospy.sleep(0.05)            
                           

if __name__ == "__main__":
    rospy.init_node("my_move_base")
    
    motor_ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    say_ser = rospy.ServiceProxy("AudioPlay/TTS", say)
    
    feedbackData = Pose()
    scanData = list()
    goalPointData = MyPoint()
    goalSize = 0.01
    mapData = []
    moveKey = 0
    
    arrive_pub = rospy.Publisher("/arrive", Arr, queue_size=10)

    map_pub = rospy.Subscriber("/map_map", OccupancyGrid, updata_mapData)
    move_base_feedback_pub = rospy.Subscriber("/goalCoords", Pose, update_feedbackData)
    scan_pub = rospy.Subscriber("/scan", LaserScan, update_scanData)
    goalPoint_pub = rospy.Subscriber("/my_move_base/goalPoint", MyPoint, update_goalPointData)
    moveKey_pub = rospy.Subscriber("/StartFollow", sf, update_moveKey)
    
    #say_ser("I can start!")
    my_move_base()

    rospy.spin()
