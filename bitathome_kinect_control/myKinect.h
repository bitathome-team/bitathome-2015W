#pragma once
#include <Kinect.h>
#include <opencv2\opencv.hpp>
#define STATE_IDLE 1
#define STATE_NORMAL 0
#define WAIT_FRAME 30*10
// Safe release for interfaces
template<class Interface>
inline void SafeRelease(Interface *& pInterfaceToRelease)
{
	if (pInterfaceToRelease != NULL)
	{
		pInterfaceToRelease->Release();
		pInterfaceToRelease = NULL;
	}
}

class CBodyBasics
{
	//kinect 2.0 的深度空间的高*宽是 424 * 512，在官网上有说明
	static const int        cDepthWidth = 512;
	static const int        cDepthHeight = 424;

public:
	CBodyBasics();
	~CBodyBasics();
	void                    Update();//获得骨架、背景二值图和深度信息
	HRESULT                 InitializeDefaultSensor();//用于初始化kinect
	
	double					target_angle;//
	double					target_r;
	double					target_x;//传递给运动系统的目标地点的相对坐标x值
	double					target_y;//传递给运动系统的目标地点的相对坐标y值
	int						m_IBodyHeadx[7];//记录第i个body在深度图中的像素x值
	int						m_IBodyHeady[7];//记录第i个body在深度图中的像素y值
	int						BodyNum;//记录当前帧捕捉到多少body
	int						targetBodyIndex;//记录当前第i个body是目标人
	bool					m_flagIBodyIsTracked[7];//标记数组标记第i个Body是否存在
	int						m_state;//标记机器状态
	int						m_wait_count;//等待多少帧

private:
	IKinectSensor*          m_pKinectSensor;//kinect源
	ICoordinateMapper*      m_pCoordinateMapper;//用于坐标变换
	IBodyFrameReader*       m_pBodyFrameReader;//用于骨架数据读取
	IDepthFrameReader*      m_pDepthFrameReader;//用于深度数据读取
	IBodyIndexFrameReader*  m_pBodyIndexFrameReader;//用于背景二值图读取

	//通过获得到的信息，把骨架和背景二值图画出来
	void                    ProcessBody(int nBodyCount, IBody** ppBodies);
	//画骨架函数
	void DrawBone(const Joint* pJoints, const DepthSpacePoint* depthSpacePosition, JointType joint0, JointType joint1);
	//画手的状态函数
	void DrawHandState(const DepthSpacePoint depthSpacePosition, HandState handState);
	//表示
	void TargetZero();

	//显示图像的Mat
	cv::Mat skeletonImg;
	cv::Mat depthImg;
};

