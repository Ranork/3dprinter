import serial
import time
import os

arduino = serial.Serial('/dev/ttyUSB0', 115200, timeout=.1)
arduino.flushInput()

time.sleep(1)


print("-- PID: " + str(os.getpid()))

z = True

while z:
    ser_bytes = arduino.readline()
    decoded_bytes = ser_bytes[0:len(ser_bytes) - 2].decode("utf-8", errors='replace')
    print(decoded_bytes)
    time.sleep(3)