#include <ros/ros.h>
#include <tf/transform_broadcaster.h>
#include <sensor_msgs/Joy.h>
#include <unistd.h>
#include <pthread.h>
float x = 0;
float y = 0;
float th = 0;
ros::Rate rate(50);
void joycallback(const sensor_msgs::Joy::ConstPtr& msg)
{
    float change = 0.1;
    float change_th = 0.1;
    if (msg->buttons[4] == 1 || msg -> buttons[5] == 1)
    {
        change = 0.025;
        change_th = 0.01;
    }
    x = x + change * msg->buttons[3] - change * msg->buttons[0];
    y = y + change * msg->buttons[2] - change * msg->buttons[1];
    th = th + change_th * msg->axes[6];
    //ROS_INFO("x:%f y:%f th:%f",x,y,th);
}

void *tf_run(void *junk){
    static tf::TransformBroadcaster br;
    tf::Transform transform;
    transform.setOrigin( tf::Vector3(x, y, 0.0) );
    tf::Quaternion q;
    q.setRPY(0, 0, th);
    transform.setRotation(q);
    br.sendTransform(tf::StampedTransform(transform, ros::Time::now(), "map", "map_map"));
    rate.sleep();
}

int main(int argc, char **argv)
{
    x = 0;
    y = 0;
    th = 0;
    ros::init(argc, argv, "joy_tf_control");
    ros::NodeHandle j;
    ros::Subscriber sub = j.subscribe("joy", 1000, joycallback);

    pthread_t thread;
    int temp;
    if ((temp = pthread_create(&thread, NULL, tf_run, NULL)) != 0) {
        ROS_INFO("tf出错!!!");
    }

    ros::spin();
    return 0;
}
