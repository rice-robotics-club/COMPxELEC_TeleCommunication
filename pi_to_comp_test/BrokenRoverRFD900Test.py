import serial
import time
from pynput import keyboard

# Change this to your actual COM port
PORT = "COM8"
BAUD = 57600  # Default for RFD900

print("started")
# Start the keyboard listener

def on_press(key):
    global message
    try:
        if key.char == 'w':
            message = "sigmaballs"
            print(f"'w' pressed. message = {message}")
        else:
            message = "0"
    except AttributeError:
        pass  # Ignore special keys

while True:
    message = "0"
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Opened {PORT}")
    try:
        # The message to send
        ser.write((message + "\n").encode())
        print("Sent:", message)

        # Optional: keep the port open a bit
        time.sleep(0.5)
    except Exception as e:
        print("Error:", e)
    finally:
        ser.close()
        print("Port closed.")
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

