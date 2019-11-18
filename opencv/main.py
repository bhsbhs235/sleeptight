# -*- coding: utf-8 -*-
#main function code

import RPi.GPIO as GPIO
import stream
import os
import detect
import cds
import time
import sys
import wjson
import datetime
import cv2
import record
import tcpServer
import msg

deepTime = 600 #깊은잠 판별 시간
noiseArea = 5000 # 노이즈 판별 크기
contourHuman = 800 # 모션 감지 민감도 설정-사람 감지
contourSleep = 400  # 모션 감지 민감도 설정-수면 뒤척임 감지
cdsSetvalue = 2500 #조도센서 설정값
dataRecord = 1 #수면 데이터 상세 기록 on(1), off(0) flag
showWindows = 0 #카메라 영상창 on(1), off(0) flag
irLedState = '0' # irLed 상태 flag
modeFlag = True


#조도센서로 불이 꺼지는것을 감지하면 사람의 움직임을 감지
def humanDetection():
    global cdsSetvalue, contourHuman, showWindows, dataRecord, modeFlag
    cdsValue = 0
    cdsCount = 0
    detectNumber = 0
    print('조도 센서 감지')
    while True:
        time.sleep(1)
        if modeFlag == True:
            print('수면 패턴 측정 모드 동작중')
            while cdsCount < 2:
                cdsValue = cds.light(4)
                print('조도 값: %d' % cdsValue)
                cdsCount += 1
     
        elif modeFlag == False:
            print('보안 모드 동작중')
            detectPerson()
        

        cdsCount = 0

        if cdsValue > cdsSetvalue: #조도센서로 불이 꺼진걸 감지하면 
            print('불이 꺼짐, 사람 감지 시작, 감지 민감도: %d' % contourHuman)
            print('적외선 램프 켜짐')
            irledon()
            detectTime1 = time.time()
            while True:
                areaValue = detect.motionDetect(60, contourHuman, showWindows) #일정시간동안 움직임 감지
                detectTime2 = time.time()
                totalDetectTime = int(detectTime2 - detectTime1)
                if totalDetectTime > 900:
                    irledoff()
                    print('사람없음')
                    break
                if areaValue > 800:
                    detectNumber += 1
                    time.sleep(2) #정확한 감지를 위한 딜레이
                if detectNumber >= 1: 
                    print('사람감지, 수면감지 시작')
                    return True #수면 감지



#불이 꺼지고 사람이 움직이는 것이 감지되면 
#사람이 잠드는 평균 시간인 30분간 모션 감지를 하여 
#수면 감지 판별
def sleepDetection():
    global cdsSetvalue, contourSleep, showWindows, dataRecord
    sleepdetect = 0
    totaldetect = 0
    count = 0
    cdsCount = 0 
    exitcount = 0

    sleepValue = humanDetection() #불이 꺼지고 사람이 움직이는 것을 감지

    if sleepValue == True: 
        time.sleep(3) #정확한 분석을 위한 딜레이 

        print('사람이 잠자는지 수면 감지 판별 시작')
        detectTime1 = time.time()
        while True: #5분간 잠자는 공간을 모션 감지하여 사람이 진짜 잠자는지 판별
            print('일정시간 동안 움직임 감지')
            light = cds.light(4)
            sleepdetect = detect.motionDetect(30, contourSleep, showWindows)
            detectTime2 = time.time()
            totalDetectTime = int(detectTime2 - detectTime1)
            if totalDetectTime > 1800:
                print('수면중인 사람 감지 실패, 사람 없음')
                break
            if dataRecord == 1: #수면 데이터 상세 기록
                record.writetxt(sleepdetect, light)
            if sleepdetect > 0: # 중복 감지를 방지하기 위한 딜레이
                time.sleep(3) 
            count += 1

            if sleepdetect > 0: #움직임이 감지되면 참
                totaldetect += 1
            if totaldetect > 2:
                print('수면 중인 사람 감지 성공')
                return True
            print('조도 값: %d' % light)
            if light < cdsSetvalue: #방안 등이 켜져있는지 검사
                print('방안 불 켜짐, 수면 감지 실패')
                break
                


         

