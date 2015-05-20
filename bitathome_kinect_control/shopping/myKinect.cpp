#include "myKinect.h"
#include <iostream>
#include	<cmath>
#define PI 3.1415926535898

/// Initializes the default Kinect sensor
HRESULT CBodyBasics::InitializeDefaultSensor()
{
	//�����ж�ÿ�ζ�ȡ�����ĳɹ����
	HRESULT hr;

	//����kinect
	hr = GetDefaultKinectSensor(&m_pKinectSensor);
	if (FAILED(hr)){
		return hr;
	}

	//�ҵ�kinect�豸
	if (m_pKinectSensor)
	{
		// Initialize the Kinect and get coordinate mapper and the body reader
		IBodyFrameSource* pBodyFrameSource = NULL;//��ȡ�Ǽ�
		IDepthFrameSource* pDepthFrameSource = NULL;//��ȡ�����Ϣ
		IBodyIndexFrameSource* pBodyIndexFrameSource = NULL;//��ȡ������ֵͼ

		//��kinect
		hr = m_pKinectSensor->Open();

		//coordinatemapper
		if (SUCCEEDED(hr))
		{
			hr = m_pKinectSensor->get_CoordinateMapper(&m_pCoordinateMapper);
		}

		//bodyframe
		if (SUCCEEDED(hr))
		{
			hr = m_pKinectSensor->get_BodyFrameSource(&pBodyFrameSource);
		}

		if (SUCCEEDED(hr))
		{
			hr = pBodyFrameSource->OpenReader(&m_pBodyFrameReader);
		}

		//depth frame
		if (SUCCEEDED(hr)){
			hr = m_pKinectSensor->get_DepthFrameSource(&pDepthFrameSource);
		}

		if (SUCCEEDED(hr)){
			hr = pDepthFrameSource->OpenReader(&m_pDepthFrameReader);
		}

		//body index frame
		if (SUCCEEDED(hr)){
			hr = m_pKinectSensor->get_BodyIndexFrameSource(&pBodyIndexFrameSource);
		}

		if (SUCCEEDED(hr)){
			hr = pBodyIndexFrameSource->OpenReader(&m_pBodyIndexFrameReader);
		}

		SafeRelease(pBodyFrameSource);
		SafeRelease(pDepthFrameSource);
		SafeRelease(pBodyIndexFrameSource);
	}

	if (!m_pKinectSensor || FAILED(hr))
	{
		std::cout << "Kinect initialization failed!" << std::endl;
		return E_FAIL;
	}

	//skeletonImg,���ڻ��Ǽܡ�������ֵͼ��MAT
	skeletonImg.create(cDepthHeight, cDepthWidth, CV_8UC3);
	skeletonImg.setTo(0);

	//depthImg,���ڻ������Ϣ��MAT
	depthImg.create(cDepthHeight, cDepthWidth, CV_8UC1);
	depthImg.setTo(0);

	return hr;
}


