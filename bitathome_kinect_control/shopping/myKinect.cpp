#include "myKinect.h"
#include <iostream>
#include	<cmath>
#define PI 3.1415926535898

/// Initializes the default Kinect sensor
HRESULT CBodyBasics::InitializeDefaultSensor()
{
	//用于判断每次读取操作的成功与否
	HRESULT hr;

	//搜索kinect
	hr = GetDefaultKinectSensor(&m_pKinectSensor);
	if (FAILED(hr)){
		return hr;
	}

	//找到kinect设备
	if (m_pKinectSensor)
	{
		// Initialize the Kinect and get coordinate mapper and the body reader
		IBodyFrameSource* pBodyFrameSource = NULL;//读取骨架
		IDepthFrameSource* pDepthFrameSource = NULL;//读取深度信息
		IBodyIndexFrameSource* pBodyIndexFrameSource = NULL;//读取背景二值图

		//打开kinect
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

	//skeletonImg,用于画骨架、背景二值图的MAT
	skeletonImg.create(cDepthHeight, cDepthWidth, CV_8UC3);
	skeletonImg.setTo(0);

	//depthImg,用于画深度信息的MAT
	depthImg.create(cDepthHeight, cDepthWidth, CV_8UC1);
	depthImg.setTo(0);

	return hr;
}


/// Main processing function
void CBodyBasics::Update()
{
	//每次先清空skeletonImg
	skeletonImg.setTo(0);


	//当前帧识别状态
	int stateNow = M_STATE_NULL;

	//赋初值
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

	//如果丢失了kinect，则不继续操作
	if (!m_pBodyFrameReader)
	{
		return;
	}

	//如果需要等待，则继续等待
	if(m_wait_count>0){
		m_wait_count--;
		return;
	}

	IBodyFrame* pBodyFrame = NULL;//骨架信息
	IDepthFrame* pDepthFrame = NULL;//深度信息
	IBodyIndexFrame* pBodyIndexFrame = NULL;//背景二值图

	//记录每次操作的成功与否
	HRESULT hr = S_OK;

	//---------------------------------------获取背景二值图并显示---------------------------------
	if (SUCCEEDED(hr)){
		hr = m_pBodyIndexFrameReader->AcquireLatestFrame(&pBodyIndexFrame);//获得背景二值图信息
	}
	if (SUCCEEDED(hr)){
		BYTE *bodyIndexArray = new BYTE[cDepthHeight * cDepthWidth];//背景二值图是8为uchar，有人是黑色，没人是白色
		pBodyIndexFrame->CopyFrameDataToArray(cDepthHeight * cDepthWidth, bodyIndexArray);

		//把背景二值图画到MAT里
		uchar* skeletonData = (uchar*)skeletonImg.data;
		for (int j = 0; j < cDepthHeight * cDepthWidth; ++j){
			*skeletonData = bodyIndexArray[j]; ++skeletonData;
			*skeletonData = bodyIndexArray[j]; ++skeletonData;
			*skeletonData = bodyIndexArray[j]; ++skeletonData;
		}
		delete[] bodyIndexArray;
	}
	SafeRelease(pBodyIndexFrame);//必须要释放，否则之后无法获得新的frame数据

	//-----------------------------获取骨架并显示----------------------------
	if (SUCCEEDED(hr)){
		hr = m_pBodyFrameReader->AcquireLatestFrame(&pBodyFrame);//获取骨架信息
	}
	if (SUCCEEDED(hr))
	{
		IBody* ppBodies[BODY_COUNT] = { 0 };//每一个IBody可以追踪一个人，总共可以追踪六个人

		if (SUCCEEDED(hr))
		{
			//把kinect追踪到的人的信息，分别存到每一个IBody中
			hr = pBodyFrame->GetAndRefreshBodyData(_countof(ppBodies), ppBodies);
		}

		if (SUCCEEDED(hr))
		{
			//对每一个IBody，我们找到他的骨架信息，并且画出来
			ProcessBody(BODY_COUNT, ppBodies);
		}

		for (int i = 0; i < _countof(ppBodies); ++i)
		{
			SafeRelease(ppBodies[i]);//释放所有
		}
	}
	SafeRelease(pBodyFrame);//必须要释放，否则之后无法获得新的frame数据

	//-----------------------获取深度数据并显示--------------------------
	if (SUCCEEDED(hr)){
		hr = m_pDepthFrameReader->AcquireLatestFrame(&pDepthFrame);//获得深度数据
	}
	if (SUCCEEDED(hr)){
		UINT16 *depthArray = new UINT16[cDepthHeight * cDepthWidth];//深度数据是16位unsigned int
		pDepthFrame->CopyFrameDataToArray(cDepthHeight * cDepthWidth, depthArray);

		//把深度数据画到MAT中
		uchar* depthData = (uchar*)depthImg.data;
		for (int j = 0; j < cDepthHeight * cDepthWidth; ++j){
			*depthData = depthArray[j];
			++depthData;
		}
		// tempLogic

		//03-29 false表明自启动以来一直未出现目标
		if(b_firstFindBody == false ){

			if(BodyNum == 1){

				//03-29 说明第一次找到了那个人，那么flag置true，同时将该人设到目标原位置中
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
			else //03-29 bodyNum！=1表明要么目前视野里没人，要么多个人，都无法确定哪个才是我要跟的目标
			{

			}
		}
		else// 03-29 表明之前已经找到过人了
		{
			bool tempFlag = false;// 03-29 标记当前数组中是否有在阈值内的跟踪目标
			for (int i = 0; i < BODY_COUNT ; i++)
			{
				if (m_flagIBodyIsTracked[i]==true)//03-29 表明第i个body中存有人的数据
				{
					double temp_r =	depthArray[ m_IBodyHeady[i] * cDepthWidth +  m_IBodyHeadx[i] ];
					double temp_x = temp_r * cos(d_angle[i]);
					double temp_y = temp_r * sin(d_angle[i]);

					temp_x = temp_x/1000.0;
					temp_y = temp_y/1000.0;


					//03-29 如果目标位置距在原位置阈值范围内
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

			if(tempFlag==false){//03-29 说明原目标已经不在视野内，就停下来

			}
		}
		delete[] depthArray;
	}
	SafeRelease(pDepthFrame);//必须要释放，否则之后无法获得新的frame数据
	imshow("depthImg", depthImg);
	cv::waitKey(5);

	double LS = d_angleLeftShoulderTarget;
	double LE = d_angleLeftElbowTarget;
	double RS = d_angleRightShoulderTarget;
	double RE = d_angleRightElbowTarget;

	if( LS >=0 ){//表示该帧命中
		
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

		if(stateNow == i_tempState){//该帧与当前检测姿势相同
			i_counterState++;

			if(i_tempState != i_state && i_counterState >= i_counterStateUpperBound){//识别该姿势，将该姿势设为当前识别姿势
				i_state = i_tempState;
			}
		}
		else
		{
			i_tempState = stateNow;//更新检测姿势
			i_counterState = 0;
		}
	}

}
/// 计算角度
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
	//记录操作结果是否成功
	HRESULT hr;

	//初始化计数器
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

	//对于每一个IBody
	for (int i = 0; i < nBodyCount; ++i)
	{
		IBody* pBody = ppBodies[i];




		if (pBody)//还没有搞明白这里pBody和下面的bTracked有什么区别
		{
			BOOLEAN bTracked = false;
			hr = pBody->get_IsTracked(&bTracked);

			if (SUCCEEDED(hr) && bTracked)
			{
				BodyNum++;
				m_flagIBodyIsTracked[i] = true;
				targetBodyIndex = i;

				Joint joints[JointType_Count];//存储关节点类
				HandState leftHandState = HandState_Unknown;//左手状态
				HandState rightHandState = HandState_Unknown;//右手状态

				//获取左右手状态
				pBody->get_HandLeftState(&leftHandState);
				pBody->get_HandRightState(&rightHandState);

				//存储深度坐标系中的关节点位置
				DepthSpacePoint *depthSpacePosition = new DepthSpacePoint[_countof(joints)];

				//获得关节点类
				hr = pBody->GetJoints(_countof(joints), joints);
				if (SUCCEEDED(hr))
				{
					for (int j = 0; j < _countof(joints); ++j)
					{
						//将关节点坐标从摄像机坐标系（-1~1）转到深度坐标系（424*512）
						m_pCoordinateMapper->MapCameraPointToDepthSpace(joints[j].Position, &depthSpacePosition[j]);
					}


					//--------获取头在深度坐标系中的值
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


					//-----------------------2015-4-4-----------计算人体4个部分的夹角
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

//画手的状态
void CBodyBasics::DrawHandState(const DepthSpacePoint depthSpacePosition, HandState handState)
{
	//给不同的手势分配不同颜色
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
	default://如果没有确定的手势，就不要画
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
		//非常确定的骨架，用白色直线
		line(skeletonImg, p1, p2, cvScalar(255, 255, 255));
	}
	else
	{
		//不确定的骨架，用红色直线
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