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
#   2015/07/08 09:13 : 更改文件 [曹帅毅 马俊邦]
#   2015/07/09 20:16 : 加入丢失时kinect找回条件 [曹帅毅 马俊邦]



import rospy, math
from bitathome_hardware_control.srv import *
from sensor_msgs.msg import LaserScan
from bitathome_move_control.msg import *
from tf.msg import tfMessage
def run(data):
    global scanData
    scanData = data.ranges
    
def sf_init():
    global flag, X, Y, Curvedata
    flag = 0
    X = -1
    Y = -100
    Curvedata = -1
    
def sf_flag(sf_data):
    global start_follow
    start_follow = sf_data.sff
    if start_follow == 1:
        sf_init()

def reco_run(reco_data):
    global recoData
    recoData = reco_data

#获得机器的世界坐标
def changeTf(data):
    global tf_x, tf_y
    if data.transforms[0].child_frame_id == "base_link":
        tf_x = data.transforms[0].transform.translation.x
        tf_y = data.transforms[0].transform.translation.y

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
            judge_x = S_data * math.cos(math.radians(i * 0.5 - 135))
            judge_y = S_data * math.sin(math.radians(i * 0.5 - 135))
            cnt += 1
                
        if flag == 1:
            dx = S_data * math.cos(math.radians(i * 0.5 - 135)) - judge_x
            dy = S_data * math.sin(math.radians(i * 0.5 - 135)) - judge_y
            R = math.sqrt(dx * dx + dy * dy)
            if R < 0.05:
                #阈值
                Ck[cnt - 1].append([S_data, i])
                judge_x = S_data * math.cos(math.radians(i * 0.5 - 135))
                judge_y = S_data * math.sin(math.radians(i * 0.5 - 135))
            else :
                Ck.append([])
                Ck[cnt].append([S_data, i])
                judge_x = S_data * math.cos(math.radians(i * 0.5 - 135))
                judge_y = S_data * math.sin(math.radians(i * 0.5 - 135))
                cnt += 1
        i += 1
    Curve()
    Judge()

def Curve():
    global Ck
    Length = len(Ck)
    global Curve_data
    Curve_data = []
    Curve_data1 = []
    for i in range(0, Length - 1):
        length = len(Ck[i])
        Ck_last_x = Ck[i][length - 1][0] * math.cos(math.radians(Ck[i][length - 1][1] * 0.5 - 135))
        Ck_last_y = Ck[i][length - 1][0] * math.sin(math.radians(Ck[i][length - 1][1] * 0.5 - 135))
        Ck_first_x = Ck[i][0][0] * math.cos(math.radians(Ck[i][0][1] * 0.5 - 135))
        Ck_first_y = Ck[i][0][0] * math.sin(math.radians(Ck[i][0][1] * 0.5 - 135))
        Dk = math.sqrt((Ck_last_x - Ck_first_x) ** 2 + (Ck_last_y - Ck_first_y) ** 2) * 1.000
        Lk = 0
        for j in range(0, length - 2):
            lx = Ck[i][j][0] * math.cos(math.radians(Ck[i][j][1] * 0.5 - 135))
            ly = Ck[i][j][0] * math.sin(math.radians(Ck[i][j][1] * 0.5 - 135))
            fx = Ck[i][j + 1][0] * math.cos(math.radians(Ck[i][j + 1][1] * 0.5 - 135))
            fy = Ck[i][j + 1][0] * math.sin(math.radians(Ck[i][j + 1][1] * 0.5 - 135))
            Lk += math.sqrt((lx - fx) ** 2 + (ly - fy) ** 2)
        if Dk < 0.05:
            continue
        curve = Lk / Dk
        #curve1 = Lk / abs(Ck_first_y - Ck_last_y)
        xc = 0
        yc = 0
        if curve > 1.0 and Lk > 0.1 and Lk < 0.5:
            for k in range(0, length - 1):
                xc += Ck[i][k][0] * math.cos(math.radians(Ck[i][k][1] * 0.5 - 135))
                yc += Ck[i][k][0] * math.sin(math.radians(Ck[i][k][1] * 0.5 - 135))
            xc /= length
            yc /= length
            Curve_data.append([curve, xc, yc])
            #Curve_data1.append([curve, curve1,xc, yc])
        #print Curve_data
    ##if len(Curve_data) > 0:
        ##print Curve_data
    #print Curve_data1
def Judge_reco():
    global recoData
    global Curve_data
    Len = len(recoData)
    Reco_list = []
    ans_reco = []
    if Len == 0:
        Curve_data = None
        return None
    for i in range(0, Len):
        Reco_list.append(recoData[i])

    for i in range(Len):
        compare = Reco_list[i]
        for j in range(len(Curve_data)):
            if data.X > 0.01:
                curve = math.atan(data.Y/data.X)
            elif data.X < 0.01 and data.Y < 0:
                curve = -(math.pi - math.atan(data.Y / data.X))
            elif data.X < 0.01 and data.Y > 0:
                curve = math.pi + math.atan(data.Y / data.X)
            else:
                curve = 0
            if math.fabs(curve - compare) < math.radians(5):
                ans_reco.append(Curve_data[j])

    if len(ans_reco) == 0:
        Curve_data = None
        return None
    Curve_data = ans_reco
    return Curve_data

def Judge():
    global Curve_data, X, Y, Curvedata, flag, tf_x, tf_y, x_old, y_old
    #记录丢失前的世界坐标
    Len = len(Curve_data)
    #Judge_reco()
    minx = 1000
    ans = -1
    if X == -1:
        for i in range(0, Len - 1):
            if Curve_data[i][1] > 0.5 and Curve_data[i][1] < 1.0 and Curve_data[i][2] > -1.0 and Curve_data[i][2] < 1.0:
                if minx > math.fabs(Curve_data[i][2]):
                    ans = i
                    minx = Curve_data[i][2]
        minx = 1000
        if Len > 0.1 and ans > -1:
            X = Curve_data[ans][1]
            Y = Curve_data[ans][2]
            Curvedata = Curve_data[ans][0]

    elif X == -2:
        #Judge_reco()
        #Len = len(Curve_data)
        for i in range(0, Len):
            dis = (Curve_data[i][1] - x_old + tf_x) ** 2 + (Curve_data[i][2] - y_old + tf_y) ** 2
            if minx > dis and dis < 1.0:
                ans = i
                minx = dis
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
            flag += 1
            if flag > 100:
                x_old = tf_x + X
                y_old = tf_y + Y
                X = -2
                Y = -100
                Curvedata = None

    if X == -2:
        print "x_old: %f" % x_old
        print "y_old: %f" % y_old
        print "tf_x: %f" % tf_x
        print "tf_y: %f" % tf_y
        print x_old - tf_x
        print y_old - tf_y
        print Curvedata
        print "lost"
        pub.publish(x_old - tf_x, y_old - tf_y)
    else:
        print "tf_x:%f" % tf_x
        print "tf_y:%f" % tf_y
        print "X:%f" % X
        print "Y:%f" % Y
        print Curvedata
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
    Y = -100
    Curvedata = -1
    #获得机器的世界坐标
    tf = rospy.Subscriber("/tf", tfMessage, changeTf)
    tf_x = 0
    tf_y = 0
    x_old = 0
    y_old = 0
    #腿部数据中心点
    wait_start()
    
    rospy.spin()
