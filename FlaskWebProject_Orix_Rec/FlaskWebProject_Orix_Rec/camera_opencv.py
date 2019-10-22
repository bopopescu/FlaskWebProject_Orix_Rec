import cv2
from base_camera import BaseCamera




def cv_fourcc(c1, c2, c3, c4):
        return (ord(c1) & 255) + ((ord(c2) & 255) << 8) + \
            ((ord(c3) & 255) << 16) + ((ord(c4) & 255) << 24)


FLAG_CAM = 0
fourcc = []
out = []

class Camera(BaseCamera):
    video_source = 0
    

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    def change_flag(self, flag):
        print(flag)
        global FLAG_CAM
        FLAG_CAM = flag

    @staticmethod
    def frames():
        global FLAG_CAM
        global fourcc
        global out

        x = 100
        y = 100
        w = 1920
        h = 1080
        FRAME_RATE=10
        accum_time = 0
        curr_fps = 0
        
        camera = cv2.VideoCapture(Camera.video_source)

        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
        while True:
            # read current frame
            _, img = camera.read()
            #print(FLAG_CAM)
            #print(fourcc)
            #print(out)
            img = cv2.resize(img, (int(w), int(h)))

            if FLAG_CAM == 1:
                #print("CAM init")
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('output3.avi',fourcc, 10, (w, h))
                FLAG_CAM = 2
            elif FLAG_CAM == 2:
                #print("CAM rec")
                out.write(img) 
            elif FLAG_CAM == 3:
                #print("CAM end")
                out.release()
                FLAG_CAM = 0
            else:
                #print("CAM display")
                pass
            #print(out)

            # encode as a jpeg image and return it
            
            img = cv2.resize(img, (int(w/2), int(h/2)))
            yield cv2.imencode('.jpg', img)[1].tobytes()

        