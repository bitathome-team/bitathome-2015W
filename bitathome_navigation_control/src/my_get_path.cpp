// Filename : my_get_path.cpp
// Author : AbigCarrot
// E-mail : liudayuan94@gmail.com
// Created Date : 2015/07/07 11:33
// Description : 根据文本文件创建地图, 并根据目标点, 规划路径
// History
//   2015/07/07 11:33 : 创建文件 [刘达远]

#include <ros/ros.h>
#include <tf/tfMessage.h>
#include <tf/transform_datatypes.h>
#include <tf/transform_listener.h>
#include <bitathome_navigation_control/MyPoint.h>
#include <bitathome_navigation_control/MyMap.h>
#include <geometry_msgs/Pose.h>
#include <nav_msgs/OccupancyGrid.h>
#include <sensor_msgs/LaserScan.h>
#include <math.h>
#include <queue>
#include <string>
#include <vector>
#include <time.h>
#include <unistd.h>
#include <pthread.h>

class tpoint {
   public:
    int x, y, idd, pa, ddir;
};

double pi = 3.141592653589793;
int dirs[8][2] = {{1,0},{0,1},{-1,0},{0,-1},{1,1},{-1,1},{-1,-1},{1,-1}};
float euler_angles[8] = {0, pi/2, pi, 0-pi/2, pi/4, 3*pi/4, 0-3*pi/4, 0-pi/4};

geometry_msgs::Pose feedbackData, _Start, mapStart, laserData;
bitathome_navigation_control::MyPoint goalData;
float scanData[541];
tpoint Now, Start, Goal;
int mapDataInit[1024*1024+100];
float pointSize = 0;
bool getKey = false, goalKey = true, feedbackKey = true, mapKey = true;
int width, height, nowPoint = 0;
std::vector<tpoint> PATH;
ros::Publisher goalPoint_pub, mapShow_pub, goalCoords_pub;
double mapEuler;

