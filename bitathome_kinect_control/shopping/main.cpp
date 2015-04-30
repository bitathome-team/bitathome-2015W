#include "SocketConnect.hpp"
#include "myKinect.h"
#include <iostream>

#define PI 3.1415926535898
#define SLEEP_TIME 30*10
#define ZERO_UP 5
const size_t CONTENT_SIZE = 1024;

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
	int zeroTime = 0;
	bool b_startOrder = false;
	int sleepCount = 0;
	CBodyBasics myKinect;
	HRESULT hr = myKinect.InitializeDefaultSensor();
	if (SUCCEEDED(hr)){
		for ( char flag = 1; true; flag ++ )
		{

			myKinect.Update();


			if(myKinect.i_state == M_STATE_SINGLE_BOXING){
				b_startOrder = true;
			}

			if(myKinect.i_state == M_STATE_DOUBLE_BOXING){
				sleepCount = SLEEP_TIME;

				myKinect.i_state = M_STATE_NORMAL;
				myKinect.i_tempState = M_STATE_NORMAL;
			}



			if(b_startOrder){//人已经发过开始命令了

				if(sleepCount <=0 ){//说明现在不是休息时间

					if(fabs(myKinect.target_x - 0)>=0.0001){	

						if(zeroTime == -1){//表示之前是丢失过骨架，这是第一次找回来
							printf("【restart】\n");
							ZeroMemory(content, CONTENT_SIZE);
							sprintf(content, "restart ");
							socket.Send(content);	
						}

						zeroTime = 0;//表示一旦出现丢失骨架，即可计时


						if ( 20 == flag) 
						{
							ZeroMemory(content, CONTENT_SIZE);
							sprintf(content, "xy %.2lf %.2lf %.6lf ", myKinect.target_x, myKinect.target_y, myKinect.target_angle);
							socket.Send(content);
						}
					}
					else
					{
						if( zeroTime >= 0 ){

							zeroTime++;

							if(zeroTime >= 5 && fabs(myKinect.d_oldAngle) >= 22){

								zeroTime = -1;//表示下一次找回来之前，都不会再重复记0


								ZeroMemory(content, CONTENT_SIZE);

								if(myKinect.d_oldAngle < 0){
									printf("【turn right】\n");
									sprintf(content, "turn right ");
								}
								else
								{
									printf("【turn left】\n");
									sprintf(content, "turn left ");
								}
								socket.Send(content);

							}

							if(zeroTime >= 20){
								
								zeroTime = -1;

								printf("【stop】\n");
								ZeroMemory(content, CONTENT_SIZE);
								sprintf(content, "stop ");
								socket.Send(content);							
							}
						}
					}
				}
				else//得到休息指令后休息时间不为0
				{
					sleepCount--;

					if(sleepCount == 0){//休息时间已完，回复一个restart

						printf("【restart】\n");
						ZeroMemory(content, CONTENT_SIZE);
						sprintf(content, "restart ");
						socket.Send(content);

					}
					else{//休息时间未完
						if ( sleepCount == SLEEP_TIME - 1)//如果是休息时间之后的第一次
						{
							printf("【stop】\n");
							ZeroMemory(content, CONTENT_SIZE);
							sprintf(content, "stop ");
							socket.Send(content);
						}

					}



				}
			}



			if(flag >= 20){
				printf("oldX = %.2lf,oldY = %.2lf,oldAngle=%.2lf ",myKinect.d_oldTargetX,myKinect.d_oldTargetY,myKinect.d_oldAngle);
				printf("x = %.2lf,y = %.2lf , ",myKinect.target_x,myKinect.target_y);
				printf("angle = %.2lf,r = %.2lf ", myKinect.target_angle  /PI * 180 , myKinect.target_r);
				printf(" LS = %.2lf, LE = %.2lf , RS = %.2lf , RE = %.2lf",myKinect.d_angleLeftShoulderTarget,myKinect.d_angleLeftElbowTarget,myKinect.d_angleRightShoulderTarget,myKinect.d_angleRightElbowTarget);
				printf(" state=%d,tempState=%d,count=%d,sleepCount=%d\n ",myKinect.i_state,myKinect.i_tempState,myKinect.i_counterState,sleepCount);
				flag = 0;
			}
		}
	}
	else{
		cout << "kinect initialization failed!" << endl;
		system("pause");
	}
	return 0;
}