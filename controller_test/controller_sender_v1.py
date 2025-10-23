import pygame
import serial
import threading
import time

# --- SERIAL SETUP ---
PORT = 'COM3'  # Replace with your RFD900 COM port (e.g. COM4 or /dev/ttyUSB0)
BAUD = 57600
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
print(f"Connected to RFD900 on {PORT} at {BAUD} baud.")

# --- CONTROLLER SETUP ---
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected!")
    exit()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Connected to controller: {joystick.get_name()}")

# --- MAIN LOOP ---
while True:
    pygame.event.pump()

    # Read analog sticks
    left_x = joystick.get_axis(0)
    left_y = -1*joystick.get_axis(1) # This inverts the values so the top is positive and bottom is negative
    right_x = joystick.get_axis(2)
    right_y = -1*joystick.get_axis(3) # Same thing

    # --- SHOULDER BUTTONS ---
    l1 = joystick.get_button(9)
    r1 = joystick.get_button(10)

    # Triggers (L2/R2)
    l2 = joystick.get_axis(4)
    r2 = joystick.get_axis(5)

    # Buttons
    cross = joystick.get_button(0)
    circle = joystick.get_button(1)
    square = joystick.get_button(2)
    triangle = joystick.get_button(3)

    # Pack controller state into a string
    inputs = f"{left_x:.2f},{left_y:.2f},{right_x:.2f},{right_y:.2f},{l1:.2f},{r1:.2f},{l2:.2f},{r2:.2f},{cross},{circle},{square},{triangle}"

    # Send it through serial
    ser.write((inputs + "\n").encode('utf-8'))

    # Print locally too
    print("Sent:", inputs)

    # Small delay to avoid spamming
    time.sleep(0.1) # This value can be changed 