from threading import Thread
from copy import deepcopy

import queue
import cv2

class Camera(Thread):
    def __init__(self, cam, normalQue, detectedQue):
        Thread.__init__(self)
        self.__cam = cam
        self.__normalQue = normalQue
        self.__detectedQue = detectedQue
        self.__shouldStop = False
        
    def __del__(self):
        self.__cam.release()
        print('Camera released')
        
    def run(self):
        while True:
            rval, frame = self.__cam.read()

            if rval:
                frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
                _, jpeg = cv2.imencode('.jpg', frame)

                self.__normalQue.put(jpeg.tobytes())
                self.__detectedQue.put(deepcopy(jpeg.tobytes()))

            if self.__shouldStop:
                break

    def stopCamera(self):
        self.__shouldStop = True