int getPath() {
    getKey = true;
    if (feedbackKey || goalKey || mapKey){
        if (feedbackKey)  ROS_INFO("huai le1");
        //if (goalKey) ROS_INFO("huai le2");
        //if (mapKey) ROS_INFO("huai le3");
        getKey = false;
        return 0;
    }
    int idd = 0;
    int mapData[height*width];
    std::queue<tpoint> path, q;
    std::vector<tpoint> tpath;
    PATH.clear();
    tpath.clear();
    while (!path.empty()) path.pop();
    while (!q.empty()) q.pop();
    nowPoint = 0;
    for (int i = 0; i < width * height; i ++) {
        mapData[i] = mapDataInit[i];
    }
    /*
    double z[3];
    tf::Quaternion qq(laserData.orientation.x, laserData.orientation.y, laserData.orientation.z, laserData.orientation.w);
    tf::Matrix3x3 m(qq);
    m.getRPY(z[0], z[1], z[2]);
    double x, y;
    ROS_INFO("%d %d", Start.x, Start.y);
    for (int i = 90; i < 450; i ++) {
        x = laserData.position.x + scanData[i] * cos((i - 270) * 0.00999999977648 + z[2]);
        y = laserData.position.y + scanData[i] * sin((i - 270) * 0.00999999977648 + z[2]);
        if (i == 270) ROS_INFO("%f %f %f %f", laserData.position.x, laserData.position.y, x, y);
        for (int ii = int(y / pointSize) + Start.y - 3; ii < int(y / pointSize) + Start.y + 3; ii ++) {
            for (int jj = int(x / pointSize) + Start.x - 3; jj < int(x / pointSize) + Start.x + 3; jj ++) {
                mapData[ii * width + jj] = 100;
            }
        }
    }*/
    ROS_INFO("start getPath");
    bitathome_navigation_control::MyMap mapDataPub;
    for (int i = 0; i < height * width; i ++)
        mapDataPub.data.push_back(mapData[i]);
    mapShow_pub.publish(mapDataPub);

    /*
    for (int i = 0; i < width * height; i ++) {
        printf("%d," , mapData[i]);
    }
    printf("\n");
    exit(0);
    */
    tpoint tNow, temp;
    tNow.x = Now.x;
    tNow.y = Now.y;
    tNow.idd = idd;
    idd ++;
    q.push(tNow);
    tpath.push_back(tNow);
    while (!q.empty()){
        temp = q.front();
        q.pop();
        if ((temp.x - Goal.x) * (temp.x - Goal.x) + (temp.y - Goal.y) * (temp.y - Goal.y) * 0.000625 <= goalData.ddd * goalData.ddd){
            while (true) {
                path.push(tpath[temp.idd]);
                temp = tpath[temp.pa];
                if (temp.idd == 0){
                    break;
                }
            }
            //printf("path len is %d\n", path.size());
            int next = -1;
            int nextx = 0, nexty = 0;
            while (!path.empty()) {
                temp = path.front();
                path.pop();
                if (temp.ddir != next && ((temp.x - nextx) * (temp.x - nextx) + (temp.y - nexty) * (temp.y - nexty)) > 25) {
                    PATH.push_back(temp);
                    next = temp.ddir;
                    nextx = temp.x;
                    nexty = temp.y;
                }
            }

            if (PATH[0].x == Goal.x and PATH[0].y == Goal.y);
            else {
                if (fabs(goalData.x - (PATH[nowPoint].x - Start.x) * pointSize) < 0.01)
                    if (goalData.y - (PATH[nowPoint].y - Start.y) * pointSize < 0)
                        goalData.z = 0 - pi / 2.0;
                    else
                        goalData.z = pi / 2.0;
                else if (goalData.x - (PATH[nowPoint].x - Start.x) * pointSize > 0)
                    goalData.z = atan((goalData.y - (PATH[nowPoint].y - Start.y) * pointSize) / (goalData.x - (PATH[nowPoint].x - Start.x) * pointSize));
                else if (goalData.y - (PATH[nowPoint].y - Start.y) * pointSize > 0)
                    goalData.z = atan((goalData.y - (PATH[nowPoint].y - Start.y) * pointSize) / (goalData.x - (PATH[nowPoint].x - Start.x) * pointSize)) + pi;
                else
                    goalData.z = atan((goalData.y - (PATH[nowPoint].y - Start.y) * pointSize) / (goalData.x - (PATH[nowPoint].x - Start.x) * pointSize)) - pi;
            }

            reverse(PATH.begin(),PATH.end());
            printf("PATH len is %d\n", (int)PATH.size());
            for (int i = 0; i < PATH.size(); i ++)
                printf("路径点%d: %d %d %f\n",i , PATH[i].x, PATH[i].y, euler_angles[PATH[i].ddir]);
            ROS_INFO("getPath over");
            getKey = false;

            int pathLen = PATH.size();
            if (pathLen == 1) {
                    bitathome_navigation_control::MyPoint ret;
                    ret.x = (PATH[nowPoint].x - Start.x) * pointSize;
                    ret.y = (PATH[nowPoint].y - Start.y) * pointSize;
                    ret.z = goalData.z;
                    ret.say = goalData.say;
                    goalPoint_pub.publish(ret);
            } else {
                    bitathome_navigation_control::MyPoint ret;
                    ret.x = (PATH[nowPoint].x - Start.x) * pointSize;
                    ret.y = (PATH[nowPoint].y - Start.y) * pointSize;
                    ret.z = euler_angles[PATH[nowPoint].ddir];
                    ret.say = "";
                    goalPoint_pub.publish(ret);
            }
            return pathLen;
        }

        for (int i = 0; i < 8; i ++) {
            tpoint  tson;
            tson.x = temp.x + dirs[i][0];
            tson.y = temp.y + dirs[i][1];

            if (tson.y * width + tson.x > 0 && tson.y * width + tson.x < width* height && (mapData[tson.y * width + tson.x] == 0 || (mapData[tson.y * width + tson.x] == -1 && mapDataInit[temp.y*width+temp.x] == -1))){
                tson.ddir = i;
                tson.pa = temp.idd;
                tson.idd = idd;
                idd ++;
                q.push(tson);
                tpath.push_back(tson);
                mapData[tson.y * width + tson.x] = 100;
            }
        }
    }

    PATH.clear();
    ROS_INFO("fuck");
    getKey = false;
    return 0;
}

