import serial
import time
from pynput import keyboard
import threading

# --- Config ---
PORT = "COM8"
BAUD = 57600
INACTIVITY_RESET = 0.2  # Reset message to "0" if no key press for X seconds

# --- Globals ---
# these variables have to be globals so that both threads can access them!
message = "0"
last_keypress_time = time.time()

# --- Keyboard listener callback ---
# these are the instructions that the keyboard listener
# loop (at the last two lines of this code) will execute whenever
# a key is pressed
def on_press(key):
    global message, last_keypress_time
    try:
        if key.char == 'w':
            message = "sigmaballs"
            print(f"'w' pressed. message = {message}")
            last_keypress_time = time.time()
    except AttributeError:
        pass  # Ignore special keys

# --- Message sending loop ---
# this is the loop that will be soon used to make a separate thread from
# the main that will run in the background
def send_loop():
    global message
    try:
        with serial.Serial(PORT, BAUD, timeout=1) as ser:
            print(f"Opened serial port {PORT} at {BAUD} baud.")
            while True:
                # Reset message to "0" if timeout passed
                if time.time() - last_keypress_time > INACTIVITY_RESET:
                    message = "no sigma balls"

                ser.write((message + "\n").encode())
                print("Sent:", message)
                time.sleep(0.5)
    except Exception as e:
        print("Serial error:", e)

# --- Start serial send loop in a separate thread ---
# this sets up the send loop to run in the background on a separate thread
# daemeon = True means that this thread will end when the main
# program is killed (we want this)
sender_thread = threading.Thread(target=send_loop, daemon=True)
sender_thread.start()

# --- Start keyboard listener (blocks main thread) ---
# this code is a loop, so it is located at the end of the main thread
# and prevents any following lines in the main thread from being reached.
# In order to also send code, we have to create a new thread
# to run in parallel with this (which happens above)
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()