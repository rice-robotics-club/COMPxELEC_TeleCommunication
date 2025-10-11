import serial

PORT = "COM8"
BAUD = 57600

ser = serial.Serial(PORT, BAUD, timeout=1)
print(f"Listening on {PORT}")

while True:
    line = ser.readline().decode(errors='ignore').strip()
    if line:
        print("Received:", line)