#wjson.writejson 인자 pastTime(이전시간), currentTime(현재시간), day(날짜), sleeppattern(깊은잠 or 얕은잠), start_end flag, number(파일이름 넘버링)
#수면 패턴 측정
def sleepPattern(run): #인자 - 0: 수면패턴 분석, 1: 수면패턴 측정
    global contourSleep, showWindows, dataRecord, noiseArea, deepTime
    maximumArea = 0
    d = datetime.date.today()
    start_end = 1 #수면 시작, 끝 flag, 1: 시작 2: 끝 0: 수면중
    sleepPatternIndex = 1 #수면패턴 정보, 시작은 얕은 잠, 1: 얕은 잠 2: 깊은 잠
    writeIndex = 1 #json 파일 넘버 인덱스
    cdsCount = 0 # 조도센서 측정을 위한 
    detectFlag = 0 #detect 판별용 flag 1: 기록중, 0: 기록중 아님
    detectCount = 0 #감지횟수 카운터

    lump1 = 0 # 0: 정보 저장 안된, 1: 저장중, 2: 저장됨
    lump2 = 0

    lump1Start = 0
    lump1End = 0
    lump2Start = 0
    lump2End = 0

    if run == 1:
        print('수면 패턴 측정 시작')
    elif run == 0:
        print('수면 데이터 분석 시작')
        f = open("sleepData.txt", 'r')
    while True:

        if run == 1:
            light = cds.light(4)
            print('조도값: %d' % light)
             
            if light < cdsSetvalue:  #조도 센서를 통해 수면의 종료 되는 것을 감지한다.
                print('불 켜짐, 수면 감지 종료')
                currentTime = time.time()
                wjson.writejson(lump1Start, currentTime, d, 1, 0, writeIndex) # 수면 데이터를 기록하기 위한 함수
                writeIndex += 1
                wjson.writejson(currentTime, currentTime, d, 1, 2, writeIndex)
                if dataRecord == 1:
                    record.writetxt(areaValue, light) # 동작 감지 정보를 기록하기 위한 함수
                irledoff()
                return #수면 감지 종료
        
        if run == 1:
            time1 = time.time() # time1, time2는 모션 감지 시간 간격을 재기 위한 변수
            areaValue = detect.motionDetect(0, contourSleep, showWindows) # 움직임이 감지되면 움직임 크기를 반환한다.
            time2 = time.time()
        elif run == 0:
            line = f.readline()    # 수면 데이터 분석을 위한 부분
            if line == '':         # 저장된 동작 감지 정보를 불러와 수면 분석을 실시
                wjson.writejson(lump1Start, time2, d, 1, 0, writeIndex)
                writeIndex += 1
                wjson.writejson(time2, time2, d, 1, 2, writeIndex)
                return
            lineSplit = line.split(',')
            time1 = int(lineSplit[0])
            time2 = int(lineSplit[1])
            areaValue = int(lineSplit[2])


        if dataRecord == 1 and run == 1: #수면 데이터 상세 기록
            record.writetxt(areaValue, light)
            record.sleepData(time1, time2, areaValue) #수면 분석 프로그램용

        timeInterval = int(time2 - time1)

        # 짧은 시간 내에 감지된 움직임들은 하나의 묶음으로 생각한다.
        # 묶음을 lump라 부르고 두 개의 묶음인 lump1 lump2가 기록되면
        # 두 묶음의 시간 간격을 검사해 얕은 수면인지 깊은 수면인지 판별
        if detectFlag == 0: #기록이 처음 시작되면 참
            if lump1 == 0: #lump1에 기록이 비어 있으면 참
                if areaValue > noiseArea: #노이즈가 감지되면 넘어감 매우 큰 크기의 값이 감지되는 경우
                    continue
                maximumArea = areaValue #lump1 정보 기록
                lump1Start = time2
                detectCount += 1
                detectFlag = 1
                lump1 = 1
                print('동작 묶음 1 기록중')
                print('동작 묶음 1 기록 시작 시간: %d' % lump1Start)
                continue 
            elif lump2 == 0 and lump1 == 2: #lump1 기록이 완료되면 lump2를 기록 시작
                if areaValue > noiseArea:
                    continue
                maximumArea = areaValue
                lump2Start = time1
                detectCount += 1
                detectFlag = 1
                lump2 = 1
                print('동작 묶음 2 기록중')
                print('동작 묶음 2 기록 시작 시간: %d' % lump2Start)
                continue
        elif detectFlag == 1: #lump1, 2가 기록중일때 감지된 동작들을 검사해 lump에 알맞은 정보를 기록한다.
            if timeInterval <= 7:
                if lump1 == 1:
                    if areaValue > maximumArea:
                        if areaValue < noiseArea:
                            maximumArea = areaValue
                        else:
                            lump1End = time1
                            continue
                    detectCount += 1
                    lump1End = time2
                    continue
                elif lump2 == 1 and lump1 == 2:
                    if areaValue > maximumArea:
                        if areaValue < noiseArea:
                            maximumArea = areaValue
                        else:
                            lump2End = time1
                            continue
                    detectCount += 1
                    lump2End = time2
                    continue
            elif timeInterval > 7:
                if lump1 == 1:
                    if maximumArea > noiseArea or detectCount == 1:
                        lump1 = 0
                        print('노이즈 제거필터 작동, 동작 묶음 제거')
                        detectCount = 0
                        detectFlag = 0
                        lump1Start = 0
                        lump1End = 0
                        continue
                    else:
                        lump1 = 2
                        print('동작 묶음 1 기록 완료')
                        lump1End = time1
                        print('동작 묶음 1 기록 종료 시간: %d' % lump1End)
                        detectCount = 0
                        detectFlag = 0
                        continue
                elif lump2 == 1:
                    if maximumArea > noiseArea or detectCount == 1:
                        lump2 = 0
                        print('노이즈 제거필터 작동, 동작 묶음 제거')
                        detectCount = 0
                        detectFlag = 0
                        lump2Start = 0
                        lump2End = 0
                        continue
                    else:
                        lump2 = 2
                        lump2End = time1
                        detectCount = 0
                        detectFlag = 0
                        print('동작 묶음 2 기록 완료')
                        print('동작 묶음 2 기록 종료 시간: %d' % lump2End)
                        
        # 감지된 동작들의 묶음인 lump1, 2가 둘다 기록이 완료되면 묶음간의 시간 간격을 검사해 수면 패턴을 측정 및 기록한다.
        if lump1 == 2 and lump2 == 2: 
            t = int(lump2Start - lump1End)
            print('동작 없는 구간 시간 간격: %d' % t)
            if t > deepTime:  #lump1, 2 사이의 시간 간격이 일정 값 이상이면 깊은 잠을 감지
                if (lump1End - lump1Start) < 60: #노이즈 제거 부분 너무 짧은 시간인 경우
                    writeIndex -= 1
                    wjson.writejson(oldlump1End, lump2Start, d, 0, start_end, writeIndex) #앞서 작성된 수면 정보 수정
                    writeIndex += 1
                    lump1Start = lump2Start
                    lump1End = lump2End
                    lump2 = 0
                    detectCount = 0
                    detectFlag = 0
                # 수면 정보를 기록하는 부분, json 형식으로 저장된다.
                else:
                    print('얕은 수면 기록') #lump1Start 부터 lump1End 까지 얕은잠
                    wjson.writejson(lump1Start, lump1End, d, 1, start_end, writeIndex)
                    if start_end == 1:
                        start_end = 0
                    writeIndex += 1
                    print('깊은 수면 기록') #lump1End 부터 lump2Start 까지 깊은잠
                    wjson.writejson(lump1End, lump2Start, d, 0, start_end, writeIndex)
                    writeIndex += 1
                    oldlump1End = lump1End
                    lump1Start = lump2Start
                    lump1End = lump2End
                    lump2 = 0
                    detectCount = 0
                    detectFlag = 0
                    #수면 패턴 기록 작성, lump2 = lump1
            else: #일정시간 값 이하이면 계속 얕은 잠을 자고 있는 것으로 판단
                lump2 = 0
                print('동작 묶음 2 초기화')
                detectCount = 0
                detectFlag = 0
                lump1End = lump2End
                #print('lump1End : %d' % lump1End)



