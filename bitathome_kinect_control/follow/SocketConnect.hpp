/*
*	SocketConnect.hpp
*	Summary：底层socket通信支持
*	Date：20140911
*	Author：Alan Snape
*	使用方法见文件末尾的样例
*/

#ifndef _SOCKET_CONNECT_HPP
#define _SOCKET_CONNEVT_HPP

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iphlpapi.h>
#include <string>
#include <map>
#include <stdio.h>

#pragma comment(lib, "Ws2_32.lib")

class SocketConnect
{
private:

	char * host;
	char * port;

	SOCKET ConnectSocket;

	std::map<SOCKET,int> errorCode;

#	define SLEEP_TIME (500)

	int startHost()
	{
		WSADATA wsaData;
		int iResult;

		// Initialize Winsock
		iResult = WSAStartup(MAKEWORD(2,2), &wsaData);
		if (iResult != 0) 
		{
			printf("WSAStartup failed with error: %d\n", iResult);
			return 1;
		}


		struct addrinfo *result = NULL, *ptr = NULL, hints;

		ZeroMemory(&hints, sizeof(hints));
		hints.ai_family = AF_INET;
		hints.ai_socktype = SOCK_STREAM;
		hints.ai_protocol = IPPROTO_TCP;
		hints.ai_flags = AI_PASSIVE;

		// Resolve the server address and port
		iResult = getaddrinfo(NULL, port, &hints, &result);
		if ( iResult != 0 ) 
		{
			printf("getaddrinfo failed with error: %d\n", iResult);
			WSACleanup();
			return 1;
		}


		// Create a SOCKET for connecting to server
		ConnectSocket = socket(result->ai_family, result->ai_socktype, result->ai_protocol);
		if (ConnectSocket == INVALID_SOCKET) 
		{
			printf("socket failed with error: %ld\n", WSAGetLastError());
			freeaddrinfo(result);
			WSACleanup();
			return 1;
		}

		// Setup the TCP listening socket
		iResult = bind( ConnectSocket, result->ai_addr, (int)result->ai_addrlen);
		if (iResult == SOCKET_ERROR) 
		{
			printf("bind failed with error: %d\n", WSAGetLastError());
			freeaddrinfo(result);
			closesocket(ConnectSocket);
			WSACleanup();
			return 1;
		}

		freeaddrinfo(result);

		iResult = listen(ConnectSocket, SOMAXCONN);
		if (iResult == SOCKET_ERROR) 
		{
			printf("listen failed with error: %d\n", WSAGetLastError());
			closesocket(ConnectSocket);
			WSACleanup();
			return 1;
		}

		return 0;

	}
	int startClient()
	{
		WSADATA wsaData;
		int iResult;

		// Initialize Winsock
		iResult = WSAStartup(MAKEWORD(2,2), &wsaData);  //called to initiate use of WS2_32.dll.
		if ( iResult != 0 ) 
		{
			printf("WSAStartup failed: %d\n", iResult);
			return 1;
		}

		addrinfo *result = NULL,
			*ptr = NULL,
			hints;

		ZeroMemory( &hints, sizeof(hints) );
		hints.ai_family = AF_INET;  // for ipv4 only
		hints.ai_socktype = SOCK_STREAM;
		hints.ai_protocol = IPPROTO_TCP;

		// Resolve the server address and port
		iResult = getaddrinfo(host, port, &hints, &result);
		if ( iResult != 0 ) 
		{
			printf("getaddrinfo failed: %d\n", iResult);
			WSACleanup();  // WSACleanup is used to terminate the use of the WS2_32 DLL.
			return 1;
		}

		// Attempt to connect to the first address returned by
		// the call to getaddrinfo
		ptr=result;

		// Create a SOCKET for connecting to server
		ConnectSocket = socket(ptr->ai_family, ptr->ai_socktype, ptr->ai_protocol);
		if ( ConnectSocket == INVALID_SOCKET ) 
		{
			printf("Error at socket(): %ld\n", WSAGetLastError());
			freeaddrinfo(result);
			WSACleanup();  // WSACleanup is used to terminate the use of the WS2_32 DLL.
			return 1;
		}
		// Connect to server.
		for ( addrinfo * temp = result; temp; temp = temp->ai_next )
		{
			iResult = connect( ConnectSocket, ptr->ai_addr, (int)ptr->ai_addrlen);
			if ( iResult == SOCKET_ERROR ) 
			{
				closesocket(ConnectSocket);
				ConnectSocket = INVALID_SOCKET;
				continue;
			}
			else 
			{
				break;
			}
		}
		freeaddrinfo(result);

		if ( ConnectSocket == INVALID_SOCKET ) 
		{
			printf("Unable to connect to server!\n");
			WSACleanup();
			return 1;
		}

		return 0;
	}

