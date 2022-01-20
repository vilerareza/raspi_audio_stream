
import io
import socket
import selectors
import threading
import sounddevice as sd
import numpy as np
from threading import Condition

t_listen = None
host =''
port = 65001
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sel = selectors.DefaultSelector()
buffer = io.BytesIO()
fs = 44100
buffer_condition = Condition()
audioData =  bytes()

def __accept_wrapper(sock):
    global sel
    # accept new connections
    conn, addr = sock.accept()
    print ('accepted connection from ', addr)
    conn.setblocking(False)
    events = selectors.EVENT_READ
    sel.register(conn,events, data = addr)

def __service_connection (key, mask):
    global sel
    global buffer
    global buffer_conditio
    global audioData
    # Receive data
    sock = key.fileobj
    data = key.data
    try:
        sockFile = sock.makefile('rb')
        if mask & selectors.EVENT_READ:
        #receiving data
            sockData = sockFile.read(1024)
            buffer.write(sockData)
            buffer.truncate()
            with buffer_condition:
                #buffer_condition.notify_all()
                audioData = buffer.getvalue()
                #print('lentemp'+str(len(temp)))
                buffer_condition.notify_all()
            buffer.seek(0)
            #if sockData:
                #print('there is some data')
                #with buffer_condition:
                #    buffer = sockData
                #    buffer_condition.notify_all()
            #self.__write(camData)
            #check the camera connection
            #sock.send(b'1')
    except:
         print ('closing connection to ', data)
         sel.unregister(sock)
         sock.close()


def __listen():
    # Listen for new connection
    lsock.bind((host,port))
    lsock.listen()
    print('listening on, ', (host,port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ | selectors.EVENT_WRITE, data = None)
    while True:
        events = sel.select(timeout = None) #this blocks
        for key, mask in events:
            if key.data is None:
                print('new connection')
                __accept_wrapper(key.fileobj)
                #print('new connection')
            else:
                #print('service connection')
                __service_connection(key, mask)

def listen_thread():
    global t_listen
    # Starting the listen thread
    if not t_listen:
        t_listen = threading.Thread(target = __listen)
        t_listen.start()
        print ('socket thread is alive')

def stream_callback(outdata, nsample, time, status):
    global buffer
    global buffer_condiiton
    global audioData
    with buffer_condition:
        buffer_condition.wait()
        temp = np.frombuffer(bytearray(audioData), dtype=np.float32)
        print(str(len(temp)))
        try:
            #temp = np.frombuffer(bytearray(audioData), dtype=np.float32)
            outdata[:256] = np.reshape(temp, (256,1))
            print (str(nsample))
            #print (str(outdata[:5]))
        except:
            print ('data size issue')
        #print ('lendata'+str(len(data)))

listen_thread()

stream = sd.OutputStream(callback = stream_callback, samplerate = fs, channels = 1, blocksize = 256)

with stream:
    sd.sleep(20000)