def main():
    global modeFlag
    sleepValue = False
    switch(21)
    while True:
        sleepValue = sleepDetection() # 수면 감지
        if sleepValue == True:
            print('수면패턴 측정 시작')
            sleepPattern(1)
            wjson.jsonTotxt()            
            #통신 모듈 작동 부분
            tcpServer.tcpSend()

        elif sleepValue == False:
            print('수면 감지 재시작')

def detectPerson(): #CCTV 보안모드 동작
    areaValue = detect.motionDetect(5, contourHuman, showWindows)
    if areaValue > 800:
        print('침입자 감지!, 메시지 전송')
        msg.sendMsg()
        time.sleep(3)
    else:
        print('침입자 없음!')


def switch(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=my_callback, bouncetime=2000)

def my_callback(channel):
    global modeFlag
    print('CCTV 모드 변경')
    if modeFlag == True:
        modeFlag = False
        cds.irLedon(20)
    elif modeFlag == False:
        cds.irLedoff(20)
        modeFlag = True
    else:
        cds.irLedoff(20)
        modeFlag = True

def irledon():
    cds.irLedon(14)


def irledoff():
    cds.irLedoff(14)

def setUp():
    global dataRecord, showWindows
    print('\n설정값 출력----------')
    if dataRecord == 1:
        print('수면 데이터 상세 기록 on')
    else:
        print('수면 데이터 상세 기록 off')
    if showWindows  == 1:
        print('모니터링용 영상창 on')
    else:
        print('모니터링용 영상창 off')
    while True:
        s = input('\n원하는 설정을 선택(1: 감지구역 설정, 2: 수면 데이터 상세 기록, 3: 모니터링 영상창, 0: 설정종료): ')
        if s == '1': #감지 구역 재설정
            print('감지 구역 재설정')
            detect.motionDetect(0, 100000, 1)
        elif s == '2': #수면 데이터 상세 기록 설정
            while True:
                k = input('\n수면 데이터 분석을 위해 상세 정보 기록 동작 on(1) or off(0): ')
                if k == '1':
                    print('수면 데이터 상세 기록 on')
                    dataRecord = 1 # 수면 데이터 상세 기록 on
                    break
                elif k == '0':
                    print('수면 데이터 상세 기록 off')
                    dataRecord = 0 # 수면 데이터 상세 기록 off
                    break
                else:
                    print('잘못된 입력, 다시 입력하세요.')
        elif s == '3': # 카메라 영상창  on off 설정
            while True:
                k = input('\n영상 처리 모니터링을 위한 영상창 on(1) or off(0): ')
                if k == '1':
                    print('모니터링용 영상창 on')
                    showWindows = 1
                    break
                elif k == '0':
                    print('모니터링용 영상창 off')
                    showWindows = 0
                    break
                else:
                    print('잘못된 입력, 다시 입력하세요.')
        elif s == '0':
            print('\n설정값 출력----------')
            if dataRecord == 1:
                print('수면 데이터 상세 기록 on')
            else:
                print('수면 데이터 상세 기록 off')
            if showWindows  == 1:
                print('모니터링용 영상창 on')
            else:
                print('모니터링용 영상창 off')    
            break


