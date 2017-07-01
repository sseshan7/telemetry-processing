import serial
import asyncio
import websockets
import json



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
'host' : 'localhost',
'port' : 2009
}

SERIAL_PORT = '/dev/tty.usbserial'
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1 # Seconds
#######################
ser = serial.Serial(port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)

subscriptions = set() # if we have a finite number, should be a dict
data = dict() # might end up being a dict of pandas dataframes or something

if __name__ == '__main__':
    # probably read serial data here

    start_server = websockets.serve(recieve_messages, WEBSOCKET['host'], WEBSOCKET['port'])
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.ensure_future(read_serial())
    asyncio.get_event_loop().run_forever()




async def recieve_messages(websocket, path):
    still_reading = True
    while still_reading:
        # Assuming msgs are recieved as text frames, not binary frames
        message = await websocket.recv()
        message = message.split()
        # I'm assuming (maybe wrongly) that msgs are in the form
        # "history (element)" and so on for the other commands
        if message[0] == "history":
            await handle_history(message[1])
        # elif ...

async def read_serial(websocket, path):
    global data
    global ser

    still_reading = True
    # I'm worried this will halt the rest of the program despite being an async coroutine
    while still_reading:
        incoming = (ser.readline()).split()
        acc_data = (incoming[0], incoming[1], incoming[2])
        gyro_data = (incoming[3], incoming[4], incoming[5])
        mag_data = (incoming[6], incoming[7], incoming[8])
        # save this to data in some form

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
