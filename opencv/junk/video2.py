import numpy as np
import cv2
import os

def backSubtraction():
    os.system('sudo modprobe bcm2835-v4l2')
    try:
        print("camera on")   
        cap = cv2.VideoCapture(0)
    except:
        print('error')
        return
    cap.set(3, 480)
    cap.set(4, 320)
    mog = cv2.createBackgroundSubtractorMOG2()
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fps = float(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(3))
    height = int(cap.get(4))
    print('%d' % (fps))
    fcc = cv2.VideoWriter_fourcc(*"DIVX")

    out = cv2.VideoWriter('mycam2.avi', fcc, fps, (width, height))
    print('recording')

   

    while True:
        if cap.isOpened() == False:
            cap.open()
        ret, frame = cap.read()
        if not ret:
            print("video read error")
            break

        fgmask = mog.apply(frame)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

       
        output = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
        cv2.imshow('mask', fgmask)
        out.write(output)
        
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break


    cap.release()
    out.release()
    cv2.destroyAllWindows()

backSubtraction()