def detectTest():
    global irLedState
    b = int(input('\n동작 감지 설정값 입력: '))
    irLedState = input('적외선 램프 on(1) or off(0) 선택: ')
    k = input('모니터링 영상창 on(1) or off(0) 선택: ')
    print('\n테스트를 끝내려면 esc키나 Ctrl + c키를 누르세요')
    if irLedState == '1':
        irledon()
        print('\nirLed on\n')
    if k == '1':
        tempState = 1
    else:
        tempState = 0
    if tempState == 1:
        print('모니터링용 영상창 on')
    else:
        print('모니터링용 영상창 off')
    detect.motionDetect(-1, b, tempState)
    if irLedState == '1':
        irledoff()
        print('\nirLed off')
        cds.clean()
    
  

while True:
    print('\n동작 모드 선택')
    a = input('(1: 수면 패턴 측정, 2: 설정, 3: 테스트, 4: 수면 데이터 분석, 0: 종료): ')

    if '1' == a:
        try:
            os.system("mv data/*.json data/junk")
            os.system("rm -rf data/*.txt")
            print('\n')
            if dataRecord == 1:
                print('수면 데이터 상세 기록 on')
                record.reset() #수면 기록 txt 리셋
                record.sleepDataReset()
            else:
                print('수면 데이터 상세 기록 off')

            if showWindows == 1:
                print('모니터링용 영상창 on')
            else:
                print('모니터링용 영상창 off')

            main()

        except KeyboardInterrupt:
            irledoff()
            print('irled off')
            cds.clean()
            cv2.destroyAllWindows()
            pass
    elif '2' == a:
        setUp()
                
    elif '3' == a:
        while True:
            print('\n 테스트 동작 선택')
            b = input('(1: 동작 감지 테스트, 2: CCTV 화면 스트리밍, 3: CCTV 보안모드, 0: 종료): ')
            if '1' == b:
                try:
                    print('\n동작 감지 테스트 시작')
                    detectTest()
                    print('\n동작 감지 테스트 종료')
                except KeyboardInterrupt:
                    if irLedState == '1':
                        irledoff()
                        print('\nirLed off')
                        cds.clean()
                    print('\n동작 감지 테스트 강제종료')
            elif '2' == b:
                c = input('스트리밍 동작 시간 설정(초): ')
                d = int(c)
                stream.test(d)
                print('CCTV 화면 스트리밍 종료')
            elif '3' == b:
                try:
                    while True:
                        detectPerson()
                except KeyboardInterrupt:
                    pass
                         
            elif '0' == b:
                break
            else:
                print('\n다시 입력해 주세요')
                pass
            
    elif '4' == a:
        os.system("mv data/*.json data/junk") #json 파일 junk폴더로 이동
        os.system("rm -rf data/*.txt") #txt 파일 삭제
        sleepPattern(0) #수면 데이터 분석
        wjson.wjsonTotxt()  #통신에 쓰도록 json.txt 파일에 정보 저장
    elif '0' == a:
        break
    else:
        print('다시 입력해 주세요')

