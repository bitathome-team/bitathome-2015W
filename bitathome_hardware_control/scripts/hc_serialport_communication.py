#!/usr/bin/env python
# coding=utf-8
# Filename : hc_serialport_communication.py
# Author : AbigCarrot
# E-mail : liudayuan94@gmail.com
# Created Date : 2014/11/16 21:36
# Description : 串口通信类
# History
#   2014/11/16 21:36 : 创建文件 [刘达远]

import serial
import rospy


class Communtcation():

    def __init__(self, port, band, byte):
        """
        :param port: 串口名称
        :param band: 比特率
        :param byte: 位长
        :return:
        """
        self.port = port
        self.band = band
        self.byte = byte
        self.link = None  # 串口链接

    """
    :function open:打开串口链接
    :return:是否成功打开,打开不成功返回False
    """

    def open(self):
        if self.link is not None and self.link.isOpen():
            self.link.close()

        try:
            self.link = serial.Serial(self.port, self.band, self.byte)
            rospy.loginfo("Try to link serial")
        except serial.SerialException:
            rospy.loginfo("Serial name has error T_T")
            return False
        rospy.loginfo("Serial linking succeeded ^_^")
        return True

    """
    :function close:关闭串口链接
    :return: 是否成功关闭
    """

    def close(self):
        if self.link is not None and self.link.isOpen():
            self.link.close()
            rospy.loginfo("Serial linking closed ^_^")

        return True

    """
    :function write:通过串口传输命令
    """

    def write(self, data):
        if self.link is None or not self.link.isOpen():
            if not self.open():
                rospy.loginfo("Serial Port is not Opened")
                return False

        buf = bytearray(data)

        self.link.write(buf)
        # rospy.loginfo("Serial writing succeeded ^_^")

        return True

