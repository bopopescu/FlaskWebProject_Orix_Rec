"""
This script runs the FlaskWebProject_Orix_Rec application using a development server.
"""

from os import environ
from FlaskWebProject_Orix_Rec import app
from flask import Flask, request, Markup
from flask import Flask, render_template, Response, request, redirect, url_for
from flask import Flask, stream_with_context, request, Response, flash

import time
from time import sleep
import threading
import datetime

# emulated camera
from camera_opencv import Camera
import scaner_cap 

# real time 
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

# UDP
import socket

# database
from database.Mysql3 import Mysql3

import random

# file move
import shutil
import os

import module

FLAG = 1
message = {}
HOST = []
PORT = []
ID = 0
#app = Flask(__name__)

output_folder = "//172.31.19.191/oklab_database/orix_data_01/FlaskWebProject_Orix_Rec_output/"

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        
def sca_gen():
    """Video streaming generator function."""
    while True:
        velo = scaner_cap.data_get()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + velo + b'\r\n')

@app.route('/rec_stop')
def rec_stop():
    global ID
    global message

    message['id'] = ID
    Camera().change_flag(3)
    print(message)
    if(ID>0):
        message['output_path'] = output_folder + str(ID) + ".avi"

        #output_path = output_folder + str(ID) + ".avi"
        new_path = shutil.move('output3.avi', message['output_path'])
        print(message['output_path'])

        sql = "UPDATE `Drive_recorder` SET `full_path` = '{0}' WHERE `hazard_list_id`= {1}".format(message['output_path'], ID)
        print(sql)
        mysql.indi_regist(sql)
        sql = "UPDATE `hazard_list` SET `full_path` = '{0}' WHERE `id`= {1}".format(message['output_path'], ID)
        print(sql)
        mysql.indi_regist(sql)

        #img_output_folder = output_folder + str(ID) + "/"
        message['img_output_folder'] = output_folder + str(ID) + "/"
        module.video_2_frames(message, 'img_%s.png', mysql)

    return render_template('index.html')

@app.route('/stream')
def stream_view():
    global message
    global ID

    Camera().change_flag(1)

    message['datetime_now'] = datetime.datetime.now()
    message['datetime_now_str'] = message['datetime_now'].strftime("%Y-%m-%d %H:%M:%S")
    message['ID'] = message['datetime_now'].strftime("%Y%m%d%H%M%S")

    sql = "INSERT INTO `hazard_list`(`sub`, `DATE`, `hazard_type`) VALUES ('1000', '" + message['datetime_now_str'] + "', 1)"
    print(sql)
    mysql.indi_regist(sql)

    sql = 'SELECT * FROM `hazard_list` WHERE `sub` = ' + str(1000) + " AND `DATE` = '" + message['datetime_now_str'] + "'"
    print(sql)
    select_ID = mysql.sql_excute_fetch(sql)
    print(select_ID[0])
    print(select_ID[0]['id'])
    ID = select_ID[0]['id']
    rows = generate()


    return Response(stream_with_context(stream_template('index.html', rows=rows)))

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""

    gen_obj = gen(Camera())
    print("gen_obj")
    print(gen_obj)
    #print(gen_obj.next())
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    #rv.enable_buffering(5)
    return rv

def generate():
    global message
    global ID

    while True:
        #for item in data:
        item2 = scaner_cap.data_get()
        item2_format  = '{:>8.5f}'.format(item2)

        message['datetime_rec'] = datetime.datetime.now()
        message['datetime_rec_str'] = message['datetime_rec'].strftime("%Y-%m-%d %H:%M:%S")
        sql = "INSERT INTO `Drive_recorder`(`sub`, `DATE`, `velocity_kmh`, `hazard_list_id`) VALUES ('{0}', '{1}', {2}, {3})".format(1000, message['datetime_rec_str'], item2_format, ID)
        print(sql)
        mysql.indi_regist(sql)

        yield (str(item2_format), 'velocity', ID)
        #yield velo_dict
        sleep(1)



def scaner_init():
    #print("dddd")
    scaner_cap.data_loop()



if __name__ == '__main__':

    mysql = Mysql3(host='172.31.19.191', db_name='orix_data', user='root', target_id=id, target_sub=2)

    thread_1 = threading.Thread(target=scaner_init)
    #thread_2 = threading.Thread(target=scaner_get)
    #thread_3 = threading.Thread(target=connect_UDP)
    thread_1.start()
    #thread_2.start()
    #thread_3.start()

    #connect_UDP()
    
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    #PORT = 9090
    app.run(HOST, PORT, threaded=True)
    print(HOST)
    #app.debug = True
    #server = pywsgi.WSGIServer(("localhost", 9191), app, handler_class=WebSocketHandler)
    print("server.serve_forever()")
    #server.serve_forever()
    print("app.run("", 8080, threaded=True)")
    #app.run("", 8080, threaded=True)