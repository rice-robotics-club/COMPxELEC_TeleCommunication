import serial
import RPi.GPIO as GPIO

PORT = '/dev/ttyUSB0'
BAUD = 57600
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

ser = serial.Serial(PORT, BAUD, timeout=1)
print(f"Listening on {PORT}")
while True:
    line = ser.readline().decode(errors='ignore').strip()
    if line == "sigmaballs":
        print("Received:", line)
        GPIO.output(17, GPIO.HIGH)
    else:
        GPIO.output(17, GPIO.LOW)