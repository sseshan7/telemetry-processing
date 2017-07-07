import serial
import asyncio
import websockets
import json
from collections import defaultdict
import time
import math

### Configure Stuff ###
WEBSOCKET_ADDRESS = 'ws://localhost:2009' # Change this to whatever

SERIAL_PORT = '/dev/tty.usbserial'
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1 # Seconds
histories = defaultdict(list)
#######################

async def client_handler(websocket, path):
    print('entered')
    name = await websocket.recv()
    print("< {}".format(name))
    name_args = name.split()
    # histories is a dictionary of key names to list values.
    # each list contains a dictionary with two keys: "timestamp" and "value".
    if name_args[0] == 'dictionary':
        with open('dictionary.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = json.dumps(data, separators=(',', ':'))
        print(text)
        await websocket.send(text)
    elif name_args[0] == 'history':
        system = name_args[1]
        if system == 'pwr.temp':
            hist_dict = {'type': 'history', 'id': 'pwr.temp', 'value': histories}
            sock_data = json.dumps(hist_dict, separators=(',', ':'))
            print(sock_data)
            await websocket.send(sock_data)

async def generateData():
    while True:
        await asyncio.sleep(1)
        t = int(time.time())
        var = {'timestamp': t, 'value': math.sin(t)}
        histories['pwr.temp'].append(var)


start_server = websockets.serve(client_handler, 'localhost', 2009)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.ensure_future(generateData())
asyncio.get_event_loop().run_forever()

'''
async def dump_to_socket():
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)

    async with websockets.connect(WEBSOCKET_ADDRESS) as socket:
        still_reading = True
        while still_reading:
            data = ser.readline()
            # Stops reading data if it recieves an empty line, might not be what we want
            if not data:
                still_reading = False
            else:
                data = float(data.strip())
                await socket.send(data)


if __name__ == "__main__":
    # Socket should close itself after it's done
    server = websockets.serve(callback, 'localhost', 2009)
    #asyncio.get_event_loop().run_until_complete(dump_to_socket())
'''
