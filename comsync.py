import asyncio
import numpy as np
import sounddevice as sd

host = ''
port = 65001
fs = 44100
data = None


async def connection_callback(reader, writer):
    global data
    print ('connection accepted')
    #data = (await reader.read()).decode()
    data = np.frombuffer(await reader.read(), dtype = np.float32)
    #sd.play(data, fs)


    def stream_callback(outdata, nsample, time, status):
        outdata[:1024] = data

    stream = sd.OutputStream(callback = stream_callback, samplerate = fs, channels = 1)

    with stream:
        sd.sleep(20000)


async def main():
    server = await asyncio.start_server(connection_callback, host, port)
    async with server:
        await server.serve_forever()

asyncio.run(main())

'''
def stream_callback(outdata, nsample, time, status):
    print ('stream callback')
    global data
    outdata[:] = data

stream = sd.OutputStream(callback = stream_callback, samplerate = fs, channels = 1)

with stream:
    sd.sleep(20000)
'''
