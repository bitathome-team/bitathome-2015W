#pragma once
#include <Kinect.h>
#include <opencv2\opencv.hpp>
#define STATE_IDLE 1
#define STATE_NORMAL 0
#define WAIT_FRAME 30*10
#define	M_STATE_NULL -1				//无状态，表示就没有识别骨架，要么没有人，要么骨架丢失了
#define	M_STATE_NORMAL 0			//普通状态,未在规定角度范围内识别，但是已识别
#define	M_STATE_DOUBLE_FLAT 1		//双臂平摆
#define	M_STATE_DOUBLE_BOXING 2		//双臂k-boxing
#define	M_STATE_DOUBLE_UP 3			//双臂竖直向上
#define	M_STATE_SINGLE_FLAT 4		//单臂平摆
#define	M_STATE_SINGLE_BOXING 5		//单臂k-boxing
#define	M_STATE_SINGLE_UP 6			//单臂竖直向上
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
	
	//策略二： 相对坐标不会突变
	bool					b_firstFindBody;//标记是否是第一次发现跟踪目标
	double					d_oldTargetX;//原目标相对坐标x值
	double					d_oldTargetY;//原目标相对坐标y值
	double					d_oldAngle;
	double					d_recognizeDis;//阈值：判断跟踪目标时，与原坐标距离多少以内的人是我要跟的那个人
	
	//国内赛姿势
	int						i_state;//标记当前识别的姿势状态   有 -1（无状态），0（普通状态，双臂垂直下放），1（双臂平摆），2（双臂k-boxing），3（双臂竖直向上），4（单臂平摆），5(单臂k-boxing)，6（单臂竖直向上）
	int						i_tempState;//标记当前帧正测试识别的姿势状态，即备选状态
	int						i_counterState;//标记连续多少帧识别出该状态
	int						i_counterStateUpperBound;//连续帧上限，超过该上限，即识别该动作
	double					d_angleLeftShoulder[7];//左右手四个地方的夹角
	double					d_angleLeftElbow[7];
	double					d_angleRightElbow[7];
	double					d_angleRightShoulder[7];
	double					d_angleLeftShoulderTarget;//左右手四个地方的夹角——输出值
	double					d_angleLeftElbowTarget;
	double					d_angleRightElbowTarget;
	double					d_angleRightShoulderTarget;

	double					target_angle;//
	double					target_r;
	double					target_x;//传递给运动系统的第i个目标地点的相对坐标x值
	double					target_y;//传递给运动系统的第i个目标地点的相对坐标y值
	double					d_angle[7];//
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
	//计算三点之间的夹角
	double TurnAngle(DepthSpacePoint A,DepthSpacePoint B,DepthSpacePoint C);


	//显示图像的Mat
	cv::Mat skeletonImg;
	cv::Mat depthImg;
};

