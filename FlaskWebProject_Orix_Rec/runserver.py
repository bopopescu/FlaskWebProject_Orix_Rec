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

FLAG = 1
message = {}
HOST = []
PORT = []

@app.route("/", methods=["GET", "POST"])
def exercise():
    if request.method == "GET":
        return """
        下に整数を入力してください。奇数か偶数か判定します
        <form action="/" method="POST">
        <input name="num"></input>
        </form>"""
    else:
        return """
        {}は{}です！
        <form action="/" method="POST">
        <input name="num"></input>
        </form>""".format(str(request.form["num"]), ["偶数", "奇数"][int(request.form["num"]) % 2])

def func1():
    global FLAG
    while 1:
        print("func1")
        print(FLAG)
        if(FLAG == 0):
            break
        time.sleep(1)

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

@app.route('/change_camera_state', methods=['GET', 'POST'])
def change_camera_state():
    global message
    global FLAG
    global HOST
    global PORT

    print(request.form)
    print(request.form.to_dict(flat=False))
    message = request.form.to_dict(flat=False)
    
    message["host"] = HOST
    message["port"] = PORT

    try:
        if request.method == 'POST':
            #return request.form['test']
            print(message['camera_state'])
            if message['camera_state'] == [u'Start_recording']:
                message['camera_state'] = '録画中'.decode('utf-8')
                Camera().change_flag(1)
               
                message['velo'] = scaner_cap.data_get()

                sql = "UPDATE `"+table_name+"` SET lddt=" + str(lddt) + ", ldd=" + str(ldd) + ", rev=" + str(rev) + ", sev=" + str(sev) + ", G_max=" + str(G_max) + " WHERE normal_list_id=" + str(id)
                #print(sql)
                mysql.indi_regist(sql)

            if message['camera_state'] == [u'End_of_recording']:
                message['camera_state'] = '録画開始'.decode('utf-8')
                FLAG = 0
                #thread_1.end()
                Camera().change_flag(3)
                
            print(message)
            return render_template('index.html', message=message);

    except Exception as e:
        return str(e)

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.disable_buffering()
    return rv

data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0] 
def generate():
    while True:
        #for item in data:
        item2 = scaner_cap.data_get()
        print(item2)
        yield str(item2)
        sleep(1)



@app.route('/stream')
def stream_view():
    scaner_state
    try:
        if request.method == 'POST':
            if message['scaner_state'] == [u'Start_recording']:
                rows = generate()
                return Response(stream_with_context(stream_template('index.html', rows=rows)))

    except Exception as e:
        pass


@app.route('/scaner_get')
def scaner_get():
    global message
    while 1:
        print("scaner_get():")
       
        print(message)
        return Response(sca_gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def scaner_init():
    #print("dddd")
    scaner_cap.data_loop()


def connect_UDP():
    inst = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    inst.bind(('127.0.0.1', 50007))
    while True:
        data, addr = inst.recvfrom(1024)
        print("data: {}, addr: {}".format(data, addr))

@app.route('/pipe')
def pipe():
   if request.environ.get('wsgi.websocket'):
       ws = request.environ['wsgi.websocket']
       while True:
           time.sleep(1)
           message = 'aaaaaa'
           if message is None:
               break
           datetime_now = datetime.datetime.now()
           data = {
               'time': str(datetime_now),
               'message': message
           }
           ws.send(json.dumps(data))
           print(message)
           print(data)
   return


if __name__ == '__main__':

    mysql = Mysql3(host='172.31.19.191', db_name='orix_data', user='root', target_id=id, target_sub=2)

    thread_1 = threading.Thread(target=scaner_init)
    thread_2 = threading.Thread(target=scaner_get)
    #thread_3 = threading.Thread(target=connect_UDP)
    thread_1.start()
    thread_2.start()
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