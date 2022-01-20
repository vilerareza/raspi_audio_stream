
'''
this code test receive audio from socket and play
'''

import io
import socket
import selectors
import sounddevice as sd
import numpy as np
from threading import Condition
import threading

t_listen = None
host =''
port = 65001
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sel = selectors.DefaultSelector()
buffer = io.BytesIO()
fs = 44100
audioData =  bytes()
condition = Condition()
t_listen = None
connSock = None
sockFile = None

def accept_connection(sock):
    sock.accept_conn
    connSock, addr = sock.accept()
    connSock.setblocking(False)
    sel.register(connSock, selectors.EVENT_READ, data = addr)
    print ('accepted connection from ', addr)

def __listen():
    global buffer
    global audioData
    global buffer_condition
    global lsock
    # global connSock
    global sockFile
    global sel
    # Listen for new connection
    lsock.bind((host,port))
    lsock.listen()
    print('listening on, ', (host,port))
    connSock, addr = lsock.accept()
    #sel.register(lsock, selectors.EVENT_READ, data = None)
    print ('accepted connection from ', addr)
    try:
        sockFile = connSock.makefile('rb')
        create_audio_stream()
    except:
        print ('closing connection to ', addr)
        lsock.close()


def listen_thread():
    global t_listen
    # Starting the listen thread
    if not t_listen:
        t_listen = threading.Thread(target = __listen)
        t_listen.start()
        print ('socket thread is alive')

def stream_callback(outdata, nsample, time, status):
    global sockFile
    global t_listen
    global condition
    global lsock

    if sockFile:
        try:
            print ('OK')
            sockData = sockFile.read(4096)
            temp = np.frombuffer(sockData, dtype=np.float32)
            temp = np.reshape(temp, (1024,1))
            outdata[:1024] = temp
        except Exception as e:
            #t_listen = None
            print (e)
            #sockFile = None
            #listen_thread()
            with condition:
                condition.notify_all()

    else:
        pass
        #print ('None')


listen_thread()

def create_audio_stream():

    global condition

    print ('creating audio stream')
    stream = sd.OutputStream(callback = stream_callback, samplerate = fs, channels = 1, blocksize=1024)

    with stream:
        with condition:
            condition.wait()
        print('audio stream closed')