/// Main processing function
void CBodyBasics::Update()
{
	//ÿ�������skeletonImg
	skeletonImg.setTo(0);


	//��ǰ֡ʶ��״̬
	int stateNow = M_STATE_NULL;

	//����ֵ
	target_x = 0;
	target_y = 0;	
	target_r = 0;
	target_angle = 0;


	d_angleLeftElbowTarget = -1;
	d_angleLeftShoulderTarget = -1;
	d_angleRightElbowTarget = -1;
	d_angleRightShoulderTarget = -1;


	bool b_leftBoxing = false;
	bool b_leftFlat = false;
	bool b_rightBoxing = false;
	bool b_rightFlat = false;

	//�����ʧ��kinect���򲻼�������
	if (!m_pBodyFrameReader)
	{
		return;
	}

	//�����Ҫ�ȴ���������ȴ�
	if(m_wait_count>0){
		m_wait_count--;
		return;
	}

	IBodyFrame* pBodyFrame = NULL;//�Ǽ���Ϣ
	IDepthFrame* pDepthFrame = NULL;//�����Ϣ
	IBodyIndexFrame* pBodyIndexFrame = NULL;//������ֵͼ

	//��¼ÿ�β����ĳɹ����
	HRESULT hr = S_OK;

	//---------------------------------------��ȡ������ֵͼ����ʾ---------------------------------
	if (SUCCEEDED(hr)){
		hr = m_pBodyIndexFrameReader->AcquireLatestFrame(&pBodyIndexFrame);//��ñ�����ֵͼ��Ϣ
	}
	if (SUCCEEDED(hr)){
		BYTE *bodyIndexArray = new BYTE[cDepthHeight * cDepthWidth];//������ֵͼ��8Ϊuchar�������Ǻ�ɫ��û���ǰ�ɫ
		pBodyIndexFrame->CopyFrameDataToArray(cDepthHeight * cDepthWidth, bodyIndexArray);

		//�ѱ�����ֵͼ����MAT��
		uchar* skeletonData = (uchar*)skeletonImg.data;
		for (int j = 0; j < cDepthHeight * cDepthWidth; ++j){
			*skeletonData = bodyIndexArray[j]; ++skeletonData;
			*skeletonData = bodyIndexArray[j]; ++skeletonData;
			*skeletonData = bodyIndexArray[j]; ++skeletonData;
		}
		delete[] bodyIndexArray;
	}
	SafeRelease(pBodyIndexFrame);//����Ҫ�ͷţ�����֮���޷�����µ�frame����

	//-----------------------------��ȡ�Ǽܲ���ʾ----------------------------
	if (SUCCEEDED(hr)){
		hr = m_pBodyFrameReader->AcquireLatestFrame(&pBodyFrame);//��ȡ�Ǽ���Ϣ
	}
	if (SUCCEEDED(hr))
	{
		IBody* ppBodies[BODY_COUNT] = { 0 };//ÿһ��IBody����׷��һ���ˣ��ܹ�����׷��������

		if (SUCCEEDED(hr))
		{
			//��kinect׷�ٵ����˵���Ϣ���ֱ�浽ÿһ��IBody��
			hr = pBodyFrame->GetAndRefreshBodyData(_countof(ppBodies), ppBodies);
		}

		if (SUCCEEDED(hr))
		{
			//��ÿһ��IBody�������ҵ����ĹǼ���Ϣ�����һ�����
			ProcessBody(BODY_COUNT, ppBodies);
		}

		for (int i = 0; i < _countof(ppBodies); ++i)
		{
			SafeRelease(ppBodies[i]);//�ͷ�����
		}
	}
	SafeRelease(pBodyFrame);//����Ҫ�ͷţ�����֮���޷�����µ�frame����

	//-----------------------��ȡ������ݲ���ʾ--------------------------
	if (SUCCEEDED(hr)){
		hr = m_pDepthFrameReader->AcquireLatestFrame(&pDepthFrame);//����������
	}
	if (SUCCEEDED(hr)){
		UINT16 *depthArray = new UINT16[cDepthHeight * cDepthWidth];//���������16λunsigned int
		pDepthFrame->CopyFrameDataToArray(cDepthHeight * cDepthWidth, depthArray);

		//��������ݻ���MAT��
		uchar* depthData = (uchar*)depthImg.data;
		for (int j = 0; j < cDepthHeight * cDepthWidth; ++j){
			*depthData = depthArray[j];
			++depthData;
		}
		// tempLogic

		//03-29 false��������������һֱδ����Ŀ��
		if(b_firstFindBody == false ){

			if(BodyNum == 1){

				//03-29 ˵����һ���ҵ����Ǹ��ˣ���ôflag��true��ͬʱ�������赽Ŀ��ԭλ����
				b_firstFindBody = true;

				target_angle = d_angle[targetBodyIndex];

				target_r = depthArray[ m_IBodyHeady[targetBodyIndex] * cDepthWidth +  m_IBodyHeadx[targetBodyIndex] ];
				target_x = target_r * cos(target_angle);
				target_y = target_r * sin(target_angle);

				target_x = target_x/1000.0;
				target_y = target_y/1000.0;

				d_oldTargetX = target_x;
				d_oldTargetY = target_y;
				d_oldAngle	= target_angle * 180 / PI ;


				d_angleLeftElbowTarget = d_angleLeftElbow[targetBodyIndex];
				d_angleLeftShoulderTarget = d_angleLeftShoulder[targetBodyIndex];
				d_angleRightElbowTarget = d_angleRightElbow[targetBodyIndex];
				d_angleRightShoulderTarget = d_angleRightShoulder[targetBodyIndex];

				
			}
			else //03-29 bodyNum��=1����ҪôĿǰ��Ұ��û�ˣ�Ҫô����ˣ����޷�ȷ���ĸ�������Ҫ����Ŀ��
			{

			}
		}
		else// 03-29 ����֮ǰ�Ѿ��ҵ�������
		{
			bool tempFlag = false;// 03-29 ��ǵ�ǰ�������Ƿ�������ֵ�ڵĸ���Ŀ��
			for (int i = 0; i < BODY_COUNT ; i++)
			{
				if (m_flagIBodyIsTracked[i]==true)//03-29 ������i��body�д����˵�����
				{
					double temp_r =	depthArray[ m_IBodyHeady[i] * cDepthWidth +  m_IBodyHeadx[i] ];
					double temp_x = temp_r * cos(d_angle[i]);
					double temp_y = temp_r * sin(d_angle[i]);

					temp_x = temp_x/1000.0;
					temp_y = temp_y/1000.0;


					//03-29 ���Ŀ��λ�þ���ԭλ����ֵ��Χ��
					if(fabs(temp_x-d_oldTargetX)<=d_recognizeDis && fabs(temp_y-d_oldTargetY)<=d_recognizeDis){
						tempFlag = true;
						target_angle = d_angle[i];
						target_x = temp_x;
						target_y = temp_y;
						target_r = temp_r;

						d_oldTargetX = target_x;
						d_oldTargetY = target_y;
						d_oldAngle = target_angle *180 / PI;

						d_angleLeftElbowTarget = d_angleLeftElbow[i];
						d_angleLeftShoulderTarget = d_angleLeftShoulder[i];
						d_angleRightElbowTarget = d_angleRightElbow[i];
						d_angleRightShoulderTarget = d_angleRightShoulder[i];

						break;
					}
				}
			}

			if(tempFlag==false){//03-29 ˵��ԭĿ���Ѿ�������Ұ�ڣ���ͣ����

			}
		}
		delete[] depthArray;
	}
	SafeRelease(pDepthFrame);//����Ҫ�ͷţ�����֮���޷�����µ�frame����
	imshow("depthImg", depthImg);
	cv::waitKey(5);

	double LS = d_angleLeftShoulderTarget;
	double LE = d_angleLeftElbowTarget;
	double RS = d_angleRightShoulderTarget;
	double RE = d_angleRightElbowTarget;

	if( LS >=0 ){//��ʾ��֡����
		
		if( LS >= 150 && LS <= 210 && LE >= 230 && LE <= 320){
			b_leftBoxing = true;
		}
		if( LS >= 150 && LS <= 210 && LE >=150 && LE <= 210 ){
			b_leftFlat = true;
		}

		if( RS >= 150 && RS <= 210 && RE >= 40 && RE <= 130 ){
			b_rightBoxing = true;
		}
		if( RS >= 150 && RS <= 210 && RE >=150 && RE <= 210 ){
			b_rightFlat = true;
		}

		if(b_leftBoxing || b_rightBoxing){
			if(b_leftBoxing && b_rightBoxing){
				stateNow = M_STATE_DOUBLE_BOXING;
			}
			else
			{
				stateNow = M_STATE_SINGLE_BOXING;
			}
		}
		else if( b_leftFlat || b_rightFlat)
		{
			if(b_leftFlat && b_rightFlat){
				stateNow = M_STATE_DOUBLE_FLAT;
			}
			else
			{
				stateNow = M_STATE_SINGLE_FLAT;
			}
		}
		else
		{
			stateNow = M_STATE_NORMAL;
		}

		//if(i_tempState != M_STATE_NULL && i_tempState != )

		if(stateNow == i_tempState){//��֡�뵱ǰ���������ͬ
			i_counterState++;

			if(i_tempState != i_state && i_counterState >= i_counterStateUpperBound){//ʶ������ƣ�����������Ϊ��ǰʶ������
				i_state = i_tempState;
			}
		}
		else
		{
			i_tempState = stateNow;//���¼������
			i_counterState = 0;
		}
	}

}
/// ����Ƕ�
double CBodyBasics::TurnAngle(DepthSpacePoint A,DepthSpacePoint B,DepthSpacePoint C)
{
	double angle = 0,angle1,angle2;
	angle1 = atan2(A.Y - B.Y, A.X - B.X) * 180 / PI;
	angle2 = atan2(C.Y - B.Y, C.X - B.X) * 180 / PI;
	angle = angle2 - angle1;
	if(angle<0){
		angle = angle + 360;
	}

	return angle;
}

