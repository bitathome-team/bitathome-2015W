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
	//kinect 2.0 ����ȿռ�ĸ�*���� 424 * 512���ڹ�������˵��
	static const int        cDepthWidth = 512;
	static const int        cDepthHeight = 424;

public:
	CBodyBasics();
	~CBodyBasics();
	void                    Update();//��ùǼܡ�������ֵͼ�������Ϣ
	HRESULT                 InitializeDefaultSensor();//���ڳ�ʼ��kinect
	
	double					target_angle;//
	double					target_r;
	double					target_x;//���ݸ��˶�ϵͳ��Ŀ��ص���������xֵ
	double					target_y;//���ݸ��˶�ϵͳ��Ŀ��ص���������yֵ
	int						m_IBodyHeadx[7];//��¼��i��body�����ͼ�е�����xֵ
	int						m_IBodyHeady[7];//��¼��i��body�����ͼ�е�����yֵ
	int						BodyNum;//��¼��ǰ֡��׽������body
	int						targetBodyIndex;//��¼��ǰ��i��body��Ŀ����
	bool					m_flagIBodyIsTracked[7];//��������ǵ�i��Body�Ƿ����
	int						m_state;//��ǻ���״̬
	int						m_wait_count;//�ȴ�����֡

private:
	IKinectSensor*          m_pKinectSensor;//kinectԴ
	ICoordinateMapper*      m_pCoordinateMapper;//��������任
	IBodyFrameReader*       m_pBodyFrameReader;//���ڹǼ����ݶ�ȡ
	IDepthFrameReader*      m_pDepthFrameReader;//����������ݶ�ȡ
	IBodyIndexFrameReader*  m_pBodyIndexFrameReader;//���ڱ�����ֵͼ��ȡ

	//ͨ����õ�����Ϣ���ѹǼܺͱ�����ֵͼ������
	void                    ProcessBody(int nBodyCount, IBody** ppBodies);
	//���Ǽܺ���
	void DrawBone(const Joint* pJoints, const DepthSpacePoint* depthSpacePosition, JointType joint0, JointType joint1);
	//���ֵ�״̬����
	void DrawHandState(const DepthSpacePoint depthSpacePosition, HandState handState);
	//��ʾ
	void TargetZero();

	//��ʾͼ���Mat
	cv::Mat skeletonImg;
	cv::Mat depthImg;
};

