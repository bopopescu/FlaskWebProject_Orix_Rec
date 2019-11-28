
import os
import shutil
import cv2

import datetime

import socket

def video_2_frames(message, image_file, mysql):
    print("video_2_frames")
    # Delete the entire directory tree if it exists.
    video_file = message['output_path']
    image_dir = message['img_output_folder']
    ID = message['id']
    start_time = message['datetime_now']
    frame_time = start_time

    print(video_file)
    if os.path.exists(image_dir):
        shutil.rmtree(image_dir)  

    print(image_dir)
    # Make the directory if it doesn't exist.
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    print(image_file)
    # Video to frames
    i = 0
    cap = cv2.VideoCapture(video_file)
    while(cap.isOpened()):
        flag, frame = cap.read()  # Capture frame-by-frame
        #frame = cv2.resize(frame, (orgHeight / 2, orgWidth / 2))
        

        if flag == False:  # Is a frame left?
            print("flag == False")
            break
        save_path = image_dir+image_file % str(i).zfill(6)

        frame = cv2.resize(frame, (1280, 720))
        cv2.imwrite(save_path, frame)  # Save a frame
        
        print(frame_time)
        frame_time_str = frame_time.strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO `img_path`(`img_path`, `DATE`, `hazard_list_id`, `frame_id`) VALUES ('{0}', '{1}', {2}, {3})".format(save_path, frame_time_str, ID, i)
        print(sql)
        mysql.indi_regist(sql)

        print('Save', save_path)
        i += 1
        frame_time = frame_time + datetime.timedelta(milliseconds=33.333)
        
    cap.release()  # When everything done, release the capture


def SemanticSeg_client(hazard_list_id):

    HOST = '172.31.19.115'
    PORT = 50007
    ADDRESS = '172.31.19.115' # 

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

    msg = str(hazard_list_id)
    s.sendto(msg.encode('utf-8'), (ADDRESS, PORT))

    
    s.close()

    #s =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #s.connect(('172.31.19.115', 50007))
    ##s.sendall(b'1234567')
    #send_data = str(hazard_list_id).encode('utf-8')
    #print(hazard_list_id)
    #print(send_data)
    #s.sendall(send_data)
    ##s.sendall(b'15686')
    #data = s.recv(1024)
    ##
    #print(repr(data))


if __name__ == '__main__':
    SemanticSeg_client(15707)
    #SemanticSeg_client(0)