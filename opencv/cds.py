# -*- coding: utf-8 -*- 
#수면 감지 모듈

import RPi.GPIO as GPIO
import time

flag = True 

#GPIO.setmode(GPIO.BCM)

"""
라즈베리파이는 아날로그 값을 읽지 못해 조도센서를 그대로 사용할수 없다
따라서 커페시터를 이용하여 조도센서 값을 읽는 방법사용
조도센서가 빛의 양에 따라 저항이 달라지므로 커패시터에 충전되는시간에 따라 밝고 어둠을 구분
"""
#조도센서 값을 읽어오는 함수
#빛이 있으면 300, 어두워지면 1000 이상을 리턴
#+:1 -:6(그라운드) GPIO핀:7(cds와 커페시터 사이)
def light(pin):
    GPIO.setmode(GPIO.BCM)
    count = 0

    #Output
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.1)

    #input으로 변환
    GPIO.setup(pin, GPIO.IN)

    #pin이 hign가 될때까지 카운트
    while (GPIO.input(pin) == GPIO.LOW):
        count += 1
        if count >= 3000:
            break

    return count

#GPIO 초기화
def clean():
    GPIO.cleanup()


def irLedon(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)

def irLedoff(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

def switch(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=my_callback, bouncetime=500)    

def my_callback(channel):
    global flag
    print("switch pressed")
    flag = ~flag
    if flag == 1:
        while True:
            print('보안모드 동작중')
            time.sleep(0.5)
    else:
        print('수면감지중')

if __name__ == "__main__":
    irLedon(21)


    


#print('on')
#irLedon(26)
#time.sleep(3)
#print('off')
#irLedoff(26)
#time.sleep(3)
#print('on')
#irLedon(26)
#time.sleep(3)
#print('off')
#irLedoff(26)
#clean()
