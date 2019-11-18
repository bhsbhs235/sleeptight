# -*- coding: utf-8 -*-
#수면데이터 json 작성 코드


import json
import time
import datetime

def writejson(pastTime, currentTime, d, sleeppattern, start_end, number): #함수 인자 pastTime(이전시간), currentTime(현재시간), day(날짜), sleeppattern(깊은잠 or 얕은잠), start_end flag, number(파일이름 넘버링)
        
    #지난 시간 구하기
    totaloldseconds = int(pastTime) #지난시간을 초 단위로 변환
    currentoldsecond = totaloldseconds % 60 #지난 시간의 초 구하기
    totaloldMinutes = totaloldseconds // 60 #지난시간을 분으로 변환
    currentoldMinute = totaloldMinutes % 60 #지난 시간의 분 구하기
    totaloldHours = totaloldMinutes // 60 # 지난 흐른시간을 시간으로 변환
    currentoldHour = totaloldHours % 24 # 지난시간의 시 구하기
    currentoldHour += 9 #한국시간으로 변화
    if currentoldHour > 24:
        currentoldHour -= 24



    #현재 시간 구하기
    totalseconds = int(currentTime) #현재시간을 초 단위로 변환
    currentsecond = totalseconds % 60 #현재 시간의 초 구하기
    totalMinutes = totalseconds // 60 #현재시간을 분으로 변환
    currentMinute = totalMinutes % 60 #현재 시간의 분 구하기
    totalHours = totalMinutes // 60 # 현재 흐른시간을 시간으로 변환
    currentHour = totalHours % 24 # 현재시간의 시 구하기
    currentHour += 9 #한국시간으로 변화
    if currentHour > 24:
        currentHour -= 24
    #print('Hour',currentHour, "Minute",currentMinute, "Second",currentsecond)
    
    #현재날짜 구하기
    #d = datetime.date.today() #한번만 실행 하면 되기에 함수 인자로 넘겨 받음
    
    name = 'data/' + str(number) + d.strftime('%Y%m%d') + '.json'
    nametxt = 'data/' + str(number) + '.txt'
    day = int(d.strftime('%Y%m%d'))
    sleeptime = (currentoldHour*100) +  currentoldMinute
    patterntime = totalMinutes - totaloldMinutes

    print('filename: ' + name)
    print('day: %d ' % day)
    print('sleeptime: %d' %sleeptime)
    print('sleeppattern: %d' % sleeppattern)
    print('start_end: %d' % start_end)
    print('patterntime: %d' % patterntime)
    
    sleepData1 = {
        'day' : day,
        'sleeptime' : sleeptime,
        'sleeppattern' : sleeppattern,
        'start_end' : start_end,
        'patterntime' : patterntime
    }

    sleepData = {
        "patterntime": patterntime,
        "start_end": start_end,
        "sleeppattern": sleeppattern,
        "day": day,
        "sleeptime": sleeptime}
    if patterntime < 10:
        patterntime = '0' + str(patterntime)
    else:
        patterntime = str(patterntime)
    sleepDatatxt = '{"patterntime": %s, "start_end": %d, "sleeppattern": %d, "day": %d, "sleeptime": %d}' %(patterntime, start_end, sleeppattern, day, sleeptime) 
    jsonString = json.dumps(sleepData)

#    print('\njsonString')
#    print(jsonString)

    with open(name, 'w') as make_file:
        json.dump(sleepData, make_file, ensure_ascii=False)    

    f = open(nametxt, 'w')
    f.write(sleepDatatxt)
    f.close()    

def jsonTotxt():    #json to TXT file
    f1 = open("json.txt", 'w')
    f1.close()
    f1 = open("json.txt", 'a')
    d = datetime.date.today()
    number = 1
    f = open('data/' + str(number) +'.txt', 'r')
    try:
        while True:
            line = f.readline()
            f.close()
            f1.write(line+'\n')
            number += 1
            f = open('data/' + str(number) + '.txt', 'r')
    except:
        f.close()

def wjsonTotxt():
    try:
        jsonTotxt()
    except FileNotFoundError:
        f.close()


def backup():
    d = datetime.date.today()
    name = 'backup/' + d.strftime('%Y%m%d') + '.txt'
    f = open("json.txt", 'r')
    # 백업 내용 나머지
