import serial
import asyncio
import websockets


### Configure Stuff ###
WEBSOCKET_ADDRESS = 'ws://localhost:8000' # Change this to whatever

SERIAL_PORT = '/dev/tty.usbserial'
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 1 # Seconds
#######################


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
                await socket.send(data)


if __name__ == "__main__":
    # Socket should close itself after it's done
    asyncio.get_event_loop().run_until_complete(dump_to_socket())
