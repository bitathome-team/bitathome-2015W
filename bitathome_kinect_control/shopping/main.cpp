#include "SocketConnect.hpp"
#include "myKinect.h"
#include <iostream>

#define PI 3.1415926535898

const size_t CONTENT_SIZE = 100;

using namespace std;

int main()
{
	FILE * fp = fopen("ip.address", "r");
	if ( NULL == fp )
	{
		printf("404 - ip.address not found!\n");
		return 2;
	}
	char ip[20], port[10];
	ZeroMemory(ip, 20);
	ZeroMemory(port, 10);
	fscanf(fp, "%s%s", ip, port);
	fclose(fp);
	printf("%s\n%s\n", ip, port);
	//SocketConnect socket(ip, port);
	SocketSend socket(ip, port);
	char content[CONTENT_SIZE];

	CBodyBasics myKinect;
	HRESULT hr = myKinect.InitializeDefaultSensor();
	if (SUCCEEDED(hr)){
		for ( char flag = 1; true; flag ++ )
		{
			myKinect.Update();
			printf("x = %.2lf , y = %.2lf , ",myKinect.target_x,myKinect.target_y);
			printf("angle = %.2lf , r = %.2lf ", myKinect.target_angle / PI * 180 , myKinect.target_r);
			if ( 30 == flag )
			{
				putchar('\n');
				ZeroMemory(content, CONTENT_SIZE);
				sprintf(content, "xy %.2lf %.2lf %.2lf ", myKinect.target_x, myKinect.target_y, myKinect.target_angle / PI * 180);
				socket.Send(content);
				flag = 0;
			}
			putchar('\r');
		}
	}
	else{
		cout << "kinect initialization failed!" << endl;
		system("pause");
	}
	return 0;
}