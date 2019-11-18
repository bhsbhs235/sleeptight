# -*- coding: utf-8 -*- 
#테스트 영상을 만들기 위한 코드
#촬영을 끝내기위해서는 esc 키를 누르면 됨
#그레이 스케일로 저장
import numpy as np
import cv2
import os
import cds


def writeVideo():
    os.system('sudo modprobe bcm2835-v4l2')
    try:
        print('camera on')
        cap=cv2.VideoCapture(0)
    except:
        print('fail')
        return
    #원하는 fps 해상도 설정
    fps = 10
    cap.set(3, 640)  #width
    cap.set(4, 480)  #height

    width = int(cap.get(3))
    height = int(cap.get(4))
    fcc = cv2.VideoWriter_fourcc('X', '2', '6', '4')

    out = cv2.VideoWriter('mycam.avi', fcc, fps, (width, height))
    print('recording')

    while True:
        if cap.isOpened() == False:
            cap.open()
        ret, frame = cap.read()
        if not ret:
            print('video read error')
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
#        cv2.imshow('video', gray2)
        out.write(gray2)

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            print('recording off')
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()



cds.irLedon(26)
cds.irLedon(19)
cds.irLedon(5)
cds.irLedon(0)
writeVideo()
cds.irLedoff(26)
cds.irLedoff(19)
cds.irLedoff(5)
cds.irLedoff(0)
cds.clean()
