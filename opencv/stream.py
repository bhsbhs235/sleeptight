# -*- coding: utf-8 -*-
#CCTV 화면을 웹페이지에 스트리밍
#라즈베리파이 ip 주소로 접속 포트는 5000
from flask import Flask, render_template, Response, request
from camera import VideoCamera
import os
from multiprocessing import Process
import time

os.system('sudo modprobe bcm2835-v4l2')
app = Flask(__name__)

from flask import request

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        time.sleep(0.01)
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
      

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def run():
    app.run(host='0.0.0.0', debug=True)



if __name__ == '__main__':
    try:
        server = Process(target=run)
        server.start()
    except:
        server.terminate()
        server.join()