/// Handle new body data
void CBodyBasics::ProcessBody(int nBodyCount, IBody** ppBodies)
{
	//��¼��������Ƿ�ɹ�
	HRESULT hr;

	//��ʼ��������
	BodyNum = 0;

	/*

	for (int i = 0; i < nBodyCount; ++i)
	{
	IBody* pBody = ppBodies[i];

	if (pBody){
	BodyNum++;
	m_flagIBodyIsTracked[i] = true;
	}
	}
	*/

	//����ÿһ��IBody
	for (int i = 0; i < nBodyCount; ++i)
	{
		IBody* pBody = ppBodies[i];




		if (pBody)//��û�и���������pBody�������bTracked��ʲô����
		{
			BOOLEAN bTracked = false;
			hr = pBody->get_IsTracked(&bTracked);

			if (SUCCEEDED(hr) && bTracked)
			{
				BodyNum++;
				m_flagIBodyIsTracked[i] = true;
				targetBodyIndex = i;

				Joint joints[JointType_Count];//�洢�ؽڵ���
				HandState leftHandState = HandState_Unknown;//����״̬
				HandState rightHandState = HandState_Unknown;//����״̬

				//��ȡ������״̬
				pBody->get_HandLeftState(&leftHandState);
				pBody->get_HandRightState(&rightHandState);

				//�洢�������ϵ�еĹؽڵ�λ��
				DepthSpacePoint *depthSpacePosition = new DepthSpacePoint[_countof(joints)];

				//��ùؽڵ���
				hr = pBody->GetJoints(_countof(joints), joints);
				if (SUCCEEDED(hr))
				{
					for (int j = 0; j < _countof(joints); ++j)
					{
						//���ؽڵ���������������ϵ��-1~1��ת���������ϵ��424*512��
						m_pCoordinateMapper->MapCameraPointToDepthSpace(joints[j].Position, &depthSpacePosition[j]);
					}


					//--------��ȡͷ���������ϵ�е�ֵ
					m_IBodyHeadx[i]  = depthSpacePosition[JointType_SpineMid].X;
					m_IBodyHeady[i]  = depthSpacePosition[JointType_SpineMid].Y;

					if(m_IBodyHeadx[i]<0 || m_IBodyHeadx[i]>512 || m_IBodyHeady[i]<0 || m_IBodyHeady[i]>424){
						m_IBodyHeadx[i]  = depthSpacePosition[JointType_Neck].X;
						m_IBodyHeady[i]  = depthSpacePosition[JointType_Neck].Y;						
					}
					if(m_IBodyHeadx[i]<0 || m_IBodyHeadx[i]>512 || m_IBodyHeady[i]<0 || m_IBodyHeady[i]>424){
						m_IBodyHeadx[i]  = 0;
						m_IBodyHeady[i]  = 0;					
					}
					d_angle[i] = atan(joints[JointType_SpineMid].Position.X / joints[JointType_SpineMid].Position.Z);


					//-----------------------2015-4-4-----------��������4�����ֵļн�
					d_angleLeftElbow[i] = TurnAngle(depthSpacePosition[JointType_ShoulderLeft],depthSpacePosition[JointType_ElbowLeft],depthSpacePosition[JointType_WristLeft]);
					d_angleRightElbow[i] = TurnAngle(depthSpacePosition[JointType_ShoulderRight],depthSpacePosition[JointType_ElbowRight],depthSpacePosition[JointType_WristRight]);

					d_angleLeftShoulder[i] = TurnAngle(depthSpacePosition[JointType_SpineShoulder],depthSpacePosition[JointType_ShoulderLeft],depthSpacePosition[JointType_ElbowLeft]); 					
					d_angleRightShoulder[i] = TurnAngle(depthSpacePosition[JointType_SpineShoulder],depthSpacePosition[JointType_ShoulderRight],depthSpacePosition[JointType_ElbowRight]); 

					//------------------------hand state left-------------------------------
					DrawHandState(depthSpacePosition[JointType_HandLeft], leftHandState);
					DrawHandState(depthSpacePosition[JointType_HandRight], rightHandState);

					//---------------------------body-------------------------------
					DrawBone(joints, depthSpacePosition, JointType_Head, JointType_Neck);
					DrawBone(joints, depthSpacePosition, JointType_Neck, JointType_SpineShoulder);
					DrawBone(joints, depthSpacePosition, JointType_SpineShoulder, JointType_SpineMid);
					DrawBone(joints, depthSpacePosition, JointType_SpineMid, JointType_SpineBase);
					DrawBone(joints, depthSpacePosition, JointType_SpineShoulder, JointType_ShoulderRight);
					DrawBone(joints, depthSpacePosition, JointType_SpineShoulder, JointType_ShoulderLeft);
					DrawBone(joints, depthSpacePosition, JointType_SpineBase, JointType_HipRight);
					DrawBone(joints, depthSpacePosition, JointType_SpineBase, JointType_HipLeft);

					// -----------------------Right Arm ------------------------------------ 
					DrawBone(joints, depthSpacePosition, JointType_ShoulderRight, JointType_ElbowRight);
					DrawBone(joints, depthSpacePosition, JointType_ElbowRight, JointType_WristRight);
					DrawBone(joints, depthSpacePosition, JointType_WristRight, JointType_HandRight);
					DrawBone(joints, depthSpacePosition, JointType_HandRight, JointType_HandTipRight);
					DrawBone(joints, depthSpacePosition, JointType_WristRight, JointType_ThumbRight);

					//----------------------------------- Left Arm--------------------------
					DrawBone(joints, depthSpacePosition, JointType_ShoulderLeft, JointType_ElbowLeft);
					DrawBone(joints, depthSpacePosition, JointType_ElbowLeft, JointType_WristLeft);
					DrawBone(joints, depthSpacePosition, JointType_WristLeft, JointType_HandLeft);
					DrawBone(joints, depthSpacePosition, JointType_HandLeft, JointType_HandTipLeft);
					DrawBone(joints, depthSpacePosition, JointType_WristLeft, JointType_ThumbLeft);

					// ----------------------------------Right Leg--------------------------------
					DrawBone(joints, depthSpacePosition, JointType_HipRight, JointType_KneeRight);
					DrawBone(joints, depthSpacePosition, JointType_KneeRight, JointType_AnkleRight);
					DrawBone(joints, depthSpacePosition, JointType_AnkleRight, JointType_FootRight);

					// -----------------------------------Left Leg---------------------------------
					DrawBone(joints, depthSpacePosition, JointType_HipLeft, JointType_KneeLeft);
					DrawBone(joints, depthSpacePosition, JointType_KneeLeft, JointType_AnkleLeft);
					DrawBone(joints, depthSpacePosition, JointType_AnkleLeft, JointType_FootLeft);
				}
				delete[] depthSpacePosition;
			}
			else
			{
				m_flagIBodyIsTracked[i] = false;
			}

		}
		else
		{
			m_flagIBodyIsTracked[i] = false;
		}
	}
	cv::imshow("skeletonImg", skeletonImg);
	cv::waitKey(5);
}