	int acceptSocket(SOCKET * ret)
	{
		SOCKET ClientSocket = INVALID_SOCKET;

		// Accept a client socket
		ClientSocket = accept(ConnectSocket, NULL, NULL);
		if (ClientSocket == INVALID_SOCKET) 
		{
			printf("accept failed with error: %d\n", WSAGetLastError());
			closesocket(ConnectSocket);
			WSACleanup();
			return 1;
		}

		*ret = ClientSocket;
		return 0;
	}

	int sendSocket(SOCKET ConnectSocket, const char * sendbuf, int len)
	{
		int iResult;

		// Send an initial buffer
		iResult = send(ConnectSocket, sendbuf, len, 0);
		if (iResult == SOCKET_ERROR) 
		{
#	ifdef _SOCKET_CONNEVT_HPP_DEBUG
			printf("send failed: %d\n", WSAGetLastError());
#	endif
			return 1;
		}
		Sleep(SLEEP_TIME);
#	ifdef _SOCKET_CONNEVT_HPP_DEBUG
		printf("Bytes Sent: %ld\n", iResult);
#	endif
		return 0;
	}

	int receiveSocket(SOCKET ClientSocket, char * ret, int len)
	{
		int iResult = recv(ClientSocket, ret, len, 0);
		if ( iResult == 0 ) 
		{
#	ifdef _SOCKET_CONNEVT_HPP_DEBUG
			printf("Connection closing with %d\n", WSAGetLastError());
#	endif
			return 1;
		}
		else if ( iResult < 0 )
		{
#	ifdef _SOCKET_CONNEVT_HPP_DEBUG
			printf("recv failed: %d\n", WSAGetLastError());
#	endif
			return 1;
		}
		return 0;
	}

public:

	SocketConnect(char * _host, char * _port)
	{
		ConnectSocket = INVALID_SOCKET;

		int hostlen = strlen(_host)+1;
		host = new char[hostlen];
		ZeroMemory(host, hostlen);
		CopyMemory(host, _host, strlen(_host));
		int portlen = strlen(_port)+1;
		port = new char[portlen];
		ZeroMemory(port, portlen);
		CopyMemory(port, _port, strlen(_port));

		while ( startClient() );
		errorCode.clear();
	}

	SocketConnect(char * _port)
	{
		ConnectSocket = INVALID_SOCKET;

		host = NULL;
		int portlen = strlen(_port)+1;
		port = new char[portlen];
		ZeroMemory(port, portlen);
		CopyMemory(port, _port, strlen(_port));

		while ( startHost() );
		errorCode.clear();
	}

	SOCKET getNewClient()
	{
		SOCKET ret = INVALID_SOCKET;
		acceptSocket(&ret);
		return ret;
	}

	SOCKET getHost()
	{
		return ConnectSocket;
	}

	void Receive(SOCKET from, int len, char * buf)
	{
		errorCode[from] = receiveSocket(from, buf, len);
	}

	void Receive(int len, char * buf)
	{
		errorCode[ConnectSocket] = receiveSocket(ConnectSocket, buf, len);
	}

	std::string Receive(SOCKET from, int len)
	{
		char * s = new char [len];
		errorCode[from] = receiveSocket(from, s, len);
		std::string ret(s);
		delete s;
		return ret;
	}

	std::string Receive(int len)
	{
		char * s = new char [len];
		errorCode[ConnectSocket] = receiveSocket(ConnectSocket, s, len);
		std::string ret(s);
		delete s;
		return ret;
	}

