# How to Check for RFD-900x on Jetson Nano

Quick reference guide for detecting and verifying your RFD-900x modem on Jetson.

---

## 🚀 Quick Method: Use the Diagnostic Script

**Easiest way - automated checking:**

```bash
# Copy the script to Jetson
scp check_rfd900_jetson.py <username>@<jetson-ip>:~/

# Run on Jetson
cd ~
python3 check_rfd900_jetson.py
```

This script will:
- ✅ List all serial ports
- ✅ Test each port
- ✅ Try to communicate with RFD-900x using AT commands
- ✅ Check permissions
- ✅ Recommend the correct port to use

---

## 🔍 Manual Command-Line Checks

If you prefer to check manually, here are the commands:

### 1. Check if USB Device is Detected

```bash
# List all USB devices
lsusb
```

Look for entries like:
- `FTDI` (RFD-900x uses FTDI USB-to-serial chip)
- `Future Technology Devices International`

**Example output:**
```
Bus 001 Device 004: ID 0403:6001 Future Technology Devices International, Ltd FT232 Serial (UART) IC
```

### 2. Check for Serial Port

```bash
# List all USB serial devices
ls -l /dev/ttyUSB*
ls -l /dev/ttyACM*
```

**Expected output:**
```
crw-rw---- 1 root dialout 188, 0 Nov 21 10:30 /dev/ttyUSB0
```

If you see this, your RFD-900x is likely on `/dev/ttyUSB0`.

### 3. Check Recent Kernel Messages

```bash
# See what device was detected when you plugged it in
dmesg | grep -i tty
```

**Look for output like:**
```
[12345.678] usb 1-2: FTDI USB Serial Device converter now attached to ttyUSB0
```

Or:
```bash
# Check last 20 kernel messages
dmesg | tail -20
```

### 4. Check Detailed USB Device Info

```bash
# Get detailed info about USB serial devices
udevadm info -a -n /dev/ttyUSB0 | grep -i ftdi
```

### 5. Check Permissions

```bash
# Check who can access the port
ls -l /dev/ttyUSB0
```

**Output:**
```
crw-rw---- 1 root dialout 188, 0 Nov 21 10:30 /dev/ttyUSB0
```

This means:
- Owner: `root` (read/write)
- Group: `dialout` (read/write)
- Others: (no access)

**Check if you're in the dialout group:**
```bash
groups
```

If `dialout` is NOT in the list:
```bash
# Add yourself to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in for this to take effect
# Or reboot: sudo reboot
```

### 6. Grant Temporary Access (Quick Fix)

```bash
# Give everyone read/write access (temporary until reboot)
sudo chmod 666 /dev/ttyUSB0
```

### 7. Test Serial Communication

```bash
# Install screen if not present
sudo apt-get install screen

# Connect to the modem
screen /dev/ttyUSB0 57600
```

Once connected, try AT commands:
1. Type: `+++` (wait 1 second)
2. Type: `ATI` and press Enter

**Expected response:**
```
RFD SiK 2.6 on HM-TRP
```

To exit screen: Press `Ctrl+A` then `K` then `Y`

### 8. Check if Port is Already in Use

```bash
# See if another process is using the port
sudo lsof /dev/ttyUSB0
```

If a process is using it, you'll see:
```
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python3  1234 user    3u   CHR  188,0      0t0  456 /dev/ttyUSB0
```

Kill that process:
```bash
sudo kill 1234
```

---

## 🔧 Common Issues and Fixes

### Issue: "No such file or directory" - /dev/ttyUSB0

**Cause:** Device not detected

**Fixes:**
```bash
# 1. Check if USB is detected at all
lsusb

# 2. Try different USB port
# Unplug and replug the modem

# 3. Check kernel messages for errors
dmesg | tail -30

# 4. Check if driver is loaded
lsmod | grep ftdi
```

### Issue: "Permission denied"

**Cause:** Don't have access to serial port

