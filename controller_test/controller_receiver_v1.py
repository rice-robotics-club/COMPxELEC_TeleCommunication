import serial
import time
import Jetson.GPIO as GPIO


PORT = '/dev/ttyUSB0'
BAUD = 57600

GPIO.setmode(GPIO.BOARD)

ser = serial.Serial(PORT, BAUD, timeout=1)
print(f"Listening on {PORT} at {BAUD} baud for controller data...\n")

while True:
    if ser.in_waiting > 0: # Checks that something actually arrived before trying to read it.
        data = ser.readline().decode('utf-8', errors='ignore').strip()
        if not data:
            continue

        parts = data.split(',')
        if len(parts) != 12: # Helps to prevent information that doens't contain 12 inputs from being read
            continue

        # Convert
        # Unpack all controller inputs
        left_x, left_y, right_x, right_y, l1, r1, l2, r2, cross, circle, square, triangle = parts

        # Convert analogs to floats and buttons to ints
        left_x = float(left_x)
        left_y = float(left_y)
        right_x = float(right_x)
        right_y = float(right_y)
        l1 = float(l1)
        r1 = float(r1)
        l2 = float(l2)
        r2 = float(r2)
        cross = float(cross)
        circle = float(circle)
        square = float(square)
        triangle = float(triangle)
        
        # Example robot control logic:
        #if cross:  # Cross button pressed
            #print("→ Start motors")
        #if circle:  # Circle button pressed
            #print("→ Stop motors")

        print(
        f"Received: "
        f"L-stick({left_x:.2f},{left_y:.2f}) | "
        f"R-stick({right_x:.2f},{right_y:.2f}) | "
        f"L1:{l1} R1:{r1} L2:{l2:.2f} R2:{r2:.2f} | "
        f"X:{cross} O:{circle} □:{square} △:{triangle}"
        )

        if square == 1:
            GPIO.output(26, GPIO.HIGH)
        else:
            GPIO.output(26, GPIO.LOW)

        if triangle == 1:
            GPIO.output(19, GPIO.HIGH)
        else:
            GPIO.output(19, GPIO.LOW)

        if circle == 1:
            GPIO.output(13, GPIO.HIGH)
        else:
            GPIO.output(13, GPIO.LOW)

        if cross == 1:
            GPIO.output(6, GPIO.HIGH)
        else:
            GPIO.output(6, GPIO.LOW)

        if l1 == 1:
            GPIO.output(5, GPIO.HIGH)
        else:
            GPIO.output(5, GPIO.LOW)