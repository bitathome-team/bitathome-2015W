#!/usr/bin/env python
# coding=utf-8
# Filename : follow.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Description : 根据kinect提供的目标方向,进行移动
# History
#    2015/05/08 18:31 : 创建文件 [刘达远]
#    2015/07/08 8:46  : 修改避障 [曹帅毅 马俊邦]
#    2015/07/09 20:18 : 增大速度,完善避障 [曹帅毅 马俊邦]

import rospy, math
from bitathome_hardware_control.srv import *
from bitathome_move_control.msg import *
from sensor_msgs.msg import LaserScan


def run1(data):
    global scanData
    scanData = data.ranges

def sf_flag(sf_data):
    global start_follow
    start_follow = sf_data.sff

def run2(data):
    global styleData, speed, speed_ang, ang
    if data.X < 0:
        styleData = "stop"
    elif data.X ** 2 + data.Y ** 2 < 0.09:
        styleData = "back"
    elif data.X ** 2 + data.Y ** 2 < 0.25:
        if data.Y / data.X > 0.1:
            styleData = "left"
        elif data.Y / data.X < 0 - 0.1:
            styleData = "right"
        else:
            styleData = "stop"
    else:
        if data.Y / data.X > 0.1:
            styleData = "goLeft"
        elif data.Y / data.X < 0 - 0.1:
            styleData = "goRight"
        else:
            styleData = "go"
    speed = math.atan((data.X ** 2 + data.Y ** 2) ** 0.5) * 10 - 5
    if math.fabs(data.X) > 0.01:
        speed_ang = math.atan(math.fabs(data.Y/data.X)) + 1.0
    else:
        speed_ang = 0
    if data.X > 0.01:
        ang = math.atan(data.Y/data.X)
    elif data.X < 0.01 and data.Y < 0:
        ang = -(math.pi - math.atan(data.Y / data.X))
    elif data.X < 0.01 and data.Y > 0:
        ang = math.pi + math.atan(data.Y / data.X)
    else:
        ang = 0

