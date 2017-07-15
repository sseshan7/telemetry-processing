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
# -- send structure of spaceship json object
#
# - history:
# -- send history of values for item as json object

### Configure Stuff ###
WEBSOCKET = {
    'host': 'localhost',
    'port': 2009
}

SERIAL_PORT = '/dev/ttyACM0'
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = 1  # Seconds
#######################

### Global Variables ###
# subscriptions = set()  # if we have a finite number, should be a dict
histories = defaultdict(list)  # might end up being a dict of pandas dataframes or something
subscriber_id = None


class SerialReader(asyncio.Protocol):
    def connection_made(self, transport):
        """
        when connection is established, writes a test message to serial
        :param transport:
        """
        self.transport = transport
        print('port opened:', transport)
        transport.serial.rts = False
        transport.write(b'hello world\n')

    def data_received(self, incoming):
        """
        On recieving data, parses it and writes it to our structure
        :param incoming:
        """
        # temporary
        data = incoming.decode('utf-8')
        data = float(data.replace('\r\n', ''))
        histories['pwr.temp'].append({'timestamp': int(time.time() * 1000), 'value': data})
        print('received:', incoming)

    def connection_lost(self, exc):
        """
        Closes loop when connection is lost
        :param exc:
        """
        print('connection lost')
        self.transport.loop.stop()


async def receive_messages(websocket, path):
    """
    Handles recieving msgs from the js browser client
    :param websocket: the websocket being read from and written to
    :param path:
    """
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
    """
    Generates test data
    """
    while True:
        await asyncio.sleep(1)
        t = int(time.time() * 1000)
        var = {'timestamp': t, 'value': math.sin(t)}
        histories['pwr.temp'].append(var)

async def notify_subscribers(websocket, sub_id):
    if sub_id is None:
        print('subscriber_id is NONE!!!!')
    else:
        while True:
            await asyncio.sleep(1)
            data_dict = data_dict = {'type': 'data', 'id': sub_id, 'value': histories[sub_id][-1]}
            sock_data = json.dumps(data_dict, separators=(',', ':'))
            print('notifying subscribers: {}'.format(sock_data))
            await websocket.send(sock_data)

def package_data(raw_data):
    """
    Parses, packages, and organizes serial data
    :param raw_data: raw string read from serial
    :return a dict (str -> triple[str]) of json payloads keyed by sensor (should
     probably be keyed by id so its cleaner to store)
    """
    readings = [float(i) for i in raw_data.split()]
    jsons = []
    for reading in readings:
        timestamp = int(time.time())
        payload = {'timestamp': timestamp, 'value': reading}
        jsons.append(json.dumps(payload, separators=(',', ':')))
    return {
        'accel': (jsons[0], jsons[1], jsons[2]),  # ax, ay, az
        'gyro': (jsons[3], jsons[4], jsons[5]),  # gx, gy, gz
        'mag': (jsons[6], jsons[7], jsons[8])  # mx, my, mz
    }


start_server = websockets.serve(receive_messages,
                                WEBSOCKET['host'],
                                WEBSOCKET['port'])
loop = asyncio.get_event_loop()
serial_coroutine = serial_asyncio.create_serial_connection(loop, SerialReader,
                                                           SERIAL_PORT,
                                                           SERIAL_BAUDRATE)
loop.run_until_complete(start_server)
#asyncio.ensure_future(generateData())
asyncio.ensure_future(serial_coroutine)
asyncio.get_event_loop().run_forever()
