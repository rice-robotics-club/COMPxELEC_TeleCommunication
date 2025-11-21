"""
Laptop-side Protocol Test Sender for RFD-900x Modem
Uses the binary packet protocol with CRC-16 checksum validation.

Hardware Setup:
- RFD-900x-US modem connected via USB
- Configure COM port below (check Device Manager)
"""

import serial
import struct
import time
import sys
import os

# Add the parent directory to the path to import protocol
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import protocol

# Configuration
COM_PORT = 'COM8'  # Change to your RFD900 COM port (check Device Manager)
BAUD_RATE = 57600
TIMEOUT = 1

class ProtocolSender:
    def __init__(self, port, baud_rate=57600):
        """Initialize serial connection."""
        self.ser = serial.Serial(port, baud_rate, timeout=TIMEOUT)
        self.sequence_number = 0
        print(f"Connected to {port} at {baud_rate} baud")
        print(f"Start of Frame marker: {protocol.START_OF_FRAME.hex()}")
        print("-" * 60)

    def send_packet(self, packet_type, payload):
        """Pack and send a packet using the protocol."""
        packet = protocol.pack(packet_type, self.sequence_number, payload)

        if packet is None:
            print("Error: Failed to pack packet (payload too large?)")
            return False

        self.ser.write(packet)
        print(f"[SENT] Type: {packet_type}, Seq: {self.sequence_number}, "
              f"Payload: {len(payload)} bytes")
        print(f"       Hex: {packet.hex(' ')}")

        self.sequence_number = (self.sequence_number + 1) % 65536
        return True

    def send_motor_command(self, left_speed, right_speed):
        """Send motor speed command (Type 1 packet)."""
        # Pack two floats as payload (8 bytes total)
        payload = struct.pack('>ff', left_speed, right_speed)
        print(f"\nSending motor command: Left={left_speed:.2f}, Right={right_speed:.2f}")
        return self.send_packet(packet_type=1, payload=payload)

    def send_text_message(self, message):
        """Send a text message (Type 2 packet)."""
        payload = message.encode('utf-8')
        print(f"\nSending text message: '{message}'")
        return self.send_packet(packet_type=2, payload=payload)

    def send_sensor_data(self, temperature, humidity, pressure):
        """Send sensor data (Type 3 packet)."""
        # Pack three floats as payload (12 bytes total)
        payload = struct.pack('>fff', temperature, humidity, pressure)
        print(f"\nSending sensor data: Temp={temperature}°C, Humidity={humidity}%, "
              f"Pressure={pressure}hPa")
        return self.send_packet(packet_type=3, payload=payload)

    def send_ping(self):
        """Send a ping packet (Type 0, empty payload)."""
        print("\nSending ping...")
        return self.send_packet(packet_type=0, payload=b'')

    def run_interactive_test(self):
        """Interactive test menu."""
        print("\n" + "=" * 60)
        print("Interactive Protocol Test Menu")
        print("=" * 60)

        while True:
            print("\nOptions:")
            print("  1 - Send motor command")
            print("  2 - Send text message")
            print("  3 - Send sensor data")
            print("  4 - Send ping")
            print("  5 - Run automated test sequence")
            print("  q - Quit")

            choice = input("\nEnter choice: ").strip().lower()

            if choice == '1':
                try:
                    left = float(input("Enter left motor speed (-1.0 to 1.0): "))
                    right = float(input("Enter right motor speed (-1.0 to 1.0): "))
                    self.send_motor_command(left, right)
                except ValueError:
                    print("Invalid input. Please enter numbers.")

            elif choice == '2':
                message = input("Enter message: ")
                self.send_text_message(message)

            elif choice == '3':
                try:
                    temp = float(input("Enter temperature (°C): "))
                    humid = float(input("Enter humidity (%): "))
                    press = float(input("Enter pressure (hPa): "))
                    self.send_sensor_data(temp, humid, press)
                except ValueError:
                    print("Invalid input. Please enter numbers.")

            elif choice == '4':
                self.send_ping()

            elif choice == '5':
                self.run_automated_test()

            elif choice == 'q':
                print("\nClosing connection...")
                self.ser.close()
                break

            else:
                print("Invalid choice. Try again.")

    def run_automated_test(self):
        """Run a sequence of automated tests."""
        print("\n" + "=" * 60)
        print("Running Automated Test Sequence")
        print("=" * 60)

        tests = [
            ("Ping", lambda: self.send_ping()),
            ("Motor Forward", lambda: self.send_motor_command(0.75, 0.75)),
            ("Motor Turn Left", lambda: self.send_motor_command(0.5, -0.5)),
            ("Motor Backward", lambda: self.send_motor_command(-0.6, -0.6)),
            ("Motor Stop", lambda: self.send_motor_command(0.0, 0.0)),
            ("Text Hello", lambda: self.send_text_message("Hello from Laptop!")),
            ("Text Test", lambda: self.send_text_message("Testing RFD-900x modem")),
            ("Sensor Data", lambda: self.send_sensor_data(25.5, 60.2, 1013.25)),
        ]

        for i, (name, test_func) in enumerate(tests, 1):
            print(f"\n[Test {i}/{len(tests)}] {name}")
            test_func()
            time.sleep(1)  # Wait 1 second between tests

        print("\n" + "=" * 60)
        print("Automated test sequence complete!")
        print("=" * 60)


def main():
    print("=" * 60)
    print("RFD-900x Protocol Sender Test - LAPTOP SIDE")
    print("=" * 60)

    try:
        sender = ProtocolSender(COM_PORT, BAUD_RATE)
        sender.run_interactive_test()

    except serial.SerialException as e:
        print(f"\nError: Could not open {COM_PORT}")
        print(f"Details: {e}")
        print("\nTroubleshooting:")
        print("1. Check that RFD-900x modem is connected")
        print("2. Verify COM port in Device Manager")
        print("3. Update COM_PORT variable in this script")
        print("4. Ensure no other program is using the port")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
