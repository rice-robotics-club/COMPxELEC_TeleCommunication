"""
Jetson Nano-side Protocol Test Receiver for RFD-900x Modem
Uses the binary packet protocol with CRC-16 checksum validation.

Hardware Setup:
- RFD-900x-US modem connected via USB (/dev/ttyUSB0)
- Run this script on the Nvidia Jetson Nano
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
SERIAL_PORT = '/dev/ttyUSB0'  # RFD900 modem on Jetson
BAUD_RATE = 57600
TIMEOUT = 1

class ProtocolReceiver:
    def __init__(self, port, baud_rate=57600):
        """Initialize serial connection."""
        self.ser = serial.Serial(port, baud_rate, timeout=TIMEOUT)
        self.buffer = b''
        self.packet_count = 0
        self.error_count = 0
        self.last_sequence = None

        print(f"Connected to {port} at {baud_rate} baud")
        print(f"Waiting for packets (SOF: {protocol.START_OF_FRAME.hex()})...")
        print("-" * 60)

    def process_motor_command(self, payload):
        """Process motor command packet (Type 1)."""
        if len(payload) != 8:
            print(f"  ERROR: Expected 8 bytes for motor command, got {len(payload)}")
            return

        left_speed, right_speed = struct.unpack('>ff', payload)
        print(f"  MOTOR COMMAND: Left={left_speed:+.2f}, Right={right_speed:+.2f}")

        # Here you would send commands to your motor controller
        # Example: send to Arduino, control GPIO, etc.

    def process_text_message(self, payload):
        """Process text message packet (Type 2)."""
        try:
            message = payload.decode('utf-8')
            print(f"  TEXT MESSAGE: '{message}'")
        except UnicodeDecodeError:
            print(f"  TEXT MESSAGE: (decode error) Raw: {payload.hex()}")

    def process_sensor_data(self, payload):
        """Process sensor data packet (Type 3)."""
        if len(payload) != 12:
            print(f"  ERROR: Expected 12 bytes for sensor data, got {len(payload)}")
            return

        temperature, humidity, pressure = struct.unpack('>fff', payload)
        print(f"  SENSOR DATA: Temp={temperature:.1f}°C, Humidity={humidity:.1f}%, "
              f"Pressure={pressure:.2f}hPa")

    def process_ping(self, payload):
        """Process ping packet (Type 0)."""
        print(f"  PING received (payload: {len(payload)} bytes)")

    def process_packet(self, packet_data):
        """Process a received packet based on its type."""
        packet_type = packet_data['type']
        sequence = packet_data['seq']
        payload = packet_data['payload']

        self.packet_count += 1

        print(f"\n[PACKET #{self.packet_count}] Type={packet_type}, Seq={sequence}, "
              f"Payload={len(payload)} bytes")

        # Check for missing packets
        if self.last_sequence is not None:
            expected_seq = (self.last_sequence + 1) % 65536
            if sequence != expected_seq:
                missed = (sequence - expected_seq) % 65536
                print(f"  WARNING: Missed {missed} packet(s)! "
                      f"Expected seq={expected_seq}, got seq={sequence}")

        self.last_sequence = sequence

        # Route to appropriate handler based on packet type
        if packet_type == 0:
            self.process_ping(payload)
        elif packet_type == 1:
            self.process_motor_command(payload)
        elif packet_type == 2:
            self.process_text_message(payload)
        elif packet_type == 3:
            self.process_sensor_data(payload)
        else:
            print(f"  UNKNOWN TYPE: {packet_type}")
            print(f"  Raw payload: {payload.hex()}")

    def receive_and_process(self):
        """Continuously receive and process packets."""
        try:
            while True:
                # Read available data from serial port
                if self.ser.in_waiting > 0:
                    new_data = self.ser.read(self.ser.in_waiting)
                    self.buffer += new_data

                # Try to unpack a packet from the buffer
                packet_data, bytes_consumed = protocol.unpack(self.buffer)

                if packet_data is not None:
                    # Successfully unpacked a packet
                    self.process_packet(packet_data)
                    self.buffer = self.buffer[bytes_consumed:]

                elif bytes_consumed > 0:
                    # Consumed some bytes but no valid packet (corrupted data)
                    self.error_count += 1
                    print(f"\n[ERROR #{self.error_count}] Corrupted packet detected, "
                          f"skipping {bytes_consumed} bytes")
                    self.buffer = self.buffer[bytes_consumed:]

                # Small sleep to prevent busy-waiting
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\n\nReceiver stopped by user.")
            self.print_statistics()

        except Exception as e:
            print(f"\nUnexpected error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            self.ser.close()
            print("Serial port closed.")

    def print_statistics(self):
        """Print reception statistics."""
        print("\n" + "=" * 60)
        print("Reception Statistics")
        print("=" * 60)
        print(f"Total packets received: {self.packet_count}")
        print(f"Errors detected: {self.error_count}")
        if self.packet_count > 0:
            success_rate = (self.packet_count / (self.packet_count + self.error_count)) * 100
            print(f"Success rate: {success_rate:.1f}%")
        print("=" * 60)


def main():
    print("=" * 60)
    print("RFD-900x Protocol Receiver Test - JETSON SIDE")
    print("=" * 60)

    try:
        receiver = ProtocolReceiver(SERIAL_PORT, BAUD_RATE)
        receiver.receive_and_process()

    except serial.SerialException as e:
        print(f"\nError: Could not open {SERIAL_PORT}")
        print(f"Details: {e}")
        print("\nTroubleshooting:")
        print("1. Check that RFD-900x modem is connected to Jetson")
        print("2. Verify USB device with: ls -l /dev/ttyUSB*")
        print("3. Check permissions: sudo chmod 666 /dev/ttyUSB0")
        print("4. Add user to dialout group: sudo usermod -a -G dialout $USER")
        print("5. Ensure no other program is using the port")

    except KeyboardInterrupt:
        print("\n\nReceiver interrupted by user.")

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