**Fixes:**
```bash
# Quick temporary fix:
sudo chmod 666 /dev/ttyUSB0

# Permanent fix:
sudo usermod -a -G dialout $USER
# Then log out and back in
```

### Issue: Device appears as /dev/ttyACM0 instead of /dev/ttyUSB0

**Not a problem!** Some RFD-900x modems appear as ACM devices. Just use `/dev/ttyACM0` in your scripts.

```bash
# Update the receiver script:
SERIAL_PORT = '/dev/ttyACM0'  # Instead of ttyUSB0
```

### Issue: Multiple /dev/ttyUSB* devices

```bash
# List all and check which is RFD-900x
for port in /dev/ttyUSB*; do
    echo "Testing $port..."
    python3 -c "import serial; s=serial.Serial('$port', 57600, timeout=1); print('OK')" 2>/dev/null && echo "  -> $port works"
done
```

---

## 📋 Quick Checklist

Run these commands in order:

```bash
# 1. Is device connected?
lsusb | grep -i ftdi

# 2. Does serial port exist?
ls -l /dev/ttyUSB0

# 3. Can I access it?
groups | grep dialout

# 4. If not in dialout group:
sudo usermod -a -G dialout $USER

# 5. Quick permission fix (temporary):
sudo chmod 666 /dev/ttyUSB0

# 6. Test it:
python3 check_rfd900_jetson.py
```

---

## 🎯 What Port Should I Use?

**Most common:** `/dev/ttyUSB0`

**Alternative:** `/dev/ttyACM0`

**To find out for sure:**

```bash
# Method 1: Unplug modem, run this, then plug it back in
watch -n 1 ls /dev/tty*
# Watch for new device to appear

# Method 2: Check dmesg right after plugging in
dmesg | tail
# Look for "attached to ttyUSBX" message

# Method 3: Use our script
python3 check_rfd900_jetson.py
```

---

## 🧪 Testing the Connection

Once you know the port, test it:

```bash
# Simple echo test
echo "test" > /dev/ttyUSB0

# Listen for incoming data
cat /dev/ttyUSB0

# Or use the receiver script
python3 jetson_protocol_receiver.py
```

---

## 📝 Update Your Scripts

Once you've confirmed the port (e.g., `/dev/ttyUSB0`), update this line in **jetson_protocol_receiver.py**:

```python
SERIAL_PORT = '/dev/ttyUSB0'  # Change to YOUR port
```

---

## 🆘 Still Not Working?

If nothing works, check:

1. **USB cable:** Try a different cable (some are power-only)
2. **USB port:** Try a different USB port on Jetson
3. **Power:** Ensure Jetson has enough power (use barrel jack, not just USB)
4. **Modem:** Test modem on laptop first to confirm it works
5. **Firmware:** Ensure RFD-900x has correct firmware

**Get help:**
```bash
# Collect diagnostic info
echo "=== USB Devices ===" > diagnostic.txt
lsusb >> diagnostic.txt
echo -e "\n=== Serial Ports ===" >> diagnostic.txt
ls -l /dev/tty{USB,ACM}* >> diagnostic.txt 2>&1
echo -e "\n=== Recent Messages ===" >> diagnostic.txt
dmesg | tail -50 >> diagnostic.txt
echo -e "\n=== Groups ===" >> diagnostic.txt
groups >> diagnostic.txt

# View the file
cat diagnostic.txt
```

Share this output when asking for help!

---

## ✅ Success Indicators

You know it's working when:

1. ✅ `/dev/ttyUSB0` (or ttyACM0) exists
2. ✅ `ls -l /dev/ttyUSB0` shows you can access it
3. ✅ `python3 check_rfd900_jetson.py` detects it
4. ✅ Running `jetson_protocol_receiver.py` shows "Connected to /dev/ttyUSB0"
5. ✅ When laptop sends packets, Jetson receives them

---

**Quick Start Command:**
```bash
python3 check_rfd900_jetson.py
```

This will check everything automatically! 🚀
