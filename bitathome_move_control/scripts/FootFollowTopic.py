#!/usr/bin/env python
# coding=utf-8
# Filename : FootFollow.py
# Author : Csy Mjb
# E-mail : bitcsy2012@163.com
# Description : 步态跟随的初级实验
# History
#   2015/05/16 20:09 : 创建文件 [曹帅毅]
#   2015/05/20 13:55 : 更改文件 [曹帅毅 马俊邦]
#   2015/06/22 10:13 : 更改文件 [曹帅毅 马俊邦]



import rospy, math
from bitathome_hardware_control.srv import *
from sensor_msgs.msg import LaserScan
from bitathome_move_control.msg import *

def run(data):
    global scanData
    scanData = data.ranges
    
def sf_init():
    global flag, X, Y, Curvedata
    flag = 0
    X = -1
    Y = None
    Curvedata = -1
    
def sf_flag(sf_data):
    global start_follow
    start_follow = sf_data.sff
    if start_follow == 1:
        sf_init()

def reco_run(reco_data):
    global recoData
    recoData = reco_data

def wait_start():
    global start_follow
    while not rospy.is_shutdown():
        if len(scanData) == 0:
            continue
        if start_follow == 1:
            Clustering()
#点聚类    
def Clustering():
    global scanData
    global Ck
    Ck = []
    scan = []
    for i in range(len(scanData)):
        if scanData[i] < 0.09:
            if i == 0 or i == len(scanData) - 1:
                scan.append(100000)
            elif scanData[i + 1] < 0.09:
                scan.append(scanData[i - 1])
            else:
                scan.append((scanData[i - 1] + scanData[i + 1]) / 2.0)
        else:
            scan.append(scanData[i])

    i = 0
    flag = 0
    #每次聚类的判断第一个点的标志位
    cnt = 0
    #聚类集合的总数
    judge = 0
    #判断的特征点
        
    #聚类集合
    for S_data in scan:
        if flag == 0:
            Ck.append([])
            flag = 1
            Ck[cnt].append([S_data, i])
            judge_x = S_data * math.cos((i * 0.5 - 135) / 180 * math.pi)
            judge_y = S_data * math.sin((i * 0.5 - 135) / 180 * math.pi)
            cnt += 1
                
        if flag == 1:
            dx = S_data * math.cos((i * 0.5 - 135) / 180 * math.pi) - judge_x
            dy = S_data * math.sin((i * 0.5 - 135) / 180 * math.pi) - judge_y
            R = math.sqrt(dx * dx + dy * dy)
            if R < 0.05:
                #阈值
                Ck[cnt - 1].append([S_data, i])
                judge_x = S_data * math.cos((i * 0.5 - 135) / 180 * math.pi)
                judge_y = S_data * math.sin((i * 0.5 - 135) / 180 * math.pi)
            else :
                Ck.append([])
                Ck[cnt].append([S_data, i])
                judge_x = S_data * math.cos((i * 0.5 - 135) / 180 * math.pi)
                judge_y = S_data * math.sin((i * 0.5 - 135) / 180 * math.pi)
                cnt += 1
        i += 1
    Curve()
    Judge()

def Curve():
    global Ck
    Length = len(Ck)
    global Curve_data
    Curve_data = []
    for i in range(0, Length - 1):
        length = len(Ck[i])
        Ck_last_x = Ck[i][length - 1][0] * math.cos((Ck[i][length - 1][1] * 0.5 - 135) / 180 * math.pi)
        Ck_last_y = Ck[i][length - 1][0] * math.sin((Ck[i][length - 1][1] * 0.5 - 135) / 180 * math.pi)
        Ck_first_x = Ck[i][0][0] * math.cos((Ck[i][0][1] * 0.5 - 135) / 180 * math.pi)
        Ck_first_y = Ck[i][0][0] * math.sin((Ck[i][0][1] * 0.5 - 135) / 180 * math.pi)
        Dk = math.sqrt((Ck_last_x - Ck_first_x) ** 2 + (Ck_last_y - Ck_first_y) ** 2) * 1.000
        Lk = 0
        for j in range(0, length - 2):
            lx = Ck[i][j][0] * math.cos((Ck[i][j][1] * 0.5 - 135) / 180 * math.pi)
            ly = Ck[i][j][0] * math.sin((Ck[i][j][1] * 0.5 - 135) / 180 * math.pi)
            fx = Ck[i][j + 1][0] * math.cos((Ck[i][j + 1][1] * 0.5 - 135) / 180 * math.pi)
            fy = Ck[i][j + 1][0] * math.sin((Ck[i][j + 1][1] * 0.5 - 135) / 180 * math.pi)
            Lk += math.sqrt((lx - fx) ** 2 + (ly - fy) ** 2)
        if Dk < 0.001:
            continue
        curve = Lk / Dk
        xc = 0
        yc = 0
        if curve > 0.7 and Lk > 0.06 and Lk < 0.2:
            for k in range(0, length - 1):
                xc += Ck[i][k][0] * math.cos((Ck[i][k][1] * 0.5 - 135) / 180 * math.pi)
                yc += Ck[i][k][0] * math.sin((Ck[i][k][1] * 0.5 - 135) / 180 * math.pi)
            xc /= length
            yc /= length
            Curve_data.append([curve, xc, yc])

    ##if len(Curve_data) > 0:
        ##print Curve_data
