#pragma once
#include <Kinect.h>
#include <opencv2\opencv.hpp>
#define STATE_IDLE 1
#define STATE_NORMAL 0
#define WAIT_FRAME 30*10
#define	M_STATE_NULL -1				//��״̬����ʾ��û��ʶ��Ǽܣ�Ҫôû���ˣ�Ҫô�Ǽܶ�ʧ��
#define	M_STATE_NORMAL 0			//��ͨ״̬,δ�ڹ涨�Ƕȷ�Χ��ʶ�𣬵�����ʶ��
#define	M_STATE_DOUBLE_FLAT 1		//˫��ƽ��
#define	M_STATE_DOUBLE_BOXING 2		//˫��k-boxing
#define	M_STATE_DOUBLE_UP 3			//˫����ֱ����
#define	M_STATE_SINGLE_FLAT 4		//����ƽ��
#define	M_STATE_SINGLE_BOXING 5		//����k-boxing
#define	M_STATE_SINGLE_UP 6			//������ֱ����
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
	
	//���Զ��� ������겻��ͻ��
	bool					b_firstFindBody;//����Ƿ��ǵ�һ�η��ָ���Ŀ��
	double					d_oldTargetX;//ԭĿ���������xֵ
	double					d_oldTargetY;//ԭĿ���������yֵ
	double					d_oldAngle;
	double					d_recognizeDis;//��ֵ���жϸ���Ŀ��ʱ����ԭ�������������ڵ�������Ҫ�����Ǹ���
	
	//����������
	int						i_state;//��ǵ�ǰʶ�������״̬   �� -1����״̬����0����ͨ״̬��˫�۴�ֱ�·ţ���1��˫��ƽ�ڣ���2��˫��k-boxing����3��˫����ֱ���ϣ���4������ƽ�ڣ���5(����k-boxing)��6��������ֱ���ϣ�
	int						i_tempState;//��ǵ�ǰ֡������ʶ�������״̬������ѡ״̬
	int						i_counterState;//�����������֡ʶ�����״̬
	int						i_counterStateUpperBound;//����֡���ޣ����������ޣ���ʶ��ö���
	double					d_angleLeftShoulder[7];//�������ĸ��ط��ļн�
	double					d_angleLeftElbow[7];
	double					d_angleRightElbow[7];
	double					d_angleRightShoulder[7];
	double					d_angleLeftShoulderTarget;//�������ĸ��ط��ļнǡ������ֵ
	double					d_angleLeftElbowTarget;
	double					d_angleRightElbowTarget;
	double					d_angleRightShoulderTarget;

	double					target_angle;//
	double					target_r;
	double					target_x;//���ݸ��˶�ϵͳ�ĵ�i��Ŀ��ص���������xֵ
	double					target_y;//���ݸ��˶�ϵͳ�ĵ�i��Ŀ��ص���������yֵ
	double					d_angle[7];//
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
	//��������֮��ļн�
	double TurnAngle(DepthSpacePoint A,DepthSpacePoint B,DepthSpacePoint C);


	//��ʾͼ���Mat
	cv::Mat skeletonImg;
	cv::Mat depthImg;
};

