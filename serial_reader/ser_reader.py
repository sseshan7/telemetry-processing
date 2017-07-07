import serial_asyncio
import asyncio
import websockets
import json
from collections import defaultdict
import time
import math

# Program Flow:
# - continuously:
# -- read data from serial
# -- listen for msgs from client
# -- update subscribers
#
# - when msg is recieved:
# -- check type of msg (subscribe, unsubscribe, ...) and handle
#
# - subscribe/unsubscribe:
# -- add/remove subscriber to/from set
#
# - dictionary:
# -- send structure of spaceship json object???
#
# - history:
# -- send history of values for item as json object

### Configure Stuff ###
WEBSOCKET = {
    'host': 'localhost',
    'port': 2009
}

SERIAL_PORT = '/dev/tty.usbserial'
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1  # Seconds
#######################
# ser = serial.Serial(port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)
### Global Variables ###
subscriptions = set()  # if we have a finite number, should be a dict
data = defaultdict(list)  # might end up being a dict of pandas dataframes or something


class SerialReader(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        print('port opened:', transport)
        transport.serial.rts = False
        transport.write(b'hello world\n')  # test write

    def data_received(self, incoming):
        # temporary, should instead parse and save data
        print('received:', incoming)

    def connection_lost(self, exc):
        print('connection lost')
        self.transport.loop.stop()


async def receive_messages(websocket, path):
    still_reading = True
    while still_reading:
        # Assuming msgs are recieved as text frames, not binary frames
        message = await websocket.recv()
        message = message.split()
        # I'm assuming (maybe wrongly) that msgs are in the form
        # "history (element)" and so on for the other commands
        if message[0] == "history":
            await handle_history(element=message[1])
            # elif ...
        elif message[0] == 'dictionary':
            with open('dictionary.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            text = json.dumps(data, separators=(',', ':'))
            print(text)
            await websocket.send(text)


async def generateData():
    while True:
        await asyncio.sleep(1)
        t = int(time.time())
        var = {'timestamp': t, 'value': math.sin(t)}
        histories['pwr.temp'].append(var)


async def update_subscribers(websocket, path):
    # foreach subscription in subscriptions, send live data
    global subscriptions


async def handle_history(websocket, path, element):
    # send data as json object
    global data
    global subscriptions


def handle_subscribe(element):
    # add subscription to subscriptions
    global subscriptions


def handle_unsubscribe(element):
    # remove subscription from subscriptions
    global subscriptions


if __name__ == '__main__':
    # probably read serial data here
    loop = asyncio.get_event_loop()
    serial_coroutine = serial_asyncio.create_serial_connection(loop,
                                                               SerialReader,
                                                               SERIAL_PORT,
                                                               SERIAL_BAUDRATE)

    start_server = websockets.serve(receive_messages, WEBSOCKET['host'],
                                    WEBSOCKET['port'])
    loop.run_until_complete(start_server)
    asyncio.ensure_future(serial_coroutine)
    loop.run_forever()


# start_server = websockets.serve(client_handler, 'localhost', 2009)
# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.ensure_future(generateData())
# asyncio.get_event_loop().run_forever()

# async def dump_to_socket():
#     ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)
#
#     async with websockets.connect(WEBSOCKET_ADDRESS) as socket:
#         still_reading = True
#         while still_reading:
#             data = ser.readline()
#             # Stops reading data if it recieves an empty line, might not be what we want
#             if not data:
#                 still_reading = False
#             else:
#                 data = float(data.strip())
#                 await socket.send(data)
#
#
# if __name__ == "__main__":
#     # Socket should close itself after it's done
#     server = websockets.serve(callback, 'localhost', 2009)
#     #asyncio.get_event_loop().run_until_complete(dump_to_socket())