#求可行方向
def find_dir(dis, r):
    global base_width, ang  #机器人宽度
    sectors = []  # 存放可用的扇区
    sec = []  # 备份扇区
    flag = 0  # 用于标记是不是首个符合要求的数据
    # 找到可用的扇区并把相邻的扇区合并
    tmp = []
    for i in range(0, len(dis)):
        if dis[i] > r:
            if flag is 0:
                if i is len(dis) - 1:
                    sectors.append([i, i])
                    sec.append([i, i])
                else:
                    tmp.append(i)
                    flag = 1
            else:
                if i is len(dis) - 1:
                    tmp.append(i)
                    sectors.append(tmp)
                    sec.append(tmp)
        else:
            if flag is not 0:
                tmp.append(i - 1)
                sectors.append(tmp)
                sec.append(tmp)
                tmp = []
                flag = 0

    #print sectors
    for i in range(0, len(sectors)):
        th = math.radians((sectors[i][0] + sectors[i][1]) // 2 * 3 + 45 - 180)
        sectors[i].append(th)
    k = 0
    for i in range(0, len(sec)):
        x_begin = dis[sec[i][0]] * math.cos(math.radians(sec[i][0] * 3.0 + 45 - 180))
        y_begin = dis[sec[i][0]] * math.sin(math.radians(sec[i][0] * 3.0 + 45 - 180))
        x_end = dis[sec[i][1]] * math.cos(math.radians(sec[i][1] * 3.0 + 45 - 180))
        y_end = dis[sec[i][1]] * math.sin(math.radians(sec[i][1] * 3.0 + 45 - 180))
        width = math.sqrt((x_begin - x_end) ** 2 + (y_begin - y_end) ** 2)
        if base_width > width:
            '''
            print "距离1: %f" % dis[sec[[0]]
            print "编号1: %d" % sec[i][0]
            print "距离2: %f" % dis[sec[i][1]]
            print "编号2: %d" % sec[i][1]
            print "角度1: %f" % cos(sec[i][0] * 3.0 / 180 * pi)
            print "角度2: %f" % cos(sec[i][1] * 3.0 / 180 * pi)
            print "%f" % (dis[sec[i][0]] * cos(sec[i][0] * 3.0 / 180 * pi))
            print "%f" % (dis[sec[i][1]] * cos(sec[i][1] * 3.0 / 180 * pi))
            '''
            del sectors[i - k]
            k += 1
            continue
        # 判断矩形条件
        # 确定起始角度
        if ang < math.radians(sec[i][0] * 3 - 135):
            th_start = math.radians(sec[i][0] * 3 - 135)
        elif ang > math.radians(sec[i][1] * 3 - 135):
            th_start = math.radians(sec[i][1] * 3 - 135)
        else:
            th_start = ang
        th_real = th_start
        change = (th_start - sec[i][2]) / 10
        # 找到最合适的角度
        while sec[i][2] < th_real < th_start or th_start < th_real < sec[i][2]:

            # 矩形条件
            d = math.sqrt(r ** 2 - (base_width / 2) ** 2)  #矩形的长
            th_x_start = - base_width / 2 * math.sin(th_real)
            th_y_start = base_width / 2 * math.cos(th_real)
            th_x_end = base_width / 2 * math.sin(th_real)
            th_y_end = -base_width / 2 * math.cos(th_real)
            th_x_middle = d * math.cos(th_real)
            th_y_middle = d * math.sin(th_real)
            # 矩形直线四条边直线方程:kx-y+b = 0
            # 平行于角平分线的两条
            k1 = k2 = math.tan(th_real)
            b1 = -k1 * th_x_start + th_y_start
            b2 = -k2 * th_x_end + th_y_end
            # 垂直于角平分线的两条线
            k3 = k4 = math.tan(th_real + math.pi / 2)
            b3 = -k3 * th_x_middle + th_y_middle
            b4 = 0
            th_flag = True
            for j in range(0, len(dis)):
                th = (j * 3 + 45 - 180) * math.pi / 180
                x_tar = dis[j] * math.cos(th)
                y_tar = dis[j] * math.sin(th)
                dis1 = math.fabs(k1 * x_tar - y_tar + b1) / math.sqrt(k1 ** 2 + 1) + math.fabs(k2 * x_tar - y_tar + b2) / math.sqrt(k2 ** 2 + 1)
                dis2 = math.fabs(k3 * x_tar - y_tar + b3) / math.sqrt(k3 ** 2 + 1) + math.fabs(k4 * x_tar - y_tar + b4) / math.sqrt(k4 ** 2 + 1)
                if math.fabs(dis1 - base_width) < 0.02:
                    th_flag = False
                    break
                if math.fabs(dis2 - d) < 0.02:
                    th_flag = False
                    break
            if th_flag:
                break
            th_real -= change
        if flag is False:
            del sectors[i - k]
            k += 1
        else:
            sectors[i - k][2] = th_real
        '''
        #矩形条件
        d = math.sqrt(r ** 2 - (base_width / 2) ** 2)  #矩形的长
        #矩形直线四条边m直线方程:kx-y+b = 0
        #平行于角平分线的两条
        k1 = k2 = math.tan(sec[i][2])
        b1 = -k1 * x_begin + y_begin
        b2 = -k2 * x_end + y_end
        #垂直于角平分线的两条线
        k3 = k4 = math.tan(sec[i][2] + math.pi / 2)
        b3 = -k3 * x_begin + y_begin
        b4 = 0
        for j in range(0, len(dis)):
            th = (j * 3 + 45 - 180) * math.pi / 180
            x_tar = dis[j] * math.cos(th)
            y_tar = dis[j] * math.sin(th)
            dis1 = math.fabs(k1 * x_tar - y_tar + b1) / math.sqrt(k1 ** 2 + 1) + math.fabs(k2 * x_tar - y_tar + b2) / math.sqrt(k2 ** 2 + 1)
            dis2 = math.fabs(k3 * x_tar - y_tar + b3) / math.sqrt(k3 ** 2 + 1) + math.fabs(k4 * x_tar - y_tar + b4) / math.sqrt(k4 ** 2 + 1)
            if math.fabs(dis1 - base_width) < 0.02:
                del sectors[i - k]
                k += 1
                break
            if math.fabs(dis2 - d) < 0.02:
                del sectors[i - k]
                k += 1
                break
        '''

        '''
        if sec[i][2] <= 0:
            for j in range(0, len(dis)):
                th = (j * 3 - 90) * math.pi / 180  # 第ｊ个点的角度
                if th > sec[i][2] + math.pi / 2:
                    break
                elif th < 0 and (th < th1 or th > th2):
                    if dis[j] < 1.0 / math.sin(sec[i][2] - th):  # 有点落在矩形内
                        del sectors[i - k]
                        k += 1
                        break
                elif th > 0 and (th < th1 or th > th2):
                    if dis[j] < 1.0 / math.cos(sec[i][2] + math.pi / 2 - th):
                        del sectors[i - k]
                        k += 1
                        break
        else:
            for j in range(0, len(dis)):
                th = (j * 3 - 90) * math.pi / 180  # 第ｊ个点的角度
                if th < sec[i][2] - math.pi / 2:
                    continue
                elif th < 0 and (th < th1 or th > th2):
                    if dis[j] < 1.0 / math.sin(sec[i][2] - th):  # 有点落在矩形内
                        del sectors[i - k]
                        k += 1
                        break
                elif th > 0 and (th < th1 or th > th2):
                    if dis[j] < 1.0 * 1.2 / math.cos(sec[i][2] + math.pi / 2 - th):
                        del sectors[i - k]
                        k += 1
                        break
        '''
    return sectors

def follow_pub():
    global scanData, styleData, start_follow, ang, speed, speed_ang, speed_old
    while not rospy.is_shutdown():
        if scanData is None or styleData == "" or start_follow == 0:
            continue
        flag = False
        distance = []
        #取-135~135度，将它分为90组，每组六个数据
        for i in range(0, 541, 6):
            distance.append(scanData[i: i+6])
        #取每组中的最小值作为这组的标记值并存放到dis中
        dis = []
        for i in distance:
            tmp = 5
            for j in i:
                if (j < tmp) and (j > 0.009):
                    tmp = j
            dis.append(tmp)
        sec = []  # 用于存放得到的可行方向
        R = 1.5
        th_best = 2.0  # 最优角度
        r = 0  # 最优距离
        while R > 0.5:
            sec = find_dir(dis, R)
            if len(sec) > 0:
                for i in sec:
                    if math.fabs(i[2] - ang) < math.fabs(th_best - ang):
                        th_best = i[2]
                        r = R
            R -= 0.1
        #紧急避障
        for i in range(0, 90):
            if dis[i] < 0.35 and (15 < i < 45):
                ser(0, 400, 0)
                time = dis[14] / 2 / (0.7 / 2.5)
                if time > 0.8:
                    time = 0.8
                rospy.sleep(time)
                rospy.loginfo("front:%d" % i)
                rospy.loginfo("vx:%f" % -math.sin(math.radians(i * 3 - 135)) * 500)
                rospy.loginfo("vy:%f" % -math.cos(math.radians(i * 3 - 135)) * 500)
                flag = True
                speed_old = 0
                break
            if dis[i] < 0.4 and (45 < i < 75):
                ser(0, -400, 0)
                time = dis[74] / 2 / (0.7 / 2.5)
                if time > 0.8:
                    time = 0.8
                rospy.sleep(time)
                rospy.sleep(0.8)
                rospy.loginfo("front:%d" % i)
                rospy.loginfo( "vx:%f" % -math.sin(math.radians(i * 3 - 135)) * 500)
                rospy.loginfo("vy:%f" % -math.cos(math.radians(i * 3 - 135)) * 500)
                flag = True
                speed_old = 0
                break
            '''
            if dis[i] < 0.4 and (15 < i < 75):
                ser(0, -math.cos((i * 3 - 135) / 180 * math.pi) * 500, 0)
                rospy.loginfo ("front:%d" % i)
                rospy.loginfo( "vx:%f" % -math.sin(math.radians(i * 3 - 135)) * 500)
                rospy.loginfo ("vy:%f" % -math.cos(math.radians(i * 3 - 135)) * 500)
                flag = True
                break
            '''
            '''
            elif dis[i] < 0.4 and (i < 13 or i > 77):
                ser(-math.sin((i * 3 - 135) / 180 * math.pi) * 300, -math.cos((i * 3 - 135) / 180 * math.pi) * 300, 0)
                rospy.loginfo("back:%d" % i)
                rospy.loginfo( "vx:%f" % -math.sin(math.radians(i * 3 - 135)) * 500)
                rospy.loginfo ("vy:%f" % -math.cos(math.radians(i * 3 - 135)) * 500)
                flag = True
                break
            '''
        if flag:
            continue
        if r is 0:
            rospy.loginfo("没找着可行方向")
            ser(0, 0, ang * 100)
            flag = True
        else:
            rospy.loginfo("可行区间")
            #输出找到的最优可行区间便于调试
            sec = find_dir(dis, r)
            print sec
        if flag:
            continue
        else:
            print "最佳角度:%f" % th_best
            print "最佳距离:%f" % r
            print "目标角度:%f" % ang
            if math.fabs(th_best - ang) > 10 * math.pi / 180:  # 低于10度不转
                if styleData == "goLeft" or styleData == "goRight" or styleData == "go":
                    styleData = "goaviod"
        print styleData
        if math.fabs(speed - speed_old) > 2.0:
            speed = speed_old + (speed - speed_old) / 100
            speed_old = speed
            ang = ang / 10
        if styleData == "stop":
            ser(0, 0, 0)
        elif styleData == "go":
            ser(250*speed, 0, 0)
        elif styleData == "goRight":
            ser(250*speed, 0, -250*speed_ang)
        elif styleData == "goLeft":
            ser(250*speed, 0, 250*speed_ang)
        elif styleData == "right":
            ser(0, 0, -250*speed_ang)
        elif styleData == "left":
            ser(0, 0, 250*speed_ang)
        elif styleData == "back":
            ser(-250, 0, 0)
        elif styleData == "goaviod":
            '''
            ser(150 * speed * math.cos(th_best), 100 * speed * math.sin(th_best), 0)
            rospy.sleep(0.5)
            ser(0, 0, ang / abs(ang) * (abs(ang-th_best) + 1.0) * 350)
            rospy.sleep(0.05)
            '''
            ser(250 * speed * math.cos(th_best), 250 * speed * math.sin(th_best), ang * 400)
        print "speed:%f" % speed
        print "speed_ang:%f" % speed_ang
        rospy.sleep(0.01)


if __name__ == "__main__":
    rospy.init_node("kinect_move")

    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    scanData = list()
    styleData = ""
    speed = 0
    speed_old = 0
    speed_ang = 0
    start_follow = 0
    base_width = 0.6
    ang = 0  #目标角度
    scan_pub = rospy.Subscriber("/scan", LaserScan, run1)
    point_pub = rospy.Subscriber("FootFollow_topic", FootFollow, run2)
    start_follow = rospy.Subscriber("/StartFollow", sf, sf_flag)
    follow_pub()

    rospy.spin()
