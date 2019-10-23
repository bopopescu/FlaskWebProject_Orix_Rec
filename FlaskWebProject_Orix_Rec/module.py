
import os
import shutil
import cv2

import datetime

def video_2_frames(message, image_file, mysql):
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
        if flag == False:  # Is a frame left?
            break
        save_path = image_dir+image_file % str(i).zfill(6)
        cv2.imwrite(save_path, frame)  # Save a frame
        
        print(frame_time)
        frame_time_str = frame_time.strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO `img_path`(`img_path`, `DATE`, `hazard_list_id`, `frame_id`) VALUES ('{0}', '{1}', {2}, {3})".format(save_path, frame_time_str, ID, i)
        print(sql)
        mysql.indi_regist(sql)

        print('Save', save_path)
        i += 1
        frame_time = frame_time + datetime.timedelta(milliseconds=100)
        
    cap.release()  # When everything done, release the capture