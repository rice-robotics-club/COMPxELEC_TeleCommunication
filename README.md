# COMPxELEC_TeleCommunication
Let's gooooo!

Packing and Unpacking notes:
The checksum is using CRC16. https://crccalc.com/?crc=123456789&method=&datatype=ascii&outtype=hex
The checksum is represented as big endian. 
The starting key for every packet is b'\x1A\xCF'. (0x1ACF)
