import serial

def dumpLines():
    ser = serial.Serial('/dev/tty.usbserial', 115200)
    while True:
        print ser.readLine() # this function is blocking

if __name__ == "__main__":
    print("hi")
    dumpLines()
