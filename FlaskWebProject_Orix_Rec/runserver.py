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

import pandas as pd

import os

import glob
ls_file_name = glob.glob('./*')
print(ls_file_name)

FLAG = 1
message = {}
HOST = []
PORT = []
ID = 0
#app = Flask(__name__)

output_folder = "//172.31.19.191/oklab_database/orix_data_01/FlaskWebProject_Orix_Rec_output/"

mysql = Mysql3(host='172.31.19.191', db_name='orix_data', user='root', target_id=id, target_sub=2)

post_dict = {"apple":1, "orange":2, "banana":3, "drive_recorder_id":0}

post_dict['hazard_id'] = 0
post_dict['Co_Ltd'] = "-"
post_dict['number'] = "-"
post_dict['Chassis_number'] = "-"
post_dict['sub'] = 0
post_dict['Model_name'] = "-"


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
    print("==========\nrec_stop\n==========")
    global ID
    global message

    message['id'] = ID
    Camera().change_flag(3)
    print(message)
    if(ID>0):
        message['output_path'] = output_folder + str(ID) + ".avi"

        #output_path = output_folder + str(ID) + ".avi"
        print("shutil.move")
        new_path = shutil.copy2('output3.avi', message['output_path'])
        print(message)

        sql = "UPDATE `Drive_recorder2` SET `full_path` = '{0}' WHERE `hazard_list_id`= {1}".format(message['output_path'], ID)
        print(sql)
        mysql.indi_regist(sql)
        sql = "UPDATE `hazard_list` SET `full_path` = '{0}' WHERE `id`= {1}".format(message['output_path'], ID)
        print(sql)
        mysql.indi_regist(sql)

        #img_output_folder = output_folder + str(ID) + "/"
        message['img_output_folder'] = output_folder + str(ID) + "/"
        print("module.video_2_frames(message, 'img_%s.png', mysql)")
        module.video_2_frames(message, 'img_%s.png', mysql)
        module.SemanticSeg_client(message['id'])

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
        
        sql = "INSERT INTO `driving_simulator_log`(`sub`, `DATE`, `velocity_kmh`, `hazard_list_id`) VALUES ('{0}', '{1}', {2}, {3})".format(1000, message['datetime_rec_str'], item2_format, ID)
        print(sql)
        mysql.indi_regist(sql)

        yield (str(item2_format), 'velocity', ID)
        #yield velo_dict
        sleep(0.5)






def scaner_init():
    #print("dddd")
    scaner_cap.data_loop()

@app.route("/go_result")
def go_result():
    return render_template("result.html", post_dict=post_dict)

@app.route("/go_home")
def go_home():
    return render_template("index.html")


@app.route("/go_result_submit", methods=['GET','POST']) # アドレス"/"の時にget_form()を実行しますよ、フォームのget,post両方対応しますよ
def go_result_submit():
   if request.method == 'POST':
      result = request.form
      if(result['drive_recorder_id']):
          post_dict['drive_recorder_id'] = result['drive_recorder_id'].decode('utf-8')

          sql = "SELECT * FROM `hazard_list` WHERE `normal_list_id` = {}".format(post_dict['drive_recorder_id'])
          print(sql)
          select_result = mysql.sql_excute_fetch(sql)
          print(select_result)
          if(select_result):
              post_dict['hazard_id'] = select_result[0]['id']
              post_dict['Co_Ltd'] = select_result[0]['Co_Ltd']
              post_dict['number'] = select_result[0]['number']
              post_dict['Chassis_number'] = select_result[0]['Chassis_number']
              post_dict['sub'] = select_result[0]['sub']
              post_dict['Model_name'] = select_result[0]['Model_name']
              post_dict['v10s'] = [select_result[0]["v{:02d}".format(i+1)] for i in range(11)]
              post_dict['t10s'] = [i+1 for i in range(11)]

              RaderChart_name_lsit = ["a_min_norm", "sea_norm", "sea_norm", "sea_norm", "rev_norm"]
              post_dict['RaderChart_value'] = [select_result[0][r_var_name] for r_var_name in RaderChart_name_lsit]
              post_dict['RaderChart_name'] = RaderChart_name_lsit


          sql = "SELECT * FROM `normal_list` WHERE `id` = {}".format(post_dict['drive_recorder_id'])
          print("v10s:{}".format(post_dict['v10s']))
          print("RaderChart_name:{}".format(post_dict['RaderChart_name']))
          print(sql)
          select_result = mysql.sql_excute_fetch(sql)
          print(select_result)
          if(select_result):
              post_dict.update(select_result[0])
              rank_dict = rank_dict_get(post_dict['drive_recorder_id'])
              post_dict.update(rank_dict)


   print(post_dict)
   #print("LLLLLLLLLLLLLL")
   #print(post_dict['g_min_rank'])
   return render_template("result.html", post_dict=post_dict)


def rank_dict_get(drive_recorder_id):
    
    dataset_folder = "dataset"
    dataset_name = "data_analy_GT_notNAN4.csv"
    dataset_path = dataset_folder + "/" + dataset_name
    #df = pd.read_csv("wine.txt", sep="\t", index_col=0)
    df = pd.read_csv(dataset_path, sep=',')

    rank_dict = {}
    col_list = df.columns
    for var in col_list:
        print(var)
        df_rank = df.rank(numeric_only=True, method='min')
        df_sort = df.sort_values(var).reset_index()
        df_sort2 = df_sort.query('drive_recorder_id == {}'.format(drive_recorder_id))
        df_index = df_sort2.index[0]
        rank_dict['{}_rank'.format(var)] = df_index

    rank_dict['sample_num'] = len(df.index)
    return rank_dict


@app.route("/refresh")
def refresh():
    return render_template("result.html", post_dict=post_dict)

if __name__ == '__main__':

    #mysql = Mysql3(host='172.31.19.191', db_name='orix_data', user='root', target_id=id, target_sub=2)

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
    #app.run(HOST, PORT, threaded=True)
    app.run(debug=False, host='172.31.19.144', port=80, threaded=True)
    print(HOST)
    #app.debug = True
    #server = pywsgi.WSGIServer(("localhost", 9191), app, handler_class=WebSocketHandler)
    print("server.serve_forever()")
    #server.serve_forever()
    print("app.run("", 8080, threaded=True)")
    #app.run("", 8080, threaded=True)