void* map_run(void *junk){
    int start = clock() / CLOCKS_PER_SEC;
    while (ros::ok()) {
		//ROS_INFO("start");
        if (feedbackKey || goalKey || getKey || mapKey ) continue;
        if (clock() / CLOCKS_PER_SEC - start < 5) {
            /*
            if (mapDataInit[Now.y*width+Now.x] == -1) {
                start = clock() / CLOCKS_PER_SEC;
                if (getKey) continue;
                ROS_INFO("get again");
                int pathLen = getPath();
                while (getKey);
                if (pathLen == 0) {
                    ROS_INFO("I can't get there!!!");
                } else if (pathLen == 1) {
                    printf("now Point is %d\n", nowPoint);
                    bitathome_navigation_control::MyPoint ret;
                    ret.x = (PATH[nowPoint].x - Start.x) * pointSize;
                    ret.y = (PATH[nowPoint].y - Start.y) * pointSize;
                    ret.z = goalData.z;
                    ret.say = goalData.say;
                    goalPoint_pub.publish(ret);
                } else {
                    printf("now Point is %d\n", nowPoint);
                    bitathome_navigation_control::MyPoint ret;
                    ret.x = (PATH[nowPoint].x - Start.x) * pointSize;
                    ret.y = (PATH[nowPoint].y - Start.y) * pointSize;
                    ret.z = euler_angles[PATH[nowPoint].ddir];
                    ret.say = "";
                    goalPoint_pub.publish(ret);
                }
            }
            */
			//ROS_INFO("<100000");
			//printf("clock is %d", clock() / CLOCKS_PER_SEC - start);
            if (abs(Now.x - PATH[nowPoint].x) < 15 && abs(Now.y - PATH[nowPoint].y) < 15 && !getKey) {
                //printf("now Point is %d\n", nowPoint);
                if (nowPoint + 1 >= PATH.size() && !getKey) {
                    goalKey = true;
                    continue;
                }
                else if (nowPoint + 2 == PATH.size() && !getKey) {
                    printf("now Point is %d\n", nowPoint);
                    nowPoint ++;
                    bitathome_navigation_control::MyPoint ret;
                    ret.x = (PATH[nowPoint].x - Start.x) * pointSize;
                    ret.y = (PATH[nowPoint].y - Start.y) * pointSize;
                    ret.z = goalData.z;
                    ret.say = goalData.say;
                    goalPoint_pub.publish(ret);
                } else if (!getKey){
                    printf("now Point is %d\n", nowPoint);
                    nowPoint ++;
                    bitathome_navigation_control::MyPoint ret;
                    ret.x = (PATH[nowPoint].x - Start.x) * pointSize;
                    ret.y = (PATH[nowPoint].y - Start.y) * pointSize;
                    ret.z = euler_angles[PATH[nowPoint].ddir];
                    ret.say = "";
                    goalPoint_pub.publish(ret);
                }
            }
        } else {
            start = clock() / CLOCKS_PER_SEC;
            if (getKey) continue;
            //bitathome_navigation_control::MyPoint ret;
            //ret.x =  feedbackData.position.x;
            //ret.y = feedbackData.position.y;
            //double z[3];
            //tf::Quaternion q(feedbackData.orientation.x, feedbackData.orientation.y, feedbackData.orientation.z, feedbackData.orientation.w);
            //tf::Matrix3x3 m(q);
            //m.getRPY(z[0], z[1], z[2]);
            //ret.z = z[2];
            //ret.say = "";
            //goalPoint_pub.publish(ret);
			ROS_INFO("get again");
            int pathLen = getPath();
            while (getKey);
            if (pathLen == 0) {
                ROS_INFO("I can't get there!!!");
            } /*else if (pathLen == 1) {
                printf("now Point is %d\n", nowPoint);
                bitathome_navigation_control::MyPoint ret;
                ret.x = (PATH[nowPoint].x - Start.x) * pointSize;
                ret.y = (PATH[nowPoint].y - Start.y) * pointSize;
                ret.z = goalData.z;
                ret.say = goalData.say;
                goalPoint_pub.publish(ret);
            } else {
                printf("now Point is %d\n", nowPoint);
                bitathome_navigation_control::MyPoint ret;
                ret.x = (PATH[nowPoint].x - Start.x) * pointSize;
                ret.y = (PATH[nowPoint].y - Start.y) * pointSize;
                ret.z = euler_angles[PATH[nowPoint].ddir];
                ret.say = "";
                goalPoint_pub.publish(ret);
            }*/
        }
    }
}

