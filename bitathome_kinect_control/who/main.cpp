#include "SocketConnect.hpp"
#include <windows.h>
#include "myKinect.h"
#include <iostream>
using namespace std;

const size_t CONTENT_SIZE = 100;
const int LOST = 10;

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
	SocketSend socket(ip, port);
	char content[CONTENT_SIZE];
	CBodyBasics myKinect;
	HRESULT hr = myKinect.InitializeDefaultSensor();
	HANDLE hd = GetStdHandle(STD_OUTPUT_HANDLE);
	const char * run = "-\\|/";
	int runi[BODY_COUNT];	// Ðý×ª·ûºÅµÄ¼ÆÊý
	int jump[BODY_COUNT];	// ÌøÖ¡¼ÆÊý
	ZeroMemory(runi, sizeof(runi));
	for ( int i = 0; i < BODY_COUNT; i ++ )
	{
		printf("%d: \n", i);	// ÆÁÄ»³õÊ¼»¯
		jump[i] = LOST;			// ÌøÖ¡¼ÆÊýÉèÖÃÎª¶ªÊ§×´Ì¬
	}
	myKinect.clear = true;
	myKinect.distance = -1;
	printf("\n%s:%s\n", ip, port);
	if (SUCCEEDED(hr))
	{
		while (myKinect.distance < 1000 && myKinect.clear)
		{
			myKinect.Update();
			printf("[closed]: d=% 6.2lf c=%s\t\r", myKinect.distance/1000, (myKinect.clear?"true ":"false"));
		}
		printf("[opened]\t\t\t\t\r");
		sprintf(content, "open ");
		socket.Send(content);
		int lastclearn = 0;
		bool lastclear = !myKinect.clear;
		while (true)
		{
			myKinect.Update();
			if (lastclear != myKinect.clear)
			{
				lastclearn ++;
			}
			else
			{
				lastclearn = 0;
			}
			if (lastclearn > LOST || (lastclear && ! myKinect.clear))
			{
				lastclear = myKinect.clear;
				COORD pos;
				pos.X = 0, pos.Y = BODY_COUNT;
				SetConsoleCursorPosition(hd, pos);
				printf("[clear = %s]\t\r", (myKinect.clear?" true":"false"));
			}
			for ( int i = 0; i < BODY_COUNT; i ++ )
			{
				double x = myKinect.position[i][0], y = myKinect.position[i][1];
				bool sendflag = false;
				if ( -1 == x && -1 == y)	// ¶ªÊ§×´Ì¬
				{
					if (LOST != jump[i]) jump[i] ++;
					continue;
				}
				else						// ·Ç¶ªÊ§×´Ì¬
				{
					if (LOST == jump[i]) sendflag = true;
					jump[i] = 0;
				}
				COORD pos;
				pos.X = 0, pos.Y = i;
				SetConsoleCursorPosition(hd, pos);
				printf("%d: X= % 6.2lfm\tY=% 6.2lfm %c\r", i, x, y, run[runi[i]]);
				runi[i] = (runi[i] + 1) % 4;
				if (sendflag)
				{
					sprintf(content, "pos %.2lf %.2lf ", x, y);
					socket.Send(content);
				}
			}
		}
	}
	else
	{
		cout << "kinect initialization failed!" << endl;
		system("pause");
	}
	return 0;
}