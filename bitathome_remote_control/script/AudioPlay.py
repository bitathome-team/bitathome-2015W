#!/usr/bin/env python2.7
# -*- coding: utf-8 -*
# File Name: AudioPlay.py
# Author: Alan Snape
# Create Date: 2014/8/7 9:35
# Description: play sound (play audio file or TTS)

import rospy
from sound_play.libsoundplay import SoundClient
from bitathome_remote_control.srv import *


def do_say(data):
    rospy.loginfo("saying \"%s\"" % data.buf)
    # handle.voiceSound(data.buf).repeat()
    handle.say(data.buf, "voice_cmu_us_jmk_arctic_clunits")
    return 0


def srv():
    rospy.Service('AudioPlay/TTS', say, do_say)


if __name__ == '__main__':
    rospy.loginfo("Starting node...")
    rospy.init_node('AudioPlay')
    rospy.loginfo("Starting handle...")
    handle = SoundClient()
    rospy.sleep(1)
    handle.stopAll()
    rospy.loginfo("Ready")
    srv()
    rospy.spin()
