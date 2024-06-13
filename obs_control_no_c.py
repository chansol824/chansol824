#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32, Bool
import math

class OBS_Control:
    def __init__(self):
        rospy.init_node("control_node")

        rospy.Subscriber("/dist90R", Float32, self.dist90R_CB)
        rospy.Subscriber("/dist75R", Float32, self.dist75R_CB)
        rospy.Subscriber("/dist90L", Float32, self.dist90L_CB)
        rospy.Subscriber("/dist75L", Float32, self.dist75L_CB)
        rospy.Subscriber("/obsR", Bool, self.obsR_CB)
        rospy.Subscriber("/obsL", Bool, self.obsL_CB)

        self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=1)

        self.cmd_msg = Twist()
        self.obsR = False
        self.obsL = False
        self.dist90R = 0.5
        self.dist90L = 0.5
        self.dist75R = 0.5
        self.dist75L = 0.5
        self.wall_dist = 0.2
        self.kp = 0.01
        self.pre_steer = 0

        self.rate = rospy.Rate(10)

    def dist90R_CB(self, data):
        self.dist90R = data.data

    def dist75R_CB(self, data):
        self.dist75R = data.data

    def dist90L_CB(self, data):
        self.dist90L = data.data

    def dist75L_CB(self, data):
        self.dist75L = data.data

    def obsR_CB(self, data):
        self.obsR = data.data

    def obsL_CB(self, data):
        self.obsL = data.data

    def control(self):
        if self.obsR and not self.obsL:  # 오른쪽 벽을 따라가지만 왼쪽 벽이 없음
            speed = 0.3
            if self.dist90R == 0:
                speed = 0.0
                steer = self.pre_steer
                print('dist90R = 0')
            else:
                value = self.dist90R / self.dist75R
                if value > 1:
                    value = 1
                elif value < -1:
                    value = -1

                theta = math.acos(value) * 180 / math.pi
                print('theta:', theta)
                steer = (15 - theta) * math.pi / 180 + self.kp * (self.wall_dist - self.dist90R)
                print('steer:', steer)
            print('following right wall')
        elif self.obsR and self.obsL:  # 왼쪽 벽과 오른쪽 벽 모두 감지될 때
            speed = 0.3
            if self.dist90R == 0:
                speed = 0.0
                steer = self.pre_steer
                print('dist90R = 0')
            else:
                value = self.dist90R / self.dist75R
                if value > 1:
                    value = 1
                elif value < -1:
                    value = -1

                theta = math.acos(value) * 180 / math.pi
                print('theta:', theta)
                steer = (15 - theta) * math.pi / 180 + self.kp * (self.wall_dist - self.dist90R)
                print('steer:', steer)
            print('following right wall')
        elif self.obsL:  # 왼쪽 벽을 따라가기
            speed = 0.3
            if self.dist90L == 0:
                speed = 0.0
                steer = self.pre_steer
                print('dist90L = 0')
            else:
                value = self.dist90L / self.dist75L
                if value > 1:
                    value = 1
                elif value < -1:
                    value = -1

                theta = math.acos(value) * 180 / math.pi
                print('theta:', theta)
                steer = (theta - 15) * math.pi / 180 + self.kp * (self.wall_dist - self.dist90L)
                print('steer:', steer)
            print('following left wall')
        else:  # 양쪽 벽이 없을 때 정지
            speed = 0.3
            steer = 0
            print('no conditions met, stopping')

        self.cmd_msg.linear.x = speed
        self.cmd_msg.angular.z = steer
        self.pub.publish(self.cmd_msg)
        self.pre_steer = steer

def main():
    OBS_driving = OBS_Control()
    while not rospy.is_shutdown():
        OBS_driving.control()
        OBS_driving.rate.sleep()

if __name__ == "__main__":
    main()