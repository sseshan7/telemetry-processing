import serial_asyncio
import asyncio
import websockets
import json
from collections import defaultdict
import time

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



# Configuration

WEBSOCKET = {
    'host': 'localhost',
    'port': 2009
}

SERIAL = {
    'port': '/dev/ttyACM0',
    'baudrate': 9600,
    'timeout': 1, # Seconds
}

#######################

# Global Variables

# Contains all data recorded
histories = defaultdict(list)
# System currently subscribed to
subscriber_id = None


#######################


class SerialReader(asyncio.Protocol):
    def connection_made(self, transport):
        """
        When connection is established, notifies serial
        :param transport: object that abstracts communication with serial
        """
        self.transport = transport
        print('port opened:', transport)
        transport.serial.rts = False
        transport.write(b'Connection Established\n')

    def data_received(self, incoming):
        """
        On receiving data, parses it and writes it to our structure
        :param incoming: Line of data read from serial
        """
        # data = incoming.decode('utf-8')
        # data = float(data.replace('\r\n', ''))
        # histories['pwr.temp'].append({'timestamp': int(time.time() * 1000),
        #                               'value': data})
        raw_data = [float(i) for i in incoming.split()]
        pkg = {
        'accel': (raw_data[0], raw_data[1], raw_data[2]),
        'gyro': (raw_data[3], raw_data[4], raw_data[5]),
        'mag': (raw_data[6], raw_data[7], raw_data[8])
        }
        print('received:', incoming)

    def connection_lost(self, exc):
        """
        Closes loop when connection is lost
        :param exc: (optional) exception to be thrown
        """
        print('connection lost')
        self.transport.loop.stop()


async def receive_messages(websocket, path):
    """
    Handles recieving msgs from the js browser client
    :param websocket: the websocket being read from and written to
    :param path: (optional) url path
    """
    global subscriber_id
    still_reading = True
    count = 1
    while still_reading:
        print('waiting for message {}'.format(count))
        count += 1
        # Messages are received as text frames
        message = await websocket.recv()
        print('incoming: {}'.format(message))
        message = message.split()
        if message[0] == "history":
            craft_system = message[1]
            hist_dict = {'type': 'history',
                         'id': craft_system,
                         'value': histories[craft_system]}
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


async def notify_subscribers(websocket, sub_id):
    """
    Sends most recent sensor readings to client
    :param websocket: the socket to write to
    :param sub_id: the subscribed system id
    """
    if sub_id is None:
        print('subscriber_id is NONE!!!!')
    else:
        while True:
            await asyncio.sleep(1)
            data_dict = {'type': 'data', 'id': sub_id,
                         'value': histories[sub_id][-1]}
            sock_data = json.dumps(data_dict, separators=(',', ':'))
            print('notifying subscribers: {}'.format(sock_data))
            await websocket.send(sock_data)


if __name__ == "__main__":
    start_server = websockets.serve(receive_messages,
                                    WEBSOCKET['host'],
                                    WEBSOCKET['port'])
    loop = asyncio.get_event_loop()
    serial_coroutine = serial_asyncio.create_serial_connection(loop,
                                                               SerialReader,
                                                               SERIAL['port'],
                                                               SERIAL['baudrate'])
    loop.run_until_complete(start_server)
    asyncio.ensure_future(serial_coroutine)
    asyncio.get_event_loop().run_forever()
