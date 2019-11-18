# -*- coding: utf-8 -*-

import numpy as np
import cv2
import os
import time
import datetime
os.system('sudo modprobe bcm2835-v4l2')

col, width, row, height = -1, -1, -1, -1
frame = None
frame2 = None
inputmode = False
rectangle = False

fps = 15 #fps값 설정 변수
cap=cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, fps) # fps 설정
cap.set(3,640) #width 설정
cap.set(4,480) #heigth 설정

mog = cv2.createBackgroundSubtractorMOG2(detectShadows=False)   #차영상을 구하기위한 함수 설정
#mog = cv2.bgsegm.createBackgroundSubtractorMOG()
#mog = cv2.bgsegm.createBackgroundSubtractorGMG()
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))  #노이즈 제거를 위한 커널 설정

def onMouse(event, x, y, flags, param): #마우스 동작 함수 roi 선택용
    global col, width, row, height, frame, frame2, inputmode
    global rectangle

    if inputmode:
        if event==cv2.EVENT_LBUTTONDOWN:
            rectangle = True
            col,row = x,y
        elif event==cv2.EVENT_MOUSEMOVE:
            if rectangle:
                frame=frame2.copy()
                cv2.rectangle(frame,(col,row),(x,y),(0,255,0),2)
                cv2.imshow('frame', frame)
        elif event==cv2.EVENT_LBUTTONUP:
            inputmode = False
            rectangle = False
            cv2.rectangle(frame,(col,row),(x,y),(0,255,0),2)
            height, width = abs(y-row), abs(x-col)
            trackWindow = (col,row,width,height)
            sp = open('savePoint.txt','w')
            a = [str(col), str(row),str(width), str(height)]
            sp.write('\n'.join(a))
            sp.close()
        return
        
def backSubtraction(roi):  # 차영상을 구해 리턴하는 함수
        
    fgmask = mog.apply(roi)   #배경제거
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)  #차영상의 노이즈 제거
    #cv2.imshow('originalroi', roi) #roi 영상 확인용
    #cv2.imshow('mask', fgmask)     #roi 내 차영상 ----------------------
    return fgmask


def readFile():
    global col, row, width, height 
    try: #파일이 없어 오류 발생시 파일 생성
        f = open('savePoint.txt', 'r')
        col = int(f.readline())
        row = int(f.readline())
        width = int(f.readline())
        height = int(f.readline())
        f.close()
    except IOError: #IOError 오류가 생길때 파일 생성
        f = open('savePoint.txt', 'w')
        a = [str(1), str(1), str(1), str(1)]
        f.write('\n'.join(a))
        f.close()
        
        
#모션 감지 함수
#모션 감지 수행하는 시간을 time을 통해 조절할수 있고 
#모션감지함수를 시간제한없이 동작시키려면 time에 0을 넣어준다    
#함수 인자 : time - 모션 감지 수행 시간, contourValue - 모션감지 민감도 설정, show - 영상 확인 창 on(1), off(0)
def motionDetect(time, contourValue, show):
    global frame, frame2, inputmode, fps
    count = 0 #감지시간을 위한 카운터 값
    number = 0 #일정 시간내 모션 감지 숫자 카운트
    frameCount = 0 #frame number 
    #v1, v2, v3, v4, v5 #수면 분석 사진 저장용
    ret, frame = cap.read()
    readFile()
    cv2.rectangle(frame,(col,row),(col+width,row+height),(0,255,0),2)
    if show == 1:
        cv2.namedWindow('frame')  #-----------------------------
        cv2.setMouseCallback('frame', onMouse, param=(frame,frame2))  #------------
       
    #print('width: %d, height: %d, detect limit: %d' % (width, height, ((width*height)/3))) 
    if contourValue == 100000:
        print('감지구역 재설정을 위해 i를 누르고 마우스를 이용하여 구역을 재설정 하세요.')
        print('감지 구역 재설정을 끝내려면 esc 키를 누르세요.')


    while True:
        frameCount += 1
        ret, frame = cap.read()
        roi = frame[row:row+height, col:col+width] #영상에서 선택한 영역이외는 자름
        if not ret:
            break

        fgmask = backSubtraction(roi)
        if show == 1:
            cv2.imshow('mask', fgmask)   #roi 내 차영상 -------------------------        
        _, contours, _ = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # contours를 찾는다
        count += 1
        if (frameCount % 15 ) == 0: #15frame에 한번씩 모션 디텍트
            for c in contours: # 한 프레임의 contour들을 모두 찾아 검사해 움직임을 감지
                areaValue = cv2.contourArea(c)
                if areaValue < contourValue:
                #범위: #일정한 크기이상의 contours가 없으면 아래는 무시하고 while루프를 돈다
                    continue
                elif areaValue > ((width*height)/3):
                    continue
                elif time != 0 and time != -1: #일정시간내 감지 동작시 
                    print('동작 감지')
                    print('동작 크기: %d' % areaValue)
                    return areaValue
                elif time == 0:
                    print('동작 감지')
                    print('동작 크기: %d' % areaValue)
                    number += 1
                    saveImage(roi, fgmask)
                    return areaValue #수면 기록 테스트를 위한 리턴값
                    #return True #시간제한 없이 감지 동작-감지 동작하면 리턴
                elif time == -1:
                    print('동작 감지')
                    print('동작 크기: %d' % areaValue)
                
        cv2.rectangle(frame,(col,row),(col+width,row+height),(0,255,0),2)
        if show == 1:
            cv2.imshow('frame', frame) #---------------------
        k=cv2.waitKey(1)&0xFF

        if k==27: #ess 키로 강제 종료시
            print('esc키로 종료')
            #cap.release()
            cv2.destroyAllWindows()
            return False

        if k==ord('i'): #'i' 키로 감지 영역 재설정
            print('동작 감지를 원하는 구간을 마우스로 지정하세요')
            print('감지를 시작하려면 아무키나 누르세요')
            inputmode = True
            frame2 = frame.copy()

            while inputmode:
                cv2.imshow('frame',frame)
                cv2.waitKey(0)

        if time != 0 and count >= fps*time and time != -1: #모션감지 동작시간 time값이 0이면 계속 동작
            return 0 #일정시간 동안 움직임 감지하고 감지를 못하면 0 리턴

    #cap.release()
    #cv2.destroyAllWindows()

def saveImage(img, sub):
    currentTime = time.time() #현재시간 구하기
    totalseconds = int(currentTime) #현재시간을 초 단위로 변환
    currentsecond = totalseconds % 60 #현재 시간의 초 구하기
    totalMinutes = totalseconds // 60 #현재시간을 분으로 변환
    currentMinute = totalMinutes % 60 #현재 시간의 분 구하기
    totalHours = totalMinutes // 60 # 현재 흐른시간을 시간으로 변환
    currentHour = totalHours % 24 # 현재시간의 시 구하기
    currentHour += 9 #한국시간으로 변화
    if currentHour > 24:
        currentHour -= 24
    
    name = str(currentHour) + 'h' + str(currentMinute) + 'm' + str(currentsecond) + 's'

    cv2.imwrite('images/'+ name + '1.jpg', img)
    cv2.imwrite('images/'+ name + '2.jpg', sub)

if __name__ == '__main__':
    motionDetect(-1, 1000, 1)
