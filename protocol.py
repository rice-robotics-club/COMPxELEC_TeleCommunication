import struct 
import crcmod

# This is the unique key to start off the packet. 
START_OF_FRAME = b'\x1A\xCF'

crc16_func = crcmod.predefined.mkCrcFun('kermit')


# Define the structure formats for packing and unpacking using Python's struct module.
# '>' denotes big-endian (network) byte order.
# B = unsigned char (1 byte)
# H = unsigned short (2 bytes)
# 3 bytes in total
HEADER_FORMAT = '>BHB' # Packet Type, Sequence Number, Payload Length
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
SOF_SIZE = len(START_OF_FRAME)
CRC_SIZE = 2 # CRC-16 is 2 bytes


def pack(packet_type: int, sequence_number: int, payload: bytes) -> bytes:
    """
    Packs data into a packet with a standardized header and footer.
    
    Args:
        packet_type: An integer ID (0-255) for the packet.
        sequence_number: An integer sequence number (0-65535).
        payload: The byte payload to be sent (0-255 bytes).
        
    Returns:
        A byte array representing the full, ready-to-transmit packet.
        Returns None if the payload is too large.
    """
    if len(payload) > 255:
        print(f"Error: Payload size {len(payload)} is greater than the maximum of 255 bytes.")
        return None

    # Pack the header fields.
    payload_length = len(payload)
    header = struct.pack(HEADER_FORMAT, packet_type, sequence_number, payload_length)

    # Combine header and payload to calculate checksum.
    data_to_checksum = header + payload
    
    # Calculate the CRC-16 checksum.
    checksum = crc16_func(data_to_checksum)
    
    # Pack the checksum into 2 bytes (big-endian).
    packed_checksum = struct.pack('>H', checksum)

    # Construct the final packet.
    full_packet = START_OF_FRAME + data_to_checksum + packed_checksum

    return full_packet


def unpack(buffer: bytes) -> (dict, int):
    """
    Unpacks a packet from a byte buffer.
    
    Args:
        buffer: A byte array received from a communication channel.
        
    Returns:
        A tuple containing:
        1. A dictionary with the unpacked data ('type', 'seq', 'payload') if successful, otherwise None.
        
        
        2. An integer representing the total number of bytes consumed from the buffer.
        s
        
        Returns (None, 0) if the buffer is incomplete or corrupted.
    """
    # 1. Search for the Start of Frame to begin parsing.
    sof_index = buffer.find(START_OF_FRAME)
    if sof_index == -1:
        # No SOF found, the buffer does not contain a valid packet start.
        return None, 0 # Consume 0 bytes, no packet found

    # Adjust buffer to start at the SOF
    buffer = buffer[sof_index:]
    
    # 2. Check if the buffer is long enough for a minimal packet (header + CRC, 0-len payload)
    if len(buffer) < SOF_SIZE + HEADER_SIZE + CRC_SIZE:
        # Not enough data for a full header and CRC yet.
        return None, sof_index # Consume bytes up to the potential SOF

    # 3. Unpack the header to find the payload length.
    header_start = SOF_SIZE
    header_end = SOF_SIZE + HEADER_SIZE
    packet_type, sequence_number, payload_length = struct.unpack(HEADER_FORMAT, buffer[header_start:header_end]) # >BHB
    
    # 4. Check if the buffer contains the full declared packet.
    expected_packet_size = SOF_SIZE + HEADER_SIZE + payload_length + CRC_SIZE # note that payload length is variable extracted. 
    if len(buffer) < expected_packet_size:
        # The full packet has not arrived yet.
        return None, sof_index # Consume bytes up to the potential SOF

    # 5. Extract the data and checksum from the buffer.
    payload_start = header_end
    payload_end = payload_start + payload_length
    payload = buffer[payload_start:payload_end]

    checksum_start = payload_end
    checksum_end = checksum_start + CRC_SIZE
    received_checksum, = struct.unpack('>H', buffer[checksum_start:checksum_end])

    # 6. Verify the checksum.
    data_to_checksum = buffer[header_start:payload_end] # This is header + payload
    calculated_checksum = crc16_func(data_to_checksum)
    
    if received_checksum == calculated_checksum:
        # Checksum is valid, Packet is good.
        unpacked_data = {
            'type': packet_type,
            'seq': sequence_number,
            'payload': payload
        }
        # Return the data and the total number of bytes this packet occupied.
        return unpacked_data, expected_packet_size + sof_index
    else:
        # Checksum failed. The data is corrupt.
        # We consume up to the end of this corrupted packet to look for the next one.
        print(f"Checksum mismatch! Received: {received_checksum}, Calculated: {calculated_checksum}")
        return None, expected_packet_size + sof_index
