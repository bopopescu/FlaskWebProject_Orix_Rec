import sys
import platform

# need to find VEN.pyd
is_64bit = platform.architecture()[0]
if is_64bit == "64bit":
    sys.path.append('FlaskWebProject_Orix_Rec/static/vs2013')

import VEN
import time

com = VEN.VENCommunicationSystem()
# VEN initilization
#com.init("239.255.0.1", 64101)
com.init("239.255.0.1", 63999)

# recieve message from VEN, one read second frequency
# the message is 2 float value, stop reading message when the first message value is not -1
in_sender = "car"
in_msg = "info"
data_out = -1
nb_try = 0
print('in')
data_out = []


def data_get():
    return data_out

def data_loop():
    global data_out
    global nb_try

    while 1:
        from_scaner_data = []
        time.sleep(1)
        if com.read_float(in_sender, in_msg, from_scaner_data, 2) == 0:
            #print('recieve ' + in_sender + '/' + in_msg)
            #print(from_scaner_data)
            #print('v [km/h] : ' + str(from_scaner_data[0]*3.6))
            data_out = from_scaner_data[0]*3.6
        else:
            #print(com.get_error_string())
            data_out = com.get_error_string()
        nb_try = nb_try + 1
        #print nb_try
