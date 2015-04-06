#include <windows.h>
#include "myKinect.h"
#include <iostream>
using namespace std;

int main()
{
	CBodyBasics myKinect;
	HRESULT hr = myKinect.InitializeDefaultSensor();
	HANDLE hd = GetStdHandle(STD_OUTPUT_HANDLE);
	const char * run = "-\\|/";
	int runi[BODY_COUNT];
	ZeroMemory(runi, sizeof(runi));
	for ( int i = 0; i < BODY_COUNT; i ++ )
	{
		printf("%d: \n", i);
	}
	if (SUCCEEDED(hr))
	{
		while (true)
		{
			myKinect.Update();
			for ( int i = 0; i < BODY_COUNT; i ++ )
			{
				double x = myKinect.position[i][0], y = myKinect.position[i][1];
				if ( -1 == x && -1 == y )
				{
					continue;
				}
				COORD pos;
				pos.X = 0, pos.Y = i;
				SetConsoleCursorPosition(hd, pos);
				printf("%d: X= %02.2lfm\tY=%02.2lfm %c\r", i, x, y, run[runi[i]]);
				runi[i] = (runi[i] + 1) % 4;
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