def Judge_reco():
    global recoData
    global Curve_data
    Len = len(recoData)
    Reco_list = []
    ans_reco = []
    if Len == 0:
        return None
    for i in range(0, Len, 2):
        Reco_list.append([recoData[i], recoData[i + 1]])

    for i in range(Len/2):
        compare = Reco_list[i]
        for j in range(len(Curve_data)):
            L_dis = math.sqrt((Curve_data[j][1] - compare[0]) ** 2 + (Curve_data[j][2] - compare[1]) ** 2)
            if L_dis <= 0.2:
                ans_reco.append(Curve_data[j])
                break

    if len(ans_reco) == 0:
        return None

    Curve_data = ans_reco

    return Curve_data

def Judge():
    global Curve_data, X, Y, Curvedata, flag
    Len = len(Curve_data)
    #Judge_reco()
    minx = 1000
    ans = -1
    if X == -1:
        for i in range(0, Len - 1):
            if Curve_data[i][1] > 0.5 and Curve_data[i][1] < 1.0 and Curve_data[i][2] > -1.0 and Curve_data[i][2] < 1.0:
                if minx > abs(Curve_data[i][2]):
                    ans = i
                    minx = Curve_data[i][2]
        minx = 1000
        if Len > 0.1 and ans > -1:
            X = Curve_data[ans][1]
            Y = Curve_data[ans][2]
            Curvedata = Curve_data[ans][0]

    elif X == -2:
        for i in range(0, Len - 1):
            if Curve_data[i][1] > 0.5 and Curve_data[i][1] < 2.0 and Curve_data[i][2] > -1.5 and Curve_data[i][2] < 1.5:
                if minx > abs(Curve_data[i][2]):
                    ans = i
                    minx = Curve_data[i][2]
        minx = 1000
        if Len > 0.1 and ans > -1:
            flag = 0
            X = Curve_data[ans][1]
            Y = Curve_data[ans][2]
            Curvedata = Curve_data[ans][0]

    else:
        for i in range(0, Len - 1):
            L_dis = math.sqrt((Curve_data[i][1] - X) ** 2 + (Curve_data[i][2] - Y) ** 2)
            if L_dis < minx and L_dis < 0.3:
                ans = i
                minx = L_dis
        if Len > 0.1 and ans > -1:
            flag = 0
            X = Curve_data[ans][1]
            Y = Curve_data[ans][2]
            Curvedata = Curve_data[ans][0]
        else:
            flag+=1
            if flag > 150:
                X = -2
                Y = None
                Curvedata = None

    print X
    print Y
    print "over"
    pub.publish(X, Y)


if __name__ == "__main__":
    rospy.init_node("FootFollow", anonymous=True)
    #初始化节点        
    pub = rospy.Publisher("FootFollow_topic", FootFollow, queue_size=10)
    rate = rospy.Rate(10) # 10hz
    #发布话题
    ser = rospy.ServiceProxy("/hc_motor_cmd/vector_speed", VectorSpeed)
    #电机驱动
    scanData = []
    recoData = []
    start_follow = 0
    #激光数据 list()类型
    scan_pub = rospy.Subscriber("/scan", LaserScan, run)
    #Kinect数据
    #reco_pub = rospy.Subscriber("/FootFollow_Reco", Recoginze, reco_run)
    start_follow = rospy.Subscriber("/StartFollow", sf, sf_flag)
    #操作函数
    flag = 0
    X = -1
    Y = None
    Curvedata = -1
    #腿部数据中心点
    wait_start()
    
    rospy.spin()
