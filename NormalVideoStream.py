from threading import Thread

import traceback
import cv2

class NormalVideoStream(Thread):
    def __init__(self, framesQue):
        Thread.__init__(self)
        self.__frames = framesQue
        self.__img = None

    def run(self):
        while True:
            if self.__frames.empty():
                continue

            self.__img = self.__frames.get()

    def gen(self):
        while True:
            try:
                if self.__img is None:
                    print('Normal stream frame is none')
                    continue

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + self.__img + b'\r\n')
            except:
                traceback.print_exc()
                print('Normal video stream genenation exception')