"""
This script runs the FlaskWebProject_Orix_Rec application using a development server.
"""

from os import environ
#from FlaskWebProject_Orix_Rec import app
from flask import Flask, request, Markup
from flask import Flask, render_template, Response, request, redirect, url_for
import time
import threading

# emulated camera
from camera_opencv import Camera
import scaner_cap

# real time
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

# database
from database.Mysql3 import Mysql3

# UDP
import socket

FLAG = 1
message = {}
HOST = []
PORT = []

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def exercise():
    if request.method == "GET":
        return """
        <form action="/" method="POST">
        <input name="num"></input>
        </form>"""
    else:
        return """
        <form action="/" method="POST">
        <input name="num"></input>
        </form>""".format(str(request.form["num"]), ["Gu", "KI"][int(request.form["num"]) % 2])

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
                message['camera_state'] = 'Rec'.decode('utf-8')
                Camera().change_flag(1)

                message['velo'] = scaner_cap.data_get()

            if message['camera_state'] == [u'End_of_recording']:
                message['camera_state'] = 'Rec start'.decode('utf-8')
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

def scaner_get():
    global message
    while 1:
        message['velo'] = scaner_cap.data_get()
        print(message)
        render_template('index.html', message=message)


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


    #thread_1 = threading.Thread(target=scaner_init)
    #thread_2 = threading.Thread(target=scaner_get)
    thread_3 = threading.Thread(target=connect_UDP)
    #thread_1.start()
    #thread_2.start()
    thread_3.start()

    #connect_UDP()

    app.debug = True

    host = 'localhost'
    port = 8082

    host_port = (host, port)
    server = WSGIServer(
        host_port,
        app,
        handler_class=WebSocketHandler
    )
    server.serve_forever()
