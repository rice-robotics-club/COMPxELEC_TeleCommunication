import serial
import time
import threading
import queue

# --- Config ---
PORT = "COM12"   # Make sure this matches your device
BAUD = 57600

# --- Locks ---
# Used to prevent threads from fighting over resources
send_lock = threading.Lock()
print_lock = threading.Lock()
read_lock = threading.Lock()

# --- Queues ---
# Thread-safe storage for messages
send_queue = queue.Queue()
print_queue = queue.Queue()

# --- Globals ---
try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to {PORT} at {BAUD}")
except Exception as e:
    print(f"Error connecting to serial port: {e}")
    exit()

# --- Message Receiving Loop ---
# Continually checks for incoming data from the radio
def recieve_loop():
    while True:
        try:
            if ser.in_waiting > 0:
                # Read and decode the incoming line
                line = ser.readline().decode(errors='ignore').strip()
                if line:
                    print_queue.put(f"Received: {line}")
        except Exception as e:
            print_queue.put(f"Read error: {e}")
        
        time.sleep(0.01) # Small sleep to save CPU power

# --- Message Sending Loop ---
# Waits for items to appear in the send_queue, then sends them
def send_loop():
    while True:
        message = send_queue.get()  # Blocks here until a message is ready
        
        with send_lock:
            try:
                # Encode and write the message to the serial port
                ser.write((message + "\n").encode())
                print_queue.put(f"Sent: {message}")
            except Exception as e:
                print_queue.put(f"Serial error: {e}")

# --- Console Printing Loop ---
# Handles all printing to ensure text doesn't get jumbled
def print_loop():
    while True:
        printThis = print_queue.get() # Blocks here until text is ready to print
        with print_lock:
            print(printThis)

# --- Start Threads ---
# 1. Thread for sending data
sender_thread = threading.Thread(target=send_loop, daemon=True)
sender_thread.start()

# 2. Thread for receiving data
reciever_thread = threading.Thread(target=recieve_loop, daemon=True)
reciever_thread.start()

# 3. Thread for printing to the screen
print_thread = threading.Thread(target=print_loop, daemon=True)
print_thread.start()

# --- Main Input Loop ---
# This runs in the main thread. It waits for you to type a message and hit Enter.
print("Type a message and press Enter to send. (Ctrl+C to quit)")

try:
    while True:
        # Get user input (this pauses the loop until you hit Enter)
        user_msg = input()
        
        # If the message isn't empty, put it in the queue to be sent
        if user_msg:
            send_queue.put(user_msg)

except KeyboardInterrupt:
    print("\nProgram stopping...")
    ser.close()