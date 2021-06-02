from threading import Thread

import cv2
import traceback

class DetectionVideoStream(Thread):
    def __init__(self, framesQue):
        Thread.__init__(self)
        
        self.__frames = framesQue
        self.__img = None
        self.__faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def run(self):
        while True:
            if self.__frames.empty():
                continue
            
            self.__img = self.__detectFace()

    def gen(self):
        while True:
            try:
                if self.__img is None:
                    print('Detected stream frame is none')

                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + self.__img + b'\r\n')
            except:
                traceback.print_exc()
                print('Detection video stream genenation exception')
    
    def __detectFace(self):
        retImg = None

        try:
            img = self.__frames.get()

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = self.__faceCascade.detectMultiScale(gray, 1.1, 4)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

            (_, encodedImage) = cv2.imencode('.jpg', img)

            retImg = encodedImage.tobytes()
        except:
            traceback.print_exc()
            print('Face detection exception')

        return retImg