//���ֵ�״̬
void CBodyBasics::DrawHandState(const DepthSpacePoint depthSpacePosition, HandState handState)
{
	//����ͬ�����Ʒ��䲻ͬ��ɫ
	CvScalar color;
	switch (handState){
	case HandState_Open:
		color = cvScalar(255, 0, 0);
		break;
	case HandState_Closed:
		color = cvScalar(0, 255, 0);
		break;
	case HandState_Lasso:
		color = cvScalar(0, 0, 255);
		break;
	default://���û��ȷ�������ƣ��Ͳ�Ҫ��
		return;
	}

	circle(skeletonImg,
		cvPoint(depthSpacePosition.X, depthSpacePosition.Y),
		20, color, -1);
}


/// Draws one bone of a body (joint to joint)
void CBodyBasics::DrawBone(const Joint* pJoints, const DepthSpacePoint* depthSpacePosition, JointType joint0, JointType joint1)
{
	TrackingState joint0State = pJoints[joint0].TrackingState;
	TrackingState joint1State = pJoints[joint1].TrackingState;

	// If we can't find either of these joints, exit
	if ((joint0State == TrackingState_NotTracked) || (joint1State == TrackingState_NotTracked))
	{
		return;
	}

	// Don't draw if both points are inferred
	if ((joint0State == TrackingState_Inferred) && (joint1State == TrackingState_Inferred))
	{
		return;
	}

	CvPoint p1 = cvPoint(depthSpacePosition[joint0].X, depthSpacePosition[joint0].Y),
		p2 = cvPoint(depthSpacePosition[joint1].X, depthSpacePosition[joint1].Y);

	// We assume all drawn bones are inferred unless BOTH joints are tracked
	if ((joint0State == TrackingState_Tracked) && (joint1State == TrackingState_Tracked))
	{
		//�ǳ�ȷ���ĹǼܣ��ð�ɫֱ��
		line(skeletonImg, p1, p2, cvScalar(255, 255, 255));
	}
	else
	{
		//��ȷ���ĹǼܣ��ú�ɫֱ��
		line(skeletonImg, p1, p2, cvScalar(0, 0, 255));
	}
}