	void Send(SOCKET to, char * buf, int len)
	{
		errorCode[to] = sendSocket(to, buf, len);
	}

	void Send(SOCKET to, std::string sbuf)
	{
		errorCode[to] = sendSocket(to, sbuf.c_str(), sbuf.length()+1);
	}

	void Send(char * buf, int len)
	{
		errorCode[ConnectSocket] = sendSocket(ConnectSocket, buf, len);
	}

	void Send(std::string sbuf)
	{
		errorCode[ConnectSocket] = sendSocket(ConnectSocket, sbuf.c_str(), sbuf.length()+1);
	}

	int getErrorCode(SOCKET id)
	{
		return errorCode[id];
	}

	int getErrorCode()
	{
		return errorCode[ConnectSocket];
	}

	~SocketConnect()
	{
		// shutdown the send half of the connection since no more data will be sent
		if ( host )
		{
			int iResult = shutdown(ConnectSocket, SD_SEND);
			if ( iResult == SOCKET_ERROR ) 
			{
				printf("shutdown failed: %d\n", WSAGetLastError());
				closesocket(ConnectSocket);
				WSACleanup();
			}
		}
		// cleanup
		closesocket(ConnectSocket);
		WSACleanup();

		if ( host ) delete (host);
		delete (port);
	}

};

#endif

//#define clientdebug
//#define serverdebug

#ifdef clientdebug
#	define DEFAULT_PORT "44965"
#	define DEFAULT_ADDR "127.0.0.1"
#include<iostream>
int main()
{
	// 建立通信连接
	SocketConnect socket(DEFAULT_ADDR, DEFAULT_PORT);
	std::cout<<socket.Receive(512)<<std::endl;
	std::cout<<socket.getErrorCode()<<std::endl;
	// 发送
	char s[256];
	memset(s,99,sizeof(s));
	s[255] = 0;
	socket.Send(s);
	// 接受（需要用于接收的字符串的大小）
	return 0;
}
#endif

#ifdef serverdebug
#	define DEFAULT_PORT "44965"
#include<iostream>
int main()
{
	// 建立通信连接
	SocketConnect socket(DEFAULT_PORT);
	// 获取新客户端
	SOCKET client = socket.getNewClient();
	// 接受（需要客户端socket和用于接收的字符串的大小）
	std::cout<<socket.Receive(client,512)<<std::endl;
	// 发送（需要客户端socket）
	socket.Send(client,"test");
	return 0;
}
#endif

class SocketSend
{
private:

	char * host;
	char * port;

	SOCKET ConnectSocket;
	SOCKADDR_IN addr;  

	std::map<SOCKET,int> errorCode;
	
	int startClient()
	{
		WSADATA wsa;  
	    WSAStartup(MAKEWORD(2,2),&wsa); //initial Ws2_32.dll by a process  
		if ((ConnectSocket = socket(AF_INET,SOCK_DGRAM,0)) <= 0)  
		{  
			printf("Create socket fail!\n");  
			return -1;  
		}  
		addr.sin_family = AF_INET;  
		addr.sin_addr.s_addr = inet_addr(host);  
		addr.sin_port = htons(strtol(port, NULL, 10));  
		bind(ConnectSocket,(struct sockaddr *)&addr,sizeof(addr));
		return 0;
	}

public:

	SocketSend(char * _host, char * _port)
	{
		ConnectSocket = INVALID_SOCKET;

		int hostlen = strlen(_host)+1;
		host = new char[hostlen];
		ZeroMemory(host, hostlen);
		CopyMemory(host, _host, strlen(_host));
		int portlen = strlen(_port)+1;
		port = new char[portlen];
		ZeroMemory(port, portlen);
		CopyMemory(port, _port, strlen(_port));

		while ( startClient() );
		errorCode.clear();
}

	~SocketSend()
	{
		if ( host )
		{
			delete host;
		}
		if ( port )
		{
			delete port;
		}
	    WSACleanup();   //clean up Ws2_32.dll  
	}

	void Send(std::string sbuf)
	{
		sendto(ConnectSocket, sbuf.c_str(), sbuf.length()+1, 0, (struct sockaddr *)&addr, sizeof(addr));  
	}

};
