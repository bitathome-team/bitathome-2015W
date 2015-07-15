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

float pi = 3.141592653589793;
int dirs[8][2] = {{1,0},{0,1},{-1,0},{0,-1},{1,1},{-1,1},{-1,-1},{1,-1}};
float euler_angles[8] = {0, pi/2, pi, 0-pi/2, pi/4, 3*pi/4, 0-3*pi/4, 0-pi/4};

geometry_msgs::Pose feedbackData, _Start;
bitathome_navigation_control::MyPoint goalData;
float scanData[541];
tpoint Now, Start, Goal;
int mapDataInit[1024*1024+100];
float pointSize = 0;
bool getKey = true, goalKey = true, feedbackKey = true, mapKey = true;
int width, height, nowPoint = 0;
std::vector<tpoint> PATH;
ros::Publisher goalPoint_pub, mapShow_pub;

int getPath() {
    getKey = true;
    if (feedbackKey || goalKey || mapKey){
        if (feedbackKey)  ROS_INFO("huai le1");
        if (goalKey) ROS_INFO("huai le2");
        if (mapKey) ROS_INFO("huai le3");
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
    double z[3];
    tf::Quaternion qq(feedbackData.orientation.x, feedbackData.orientation.y, feedbackData.orientation.z, feedbackData.orientation.w);
    tf::Matrix3x3 m(qq);
    m.getRPY(z[0], z[1], z[2]);
    double x1 , x2 , x;
    double y1, y2, y;
    for (int i = 90; i < 450; i ++) {
        x1 = scanData[i] * cos((i - 270) * 0.00999999977648 + z[2]);
        y1 = scanData[i]  * sin((i - 270) * 0.00999999977648 + z[2]);
        x2 = 0.125 * cos(z[2]);
        y2 = 0.125 * sin(z[2]);
        x = feedbackData.position.x + x1 + x2;
        y = feedbackData.position.y + y1 + y2;
        for (int ii = int(y / pointSize) + Start.y - 3; ii < int(y / pointSize) + Start.y + 3; ii ++) {
            for (int jj = int(x / pointSize) + Start.x - 3; jj < int(x / pointSize) + Start.x + 3; jj ++) {
                mapData[ii * width + jj] = 100;
            }
        }
    }
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
    ROS_INFO("start getPath");
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
        if (temp.x == Goal.x and temp.y == Goal.y){
            while (true) {
                path.push(tpath[temp.idd]);
                temp = tpath[temp.pa];
                if (temp.idd == 0){
                    break;
                }
            }
            //printf("path len is %d\n", path.size());
            int next = -1;
            while (!path.empty()) {
                if (path.front().ddir != next) {
                    PATH.push_back(path.front());
                    next = path.front().ddir;
                }
                path.pop();
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
    return 0;
}

void* map_run(void *junk){
    int start = clock() / CLOCKS_PER_SEC;
    while (ros::ok()) {
		//ROS_INFO("start");
        if (feedbackKey || goalKey || getKey || mapKey ) continue;
        if (clock() / CLOCKS_PER_SEC - start < 2) {
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
            if (abs(Now.x - PATH[nowPoint].x) < 5 && abs(Now.y - PATH[nowPoint].y) < 5 && !getKey) {
                //printf("now Point is %d\n", nowPoint);
                if (nowPoint + 1 >= PATH.size() && !getKey) {
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
    }
}

void updata_feedbackData(const tf::tfMessage::ConstPtr& data){
	//ROS_INFO("updata_feedbackData1");
    if (data->transforms[0].header.frame_id == "map" && data->transforms[0].child_frame_id == "base_link" && !mapKey){
    //if (data->transforms[0].header.frame_id == "odom" && data->transforms[0].child_frame_id == "base_link" && !mapKey){
        //ROS_INFO("updata_feedbackData");
        feedbackData.position.x = data->transforms[0].transform.translation.x;
        feedbackData.position.y = data->transforms[0].transform.translation.y;
        feedbackData.orientation = data->transforms[0].transform.rotation;
        Now.x = Start.x + int(round(feedbackData.position.x / pointSize));
        Now.y = Start.y + int(round(feedbackData.position.y / pointSize));
        //printf("%d %d", Now.x, Now.y);
        feedbackKey = false;
    } else if (data->transforms[0].header.frame_id == "map_map" && data->transforms[0].child_frame_id == "map" && !mapKey) {
        _Start.position.x = data->info.origin.position.x;
        _Start.position.y = data->info.origin.position.y;
        Start.x = int(round(_Start.position.x / pointSize + width));
        Start.y = int(round(_Start.position.y / pointSize + height));
    }
}

void updata_goalData(const bitathome_navigation_control::MyPoint::ConstPtr& data){
	//ROS_INFO("updata_goalData1");
    if (!mapKey) {
        goalKey = true;
        goalData = *data;
        Goal.x = Start.x + int(round(goalData.x / pointSize));
        Goal.y = Start.y + int(round(goalData.y / pointSize));
        goalKey = false;
        ROS_INFO("updata_goalData");
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

    ros::Subscriber feedback_pub = n.subscribe("/tf", 1000, updata_feedbackData);
    ros::Subscriber map_pub = n.subscribe("/map_map", 1000, updata_mapData);
    ros::Subscriber goal_pub = n.subscribe("my_map/goalPoint", 1000, updata_goalData);
    ros::Subscriber scan_pub = n.subscribe("/scan", 1000, updata_scanData);

    pthread_t thread;
    int temp;
    if ((temp = pthread_create(&thread, NULL, map_run, NULL)) != 0) {
        ROS_INFO("出错!!!");
    }

    ros::spin();
    return 0;
}
