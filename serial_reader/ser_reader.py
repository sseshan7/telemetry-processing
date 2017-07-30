import serial_asyncio
import asyncio
import websockets
import json
from collections import defaultdict
import time
import queue

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
histories = defaultdict(list) # Contains all data recorded
data_buffer = queue.Queue() # Buffer queue to hold the data to be immediately sent over websocket
sockets = [None] # global list that contains socket connections to share among coroutines

subscriber_id = None # ID of the data stream currently subscribed to
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

        sub_id = subscriber_id
        data = incoming.decode('utf-8')
        raw_data = [float(i) for i in data.split()]
        pkg = {'accel': (raw_data[0], raw_data[1], raw_data[2]),
                'gyro': (raw_data[3], raw_data[4], raw_data[5]),
                'mag': (raw_data[6], raw_data[7], raw_data[8])}

        t = int(time.time() * 1000)
        histories['accel.x'].append({'timestamp': t, 'value': pkg['accel'][0]})
        histories['accel.y'].append({'timestamp': t, 'value': pkg['accel'][1]})
        histories['accel.z'].append({'timestamp': t, 'value': pkg['accel'][2]})
        histories['gyro.x'].append({'timestamp': t, 'value': pkg['gyro'][0]})
        histories['gyro.y'].append({'timestamp': t, 'value': pkg['gyro'][1]})
        histories['gyro.z'].append({'timestamp': t, 'value': pkg['gyro'][2]})
        histories['mag.x'].append({'timestamp': t, 'value': pkg['mag'][0]})
        histories['mag.y'].append({'timestamp': t, 'value': pkg['mag'][1]})
        histories['mag.z'].append({'timestamp': t, 'value': pkg['mag'][2]})

        if sub_id is not None:
            data_buffer.put(histories[sub_id][-1])

        print(raw_data)


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
    print("Entered receive messages")
    sockets[0] = websocket
    still_reading = True
    count = 1
    mycount = 0
    while still_reading:
        print("in receive messages loop: {}".format(mycount))
        mycount += 1
        print('waiting for message {}'.format(count))
        count += 1
        # Messages are received as text frames
        message = await websocket.recv()
        print('incoming: {}'.format(message))
        message = message.split()
        if message[0] == 'dictionary':
            data = None
            with open('dictionary.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            sock_data = json.dumps(data, separators=(',', ':'))
            print(sock_data)
            await websocket.send(sock_data)
        elif message[0] == "history" or 'subscribe':
            craft_system = message[1]
            subscriber_id = craft_system
            hist_dict = {'type': 'history',
                         'id': craft_system,
                         'value': histories[craft_system]}
            sock_data = json.dumps(hist_dict, separators=(',', ':'))
            print(sock_data)
            await websocket.send(sock_data)


async def notify_subscribers():
    """
    An asyncio coroutine that sends data to client as it's received from serial device
    :param websocket: the socket to write to
    """

    count = 0
    sub_id = None
    while True:
        try:
            val = data_buffer.get(False) # this call is blocking
            sub_id = subscriber_id
            print("NOTIFYING SUBSCRIBERS: {} count: {}".format(sub_id, count))
            data_dict = {'type': 'data', 'id': sub_id, 'value': val}
            sock_data = json.dumps(data_dict, separators=(',', ':'))
            await sockets[0].send(sock_data)
            count += 1
        except queue.Empty:
            await asyncio.sleep(0.05)


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
    asyncio.ensure_future(notify_subscribers())
    asyncio.ensure_future(serial_coroutine)
    asyncio.get_event_loop().run_forever()
