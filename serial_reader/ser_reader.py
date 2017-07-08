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
### Global Variables ###
subscriptions = set()  # if we have a finite number, should be a dict
data = defaultdict(list)  # might end up being a dict of pandas dataframes or
#  something


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
    """
    Generates test data
    """
    while True:
        await asyncio.sleep(1)
        t = int(time.time())
        var = {'timestamp': t, 'value': math.sin(t)}
        # histories['pwr.temp'].append(var)


async def update_subscribers(websocket, path):
    """
    Foreach subscriber in subscriptions, send relevant data
    :param websocket: socket to write to
    :param path:
    """
    global subscriptions


async def handle_history(websocket, path, element):
    """
    Send data as json object
    :param websocket: socket to write to
    :param path:
    :param element:
    """
    global data
    global subscriptions


def handle_subscribe(element):
    """
    Add subscriber to subscriptions
    :param element: element being subscribed to
    """
    global subscriptions


def handle_unsubscribe(element):
    """
    Remove subscriber from subscriptions
    :param element: element being unsubscribed from
    """
    global subscriptions


def parse_serial_data(raw_data):
    """
    Parses and organizes raw serial data
    :param raw_data: the raw string read from serial
    :return: a dict (str -> triple[float]) of sensor values keyed by sensor
    """
    readings = [float(i) for i in raw_data.split()]
    return {
        'accel': (readings[0], readings[1], readings[2]),
        'gyro': (readings[3], readings[4], readings[5]),
        'mag': (readings[6], readings[7], readings[8])
    }

if __name__ == '__main__':
    # probably read serial data here
    loop = asyncio.get_event_loop()
    serial_coroutine = serial_asyncio.create_serial_connection(loop,
                                                               SerialReader,
                                                               SERIAL_PORT,
                                                               SERIAL_BAUDRATE)

    start_server = websockets.serve(receive_messages, WEBSOCKET['host'],
                                    WEBSOCKET['port'])
    loop.run_until_complete(asyncio.gather(
        start_server,
        generateData(),
    ))
    # putting serial_coroutine in the above statement might also work?
    asyncio.ensure_future(serial_coroutine)
    loop.run_forever()


