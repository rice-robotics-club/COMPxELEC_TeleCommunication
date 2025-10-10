import serial
import threading

PORT = '/dev/serial0'   # Use UART pins (GPIO14 TX, GPIO15 RX)
BAUD = 57600

def read_from_pc(ser):
    """Continuously read and display incoming commands."""
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            if data:
                print(f"[PC Command] {data}")

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Listening on {PORT} at {BAUD} baud.")
    print("Type messages to send to PC. Ctrl+C to exit.\n")

    # Start thread for reading incoming data
    thread = threading.Thread(target=read_from_pc, args=(ser,), daemon=True)
    thread.start()

    try:
        while True:
            msg = input("You: ")
            ser.write((msg + "\n").encode('utf-8'))
    except KeyboardInterrupt:
        print("\nClosing connection.")
        ser.close()

if __name__ == "__main__":
    main()
