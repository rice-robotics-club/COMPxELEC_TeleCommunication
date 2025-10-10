import serial
import time

# Change this to your actual COM port
PORT = "COM4"
BAUD = 57600  # Default for RFD900

ser = serial.Serial(PORT, BAUD, timeout=1)
print(f"Opened {PORT}")

try:
    # The message to send
    message = "sigma balls"
    ser.write((message + "\n").encode())
    print("Sent:", message)

    # Optional: keep the port open a bit
    time.sleep(0.5)
except Exception as e:
    print("Error:", e)
finally:
    ser.close()
    print("Port closed.")