void *updata_feedbackData(void *junk){
	//ROS_INFO("updata_feedbackData1");
	ros::Rate rate(10);
    tf::TransformListener listener;
    tf::StampedTransform transform_feedback, transform_start, transform_laser;

    while (ros::ok()) {
        try {
            listener.lookupTransform("/map", "/map_map", ros::Time(0), transform_start);
            listener.lookupTransform("/map", "/base_link", ros::Time(0), transform_feedback);
            listener.lookupTransform("/map", "/laser", ros::Time(0), transform_laser);
        } catch (tf::TransformException ex){
            ROS_ERROR("wait %s",ex.what());
            ros::Duration(5.0).sleep();
        }
        /*
        mapStart.position.x = transform_start.getOrigin().x();
        mapStart.position.y = transform_start.getOrigin().y();
        _Start.orientation.x = transform_start.getRotation().x();
        _Start.orientation.y = transform_start.getRotation().y();
        _Start.orientation.z = transform_start.getRotation().z();
        _Start.orientation.w = transform_start.getRotation().w();
        double z[3];
        tf::Quaternion qq(mapStart.orientation.x, mapStart.orientation.y, mapStart.orientation.z, mapStart.orientation.w);
        tf::Matrix3x3 m(qq);
        m.getRPY(z[0], z[1], z[2]);
        mapEuler = z[2];
        Start.x = int(round((_Start.position.x + mapStart.position.x) / pointSize + width));
        Start.y = int(round((_Start.position.y + mapStart.position.y) / pointSize + height));
        //ROS_INFO("%f %f %f %f", _Start.position.x, _Start.position.y, mapStart.position.x, mapStart.position.y);
    */

        feedbackData.position.x = transform_feedback.getOrigin().x();
        feedbackData.position.y = transform_feedback.getOrigin().y();
        feedbackData.orientation.x = transform_feedback.getRotation().x();
        feedbackData.orientation.y = transform_feedback.getRotation().y();
        feedbackData.orientation.z = transform_feedback.getRotation().z();
        feedbackData.orientation.w = transform_feedback.getRotation().w();
        Now.x = Start.x + int(round(feedbackData.position.x / pointSize));
        Now.y = Start.y + int(round(feedbackData.position.y / pointSize));
        goalCoords_pub.publish(feedbackData);

        laserData.position.x = transform_laser.getOrigin().x();
        laserData.position.y = transform_laser.getOrigin().y();
        laserData.orientation.x = transform_laser.getRotation().x();
        laserData.orientation.y = transform_laser.getRotation().y();
        laserData.orientation.z = transform_laser.getRotation().z();
        laserData.orientation.w = transform_laser.getRotation().w();

        feedbackKey = false;
        rate.sleep();
    }
}

