# RFD-900x Modem Testing Guide
## Encode/Decode Testing Between Laptop and Nvidia Jetson

This guide explains how to test the binary packet protocol with CRC-16 checksum validation between your laptop and Nvidia Jetson using RFD-900x-US modems.

---

## 📋 Table of Contents
1. [Hardware Requirements](#hardware-requirements)
2. [Software Requirements](#software-requirements)
3. [Hardware Setup](#hardware-setup)
4. [Software Installation](#software-installation)
5. [Running the Tests](#running-the-tests)
6. [Understanding the Protocol](#understanding-the-protocol)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Hardware Requirements

### Laptop Side:
- Windows laptop
- RFD-900x-US modem (configured as one endpoint)
- USB cable for RFD-900x

### Jetson Side:
- Nvidia Jetson Nano (or other Jetson model)
- RFD-900x-US modem (configured as paired endpoint)
- USB cable for RFD-900x

### RFD-900x Modem Pairing:
Both modems must be paired and configured to communicate with each other. Default settings should work, but ensure:
- Same frequency band
- Same air data rate (57600 baud recommended)
- Matching network IDs

---

## 💻 Software Requirements

### Both Systems:
- Python 3.7 or higher
- `pyserial` library
- `crcmod` library

### Installation Commands:

**On Laptop (Windows):**
```bash
pip install pyserial crcmod
```

**On Jetson (Linux):**
```bash
pip3 install pyserial crcmod
# or
sudo apt-get install python3-serial python3-crcmod
```

---

## 🔌 Hardware Setup

### 1. Connect RFD-900x Modems

**Laptop Side:**
1. Connect RFD-900x modem to USB port
2. Open Device Manager (Windows Key + X → Device Manager)
3. Find "Ports (COM & LPT)" section
4. Note the COM port number (e.g., COM8, COM4)
5. Update `COM_PORT` variable in `laptop_protocol_sender.py`

**Jetson Side:**
1. Connect RFD-900x modem to USB port
2. Open terminal and check device:
   ```bash
   ls -l /dev/ttyUSB*
   ```
3. Should see `/dev/ttyUSB0` (or similar)
4. Grant permissions:
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   ```
   Or permanently add user to dialout group:
   ```bash
   sudo usermod -a -G dialout $USER
   # Log out and back in for this to take effect
   ```

### 2. Verify Modem Connection

**Test modem communication:**

On either system, you can use a serial terminal to verify the modem responds:
```bash
# Windows: Use PuTTY or similar
# Linux/Jetson:
screen /dev/ttyUSB0 57600
# Press +++ (wait) then type AT and press Enter
# Should respond with "OK"
```

---

## 📦 Software Installation

### 1. Copy Files to Systems

**On Laptop (Windows):**
Files are already in: `c:\Users\roths\Documents\Robotics\COMPxELEC_TeleCommunication\`
- `protocol.py` (core protocol library)
- `laptop_protocol_sender.py` (sender script)

**On Jetson (Linux):**
Transfer these files to Jetson:
```bash
# Option 1: Use SCP from laptop
scp protocol.py jetson_protocol_receiver.py <username>@<jetson-ip>:~/modem_test/

# Option 2: Use USB drive or git clone
# Option 3: Copy-paste file contents over SSH
```

Create directory on Jetson:
```bash
mkdir -p ~/modem_test
cd ~/modem_test
```

### 2. Verify File Structure

**Laptop:**
```
COMPxELEC_TeleCommunication/
├── protocol.py
├── laptop_protocol_sender.py
└── jetson_protocol_receiver.py
```

**Jetson:**
```
~/modem_test/
├── protocol.py
└── jetson_protocol_receiver.py
```

---

## 🚀 Running the Tests

### Step 1: Start the Receiver on Jetson

**On Jetson terminal:**
```bash
cd ~/modem_test
python3 jetson_protocol_receiver.py
```

You should see:
```
============================================================
RFD-900x Protocol Receiver Test - JETSON SIDE
============================================================
Connected to /dev/ttyUSB0 at 57600 baud
Waiting for packets (SOF: 1acf)...
------------------------------------------------------------
```

### Step 2: Start the Sender on Laptop

**On laptop command prompt:**
```cmd
cd C:\Users\roths\Documents\Robotics\COMPxELEC_TeleCommunication
python laptop_protocol_sender.py
```

You should see:
```
============================================================
RFD-900x Protocol Sender Test - LAPTOP SIDE
============================================================
Connected to COM8 at 57600 baud
Start of Frame marker: 1acf
------------------------------------------------------------

============================================================
Interactive Protocol Test Menu
============================================================

Options:
  1 - Send motor command
  2 - Send text message
  3 - Send sensor data
  4 - Send ping
  5 - Run automated test sequence
  q - Quit
```

### Step 3: Run Tests

**Option A: Automated Test Sequence**
1. Press `5` and Enter
2. Watch as 8 test packets are sent automatically
3. Verify reception on Jetson terminal

**Option B: Manual Testing**
1. Press `1` for motor command
   - Enter values like: `0.75` and `0.5`
2. Press `2` for text message
   - Type: `Hello Jetson!`
3. Press `3` for sensor data
   - Enter values like: `25.5`, `60.0`, `1013.25`
4. Press `4` for ping

### Step 4: Verify Results

**On Jetson, you should see output like:**
```
[PACKET #1] Type=0, Seq=0, Payload=0 bytes
  PING received (payload: 0 bytes)

[PACKET #2] Type=1, Seq=1, Payload=8 bytes
  MOTOR COMMAND: Left=+0.75, Right=+0.75

[PACKET #3] Type=2, Seq=2, Payload=18 bytes
  TEXT MESSAGE: 'Hello from Laptop!'

[PACKET #4] Type=3, Seq=3, Payload=12 bytes
  SENSOR DATA: Temp=25.5°C, Humidity=60.2%, Pressure=1013.25hPa
```

---

## 🔍 Understanding the Protocol

### Packet Structure

Every packet follows this binary format:

```
┌─────────────┬──────────┬─────────┬──────────┐
│ START (2B)  │ HEADER   │ PAYLOAD │ CRC (2B) │
│   0x1ACF    │  (4B)    │ (0-255B)│          │
└─────────────┴──────────┴─────────┴──────────┘
```

**Start of Frame (SOF):** `0x1A 0xCF`
- Unique marker to detect packet boundaries
- Allows recovery from corrupted data

**Header (4 bytes):**
- Byte 0: Packet Type (0-255)
- Bytes 1-2: Sequence Number (0-65535, big-endian)
- Byte 3: Payload Length (0-255)

**Payload:** Variable length data (0-255 bytes)

**Checksum:** CRC-16 Kermit (2 bytes, big-endian)
- Calculated over header + payload
- Detects transmission errors

### Packet Types

| Type | Name         | Payload Format                    | Size  |
|------|--------------|-----------------------------------|-------|
| 0    | Ping         | Empty                             | 0 B   |
| 1    | Motor Cmd    | 2 floats (left, right speed)      | 8 B   |
| 2    | Text Message | UTF-8 encoded string              | Var   |
| 3    | Sensor Data  | 3 floats (temp, humid, pressure)  | 12 B  |

### Example Packet (Motor Command)

**Command:** Left=0.75, Right=-0.5

**Binary Packet:**
```
1A CF           - Start of Frame
01              - Packet Type (1 = Motor Command)
00 65           - Sequence Number (101)
08              - Payload Length (8 bytes)
3F 40 00 00     - Left speed (0.75 as float)
BF 00 00 00     - Right speed (-0.5 as float)
D3 B3           - CRC-16 Checksum
```

**Total:** 16 bytes

---

## 🔧 Troubleshooting

### Issue: "Could not open COM port"

**Laptop (Windows):**
1. Check Device Manager for correct COM port
2. Close any other programs using the port (Arduino IDE, PuTTY, etc.)
3. Try unplugging and replugging the modem
4. Update `COM_PORT` variable in script

**Jetson (Linux):**
1. Verify device exists: `ls -l /dev/ttyUSB*`
2. Check permissions: `sudo chmod 666 /dev/ttyUSB0`
3. Add to dialout group: `sudo usermod -a -G dialout $USER`
4. Check for other processes: `sudo lsof /dev/ttyUSB0`

### Issue: "No packets received"

1. **Check modem pairing:**
   - Both modems should have matching LEDs (solid green = connected)
   - Verify air data rate matches (57600)
   - Ensure same network ID

2. **Check baud rate:**
   - Serial baud = 57600 on both scripts
   - Modem air rate configured correctly

3. **Test basic communication:**
   - Use simple text-based test first
   - Try: `echo "test" > COM8` (Windows) or `echo "test" > /dev/ttyUSB0` (Linux)

4. **Check range:**
   - Start with modems close together (< 10 meters)
   - Verify antenna connections

### Issue: "Checksum mismatch" errors

1. **Normal:** A few errors are expected in wireless communication
2. **Excessive errors (>10%):**
   - Check antenna connections
   - Reduce distance between modems
   - Check for interference (Wi-Fi, Bluetooth, other 900MHz devices)
   - Lower air data rate for more reliable transmission

### Issue: "Missing packets" warning

1. Normal in wireless communication (especially at range)
2. Sequence numbers detect gaps automatically
3. To reduce:
   - Improve antenna placement (vertical, clear line of sight)
   - Reduce transmission rate (add delays in sender)
   - Increase modem transmit power (if configurable)

### Issue: ModuleNotFoundError: crcmod

```bash
# Install missing dependency
pip install crcmod        # Windows
pip3 install crcmod       # Linux/Jetson
```

---

## 📊 Expected Results

### Successful Test Output

**Good reception (Jetson side):**
```
[PACKET #1] Type=0, Seq=0, Payload=0 bytes
[PACKET #2] Type=1, Seq=1, Payload=8 bytes
[PACKET #3] Type=2, Seq=2, Payload=18 bytes
...

Reception Statistics
============================================================
Total packets received: 8
Errors detected: 0
Success rate: 100.0%
```

**Acceptable reception (some errors):**
```
[PACKET #1] Type=1, Seq=0, Payload=8 bytes
[ERROR #1] Corrupted packet detected, skipping 16 bytes
[PACKET #2] Type=1, Seq=2, Payload=8 bytes
  WARNING: Missed 1 packet(s)! Expected seq=1, got seq=2
...

Reception Statistics
============================================================
Total packets received: 7
Errors detected: 1
Success rate: 87.5%
```

Success rate > 90% is good for wireless communication.

---

## 🎯 Next Steps

After successful testing:

1. **Integrate into your application:**
   - Import `protocol.py` into your rover control code
   - Use `protocol.pack()` to send commands
   - Use `protocol.unpack()` to receive commands

2. **Add custom packet types:**
   - Define new packet types (e.g., Type 4 = GPS data)
   - Add handler in receiver script
   - Document in this guide

3. **Implement bi-directional communication:**
   - Add sender code to Jetson script
   - Add receiver code to laptop script
   - Send telemetry back from rover

4. **Optimize for your use case:**
   - Adjust packet rate (currently 1 Hz in automated test)
   - Add retry logic for critical commands
   - Implement acknowledgment packets

---

## 📚 Additional Resources

- **RFD-900x Documentation:** https://files.rfdesign.com.au/
- **CRC-16 Calculator:** https://crccalc.com/
- **Python struct format:** https://docs.python.org/3/library/struct.html
- **Protocol Source:** `protocol.py` in this directory

---

## ✅ Quick Reference

**Start Receiver (Jetson):**
```bash
python3 jetson_protocol_receiver.py
```

**Start Sender (Laptop):**
```cmd
python laptop_protocol_sender.py
```

**Run Automated Test:**
- Choose option `5` in sender menu

**Stop Scripts:**
- Press `Ctrl+C` in terminal
- Or choose `q` in sender menu

---

**Created:** 2025
**Protocol Version:** 1.0
**Author:** Based on COMPxELEC_TeleCommunication protocol
