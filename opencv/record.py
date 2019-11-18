# -*- coding: utf-8 -*-
#수면 패턴 분석을 위한 기록 코드
#동작감지를 한것을 시간를 포함하여 txt파일에 정보 기록
import detect
import time
#import sys
import cds




def reset():
    f = open("sleep.txt", 'w')
    f.close()


def writetxt(contour, light):
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
    f = open("sleep.txt", 'a')
    data = "%d시%d분%d초,%d,%d\n" % (currentHour, currentMinute, currentsecond, contour, light)
    f.write(data)
    f.close()    
    

def sleepDataReset():
    f = open("sleepData.txt", 'w')
    f.close()

def sleepData(time1, time2, contour):
    f = open("sleepData.txt", 'a')
    data = "%d,%d,%d,\n" % (time1, time2, contour)
    f.write(data)
    f.close() 


def jsonTotxt():
    i = 1
    
    



def main():
    reset()
    print('수면 패턴 분석을 위한 기록 시작')
    cds.irLedon(14)
    a = input('동작 감지 민감도 설정: ')
    b = input('delay time: ')
    print('delay')
    time.sleep(b)
    light = 0
    while True:
        print('동작 감지중')
        area = detect.motionDetect(0, a, 0)
        print('동작 감지됨, 정보 기록')
        writetxt(area, light)
    

def start():    
    try:
        main()
    except KeyboardInterrupt:
        cds.irLedoff(14)
        cds.clean()
        print('end')
#        sys.exit()


