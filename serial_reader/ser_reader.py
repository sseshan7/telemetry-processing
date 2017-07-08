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
# subscriptions = set()  # if we have a finite number, should be a dict
histories = defaultdict(list)  # might end up being a dict of pandas dataframes or something
subscriber_id = None


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
    count = 1
    while still_reading:
        print('waiting for message {}'.format(count))
        count += 1
        # Assuming msgs are recieved as text frames, not binary frames
        message = await websocket.recv()
        print('incoming: {}'.format(message))
        message = message.split()
        if message[0] == "history":
            craft_system = message[1]
            hist_dict = {'type': 'history', 'id': craft_system, 'value': histories[craft_system]}
            sock_data = json.dumps(hist_dict, separators=(',', ':'))
            print(sock_data)
            await websocket.send(sock_data)
        elif message[0] == 'dictionary':
            data = None
            with open('dictionary.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            sock_data = json.dumps(data, separators=(',', ':'))
            print(sock_data)
            await websocket.send(sock_data)
        elif message[0] == 'subscribe':
            craft_system = message[1]
            print('craft_system id: {}'.format(craft_system))
            subscriber_id = craft_system
            await notify_subscribers(websocket, subscriber_id)


async def generateData():
    while True:
        await asyncio.sleep(1)
        t = int(time.time() * 1000)
        var = {'timestamp': t, 'value': math.sin(t)}
        histories['pwr.temp'].append(var)

async def notify_subscribers(websocket, sub_id):
    if sub_id is None:
        print('subscriber_id is NONE!!!!')
    else:
        print('notify entered')
        while True:
            print('notify entered again')
            await asyncio.sleep(1)
            data_dict = data_dict = {'type': 'data', 'id': sub_id, 'value': histories[sub_id][-1]}
            sock_data = json.dumps(data_dict, separators=(',', ':'))
            print('notifying subscribers: {}'.format(sock_data))
            await websocket.send(sock_data)


# async def update_subscribers(websocket, path):
#     # foreach subscription in subscriptions, send live data
#     global subscriptions


# async def handle_history(websocket, path, element):
#     # send data as json object
#     global data
#     global subscriptions


# def handle_subscribe(element):
#     # add subscription to subscriptions
#     global subscriptions


# def handle_unsubscribe(element):
#     # remove subscription from subscriptions
#     global subscriptions

start_server = websockets.serve(receive_messages, 'localhost', 2009)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.ensure_future(generateData())
asyncio.get_event_loop().run_forever()


# if __name__ == '__main__':
#     # probably read serial data here
#     loop = asyncio.get_event_loop()
#     serial_coroutine = serial_asyncio.create_serial_connection(loop,
#                                                                SerialReader,
#                                                                SERIAL_PORT,
#                                                                SERIAL_BAUDRATE)

#     start_server = websockets.serve(receive_messages, WEBSOCKET['host'],
#                                     WEBSOCKET['port'])
#     loop.run_until_complete(start_server)
#     asyncio.ensure_future(serial_coroutine)
#     loop.run_forever()
