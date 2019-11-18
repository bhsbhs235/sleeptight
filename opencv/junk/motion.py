# -*- coding: utf-8 -*-
#모션 감지

import numpy as np
import cv2
import os

#fps = 15, size = 640*480

count = 0 #프레임 카운터

os.system('sudo modprobe bcm2835-v4l2') #파이카메라 인식시키기 위한 코드
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FPS, 15) #fps 설정
camera.set(3, 640)  # 해상도 설정 3은 width, 4는 height
camera.set(4, 480) 

mog = cv2.createBackgroundSubtractorMOG2()   #차영상을 구하기위한 함수 설정
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))  #노이즈 제거를 위한 커널 설정


def backSubtraction():  # 차영상을 구해 리턴하는 함수

    ret, frame = cap.read()  #ret: 프레임 캡쳐 결과, frame: 캡쳐한 프레임
    fgmask = mog.apply(frame)   #배경제거
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)  #차영상의 노이즈 제거
    return fgmask
    # cv2.imshow('mask', fgmask)


def motionDetect(): # 일정시간동안 움직임을 감지해서 결과를 리턴하는 함수

    while True:
        fgmask = backSubtraction()
        _, contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # contours를 찾는다
        count += 1

        for c in contours: # 한 프레임의 contour들을 모두 찾아 검사해 움직임을 감지
            if cv2.contourArea(c) < #범위: #일정한 크기이상의 contours가 없으면 아래는 무시하고 while루프를 돈다
                continue

            return True #움직임이 검출됨 True 리턴
        

        if count > #숫자: #일정 시간동안 frame를 검사하고 종료
            break

    camera.release() #cleanup the camera
    return False #움직임이 검출되지 않음 False 리턴