void updata_goalData(const bitathome_navigation_control::MyPoint::ConstPtr& data) {
	//ROS_INFO("updata_goalData1");
    if (!mapKey) {
        goalKey = true;
        goalData = *data;
        Goal.x = Start.x + int(round(goalData.x / pointSize));
        Goal.y = Start.y + int(round(goalData.y / pointSize));
        goalKey = false;
        ROS_INFO("updata_goalData");
        while (getKey);
        getPath();
    }
}

void updata_goalData_local(const bitathome_navigation_control::MyPoint::ConstPtr& data) {
    if (!mapKey and !feedbackKey) {
        goalKey = true;
        double x, y, X, Y;
        x = data->x;
        y = data->y;
        double theta[3];
        tf::Quaternion qq(feedbackData.orientation.x, feedbackData.orientation.y, feedbackData.orientation.z, feedbackData.orientation.w);
        tf::Matrix3x3 m(qq);
        m.getRPY(theta[0], theta[1], theta[2]);
        X = x * cos(theta[2]) + y * sin(theta[2]);
        Y = x * sin(theta[2]) + y * sin(theta[2]);
        goalData.x = X + feedbackData.position.x;
        goalData.y = Y + feedbackData.position.y;
        goalData.ddd = data->ddd;
        goalData.z = data->z;
        goalData.say = data->say;
        Goal.x = Start.x + int(round(goalData.x / pointSize));
        Goal.y = Start.y + int(round(goalData.y / pointSize));
        goalKey = false;
        ROS_INFO("updata_goalData");
        while(getKey);
        getPath();
    }
}

void updata_mapData(const nav_msgs::OccupancyGrid::ConstPtr& data) {
    if (data->header.frame_id == "map") {
        mapKey = true;
        pointSize = data->info.resolution;
        width =  data->info.width;
        height = data->info.height;
        _Start.position.x = data->info.origin.position.x;
        _Start.position.y = data->info.origin.position.y;
        Start.x = int(round(_Start.position.x / pointSize + width));
        Start.y = int(round(_Start.position.y / pointSize + height));
        for (int i = 0; i < width * height; i ++) {
            mapDataInit[i] = data->data[i];
        }
        mapKey = false;
        ROS_INFO("updata_mapData");
    }
}

void updata_scanData(const sensor_msgs::LaserScan::ConstPtr& data) {
    for (int i = 0; i < 541; i ++) {
        scanData[i] = data->ranges[i];
    }
}

int main(int argc, char **argv) {
    ros::init(argc, argv, "my_get_path");
    ros::NodeHandle n;

    goalPoint_pub = n.advertise<bitathome_navigation_control::MyPoint>("/my_move_base/goalPoint", 1000);
    mapShow_pub = n.advertise<bitathome_navigation_control::MyMap>("/my_map_show", 1000);
    goalCoords_pub = n.advertise<geometry_msgs::Pose>("/goalCoords", 1000);

    //ros::Subscriber feedback_pub = n.subscribe("/tf", 1000, updata_feedbackData);
    ros::Subscriber map_pub = n.subscribe("/map_map", 1000, updata_mapData);
    ros::Subscriber goal_pub = n.subscribe("/my_map/goalPoint", 1000, updata_goalData);
    ros::Subscriber local_pub = n.subscribe("/my_map/localPoint", 1000, updata_goalData_local);
    ros::Subscriber scan_pub = n.subscribe("/scan", 1000, updata_scanData);

    pthread_t thread1;
    int temp;
    if ((temp = pthread_create(&thread1, NULL, updata_feedbackData, NULL)) != 0) {
        ROS_INFO("出错!!!");
    }

    pthread_t thread2;
    if ((temp = pthread_create(&thread2, NULL, map_run, NULL)) != 0) {
        ROS_INFO("出错!!!");
    }

    ros::spin();
    return 0;
}
