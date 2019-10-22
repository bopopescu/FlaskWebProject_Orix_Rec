
import os
import shutil
import cv2

def video_2_frames(video_file, image_dir, image_file):
    # Delete the entire directory tree if it exists.
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
        cv2.imwrite(image_dir+image_file % str(i).zfill(6), frame)  # Save a frame
        print('Save', image_dir+image_file % str(i).zfill(6))
        i += 1

    cap.release()  # When everything done, release the capture