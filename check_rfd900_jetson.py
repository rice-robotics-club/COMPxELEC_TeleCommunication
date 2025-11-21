#!/usr/bin/env python3
"""
RFD-900x Modem Detection and Diagnostic Tool for Jetson Nano
Run this script on the Jetson to find and test your RFD-900x modem.
"""

import serial
import serial.tools.list_ports
import time
import sys

def list_all_serial_ports():
    """List all available serial ports."""
    print("=" * 60)
    print("Available Serial Ports:")
    print("=" * 60)

    ports = serial.tools.list_ports.comports()

    if not ports:
        print("No serial ports found!")
        return []

    port_list = []
    for port in ports:
        print(f"\nPort: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Hardware ID: {port.hwid}")

        # Check if it might be RFD900
        if 'USB' in port.device or 'ACM' in port.device:
            print(f"  --> Likely USB device (could be RFD-900x)")
            port_list.append(port.device)

    print("\n" + "=" * 60)
    return port_list

def test_serial_port(port, baud_rate=57600):
    """Test if a serial port can be opened and basic communication works."""
    print(f"\nTesting {port} at {baud_rate} baud...")

    try:
        ser = serial.Serial(port, baud_rate, timeout=2)
        print(f"  ✓ Successfully opened {port}")

        # Wait a moment for connection to stabilize
        time.sleep(0.5)

        # Try to send AT command to RFD900
        print("  Testing AT command...")
        ser.write(b'+++')  # Enter command mode
        time.sleep(1.5)  # RFD900 requires 1 second guard time

        ser.write(b'ATI\r\n')  # Request modem info
        time.sleep(0.5)

        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            print(f"  ✓ Modem responded:")
            print("  " + "-" * 56)
            for line in response.strip().split('\n'):
                print(f"    {line}")
            print("  " + "-" * 56)

            if 'RFD' in response or 'SiK' in response:
                print(f"  ✓✓ CONFIRMED: This appears to be an RFD-900x modem!")
                ser.close()
                return True
        else:
            print("  ⚠ No response to AT command (may still be RFD-900x in data mode)")

        ser.close()
        print(f"  ✓ Port {port} is functional")
        return True

    except serial.SerialException as e:
        print(f"  ✗ Error opening {port}: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return False

def check_permissions(port):
    """Check if user has permissions to access the serial port."""
    print(f"\nChecking permissions for {port}...")

    import os
    import stat

    try:
        st = os.stat(port)
        mode = st.st_mode

        print(f"  Current permissions: {stat.filemode(mode)}")

        # Check if user is in dialout group
        import grp
        try:
            dialout_group = grp.getgrnam('dialout')
            user_groups = os.getgroups()

            if dialout_group.gr_gid in user_groups:
                print(f"  ✓ User is in 'dialout' group")
            else:
                print(f"  ✗ User is NOT in 'dialout' group")
                print(f"  Fix: sudo usermod -a -G dialout $USER")
                print(f"       (then log out and back in)")
        except KeyError:
            print(f"  ⚠ 'dialout' group not found on system")

        # Check if port is world-writable
        if mode & stat.S_IWOTH:
            print(f"  ✓ Port is world-writable")
        else:
            print(f"  ⚠ Port requires group or user permissions")
            print(f"  Quick fix: sudo chmod 666 {port}")

    except FileNotFoundError:
        print(f"  ✗ Port {port} does not exist")
    except Exception as e:
        print(f"  ⚠ Could not check permissions: {e}")

def interactive_test(port):
    """Interactive test mode to send/receive data."""
    print("\n" + "=" * 60)
    print(f"Interactive Test Mode - {port}")
    print("=" * 60)
    print("Type messages to send. Press Ctrl+C to exit.")
    print("-" * 60)

    try:
        ser = serial.Serial(port, 57600, timeout=1)

        # Start a simple read loop
        print("\nListening for incoming data...")
        print("(If you have the laptop sender running, you should see packets)\n")

        start_time = time.time()
        bytes_received = 0

        while True:
            # Check for incoming data
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                bytes_received += len(data)

                # Display as hex
                hex_str = ' '.join([f'{b:02x}' for b in data])
                print(f"[RX {len(data):3d} bytes] {hex_str}")

                # Try to display as text if printable
                try:
                    text = data.decode('utf-8', errors='ignore')
                    if text.isprintable() or '\n' in text or '\r' in text:
                        print(f"           Text: '{text.strip()}'")
                except:
                    pass

            # Check for user input (non-blocking would be better, but keeping it simple)
            time.sleep(0.1)

            # Show statistics every 10 seconds
            if time.time() - start_time >= 10 and bytes_received > 0:
                print(f"\n[Stats] Received {bytes_received} bytes in {time.time()-start_time:.1f}s")
                start_time = time.time()
                bytes_received = 0

    except KeyboardInterrupt:
        print("\n\nInteractive test stopped.")
        ser.close()
    except Exception as e:
        print(f"\nError: {e}")

def main():
    print("=" * 60)
    print("RFD-900x Modem Detector for Jetson Nano")
    print("=" * 60)

    # Step 1: List all ports
    available_ports = list_all_serial_ports()

    if not available_ports:
        print("\n⚠ No USB serial devices found!")
        print("\nTroubleshooting:")
        print("1. Ensure RFD-900x modem is plugged into USB port")
        print("2. Check if device is detected: lsusb")
        print("3. Check kernel messages: dmesg | grep tty")
        print("4. Try a different USB port or cable")
        return

    # Step 2: Test each likely port
    print("\n" + "=" * 60)
    print("Testing Detected Ports:")
    print("=" * 60)

    working_ports = []
    for port in available_ports:
        check_permissions(port)
        if test_serial_port(port):
            working_ports.append(port)

    # Step 3: Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    if working_ports:
        print(f"✓ Found {len(working_ports)} working serial port(s):")
        for port in working_ports:
            print(f"  - {port}")

        print("\nRecommended port for RFD-900x: " + working_ports[0])
        print(f"\nUpdate your scripts to use: '{working_ports[0]}'")

        # Offer interactive test
        print("\n" + "=" * 60)
        response = input(f"\nWould you like to test {working_ports[0]} interactively? (y/n): ")
        if response.lower() == 'y':
            interactive_test(working_ports[0])
    else:
        print("✗ No working serial ports found")
        print("\nCommon issues:")
        print("1. Permission denied: Run 'sudo chmod 666 /dev/ttyUSB0'")
        print("2. Not in dialout group: Run 'sudo usermod -a -G dialout $USER'")
        print("3. Device not connected: Check USB connection")
        print("4. Wrong driver: Check 'dmesg | tail' for errors")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