/// Constructor
CBodyBasics::CBodyBasics() :
	m_pKinectSensor(NULL),
	m_pCoordinateMapper(NULL),
	m_pBodyFrameReader(NULL)
{
	b_firstFindBody = false;
	d_oldTargetX = 0;
	d_oldTargetY = 0;
	d_oldAngle = 0;
	d_recognizeDis = 0.45;

	target_x = 0;
	target_y = 0;
	m_wait_count = 0;
	target_angle = 0;
	m_state = STATE_NORMAL;

	i_counterState = 0;
	i_counterStateUpperBound = 5;
	i_state = M_STATE_NULL;
	i_tempState = M_STATE_NULL;

	for (int i = 0; i < 7; i++)
	{
		m_flagIBodyIsTracked[i] = false;
		m_IBodyHeadx[i] = 0;
		m_IBodyHeady[i] = 0;
	}	

}

/// Destructor
CBodyBasics::~CBodyBasics()
{
	SafeRelease(m_pBodyFrameReader);
	SafeRelease(m_pCoordinateMapper);

	if (m_pKinectSensor)
	{
		m_pKinectSensor->Close();
	}
	SafeRelease(m_pKinectSensor);
}

void CBodyBasics::TargetZero()
{
	target_x = 0;
	target_y = 0;
}