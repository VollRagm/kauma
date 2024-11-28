import base64
import random

def base64_to_int16(base64_str, byteorder='little'):
    return int.from_bytes(base64.b64decode(base64_str), byteorder=byteorder)

def int16_to_base64(int16, byteorder='little'):
    return base64.b64encode(int16.to_bytes(16, byteorder=byteorder)).decode("utf-8")

def base64_to_buffer(base64_str):
    return base64.b64decode(base64_str)

def buffer_to_base64(buffer):
    return base64.b64encode(buffer).decode("utf-8")

def xor_buf(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

# Slices a buffer into 16 byte block array
def slice_blocks_16(buffer):
    blocks = []
    for i in range(0, len(buffer), 16):
        blocks.append(buffer[i:i+16])
    return blocks

# Merges 16 byte block array into a buffer
def merge_blocks_16(blocks):
    buffer = bytearray()
    for block in blocks:
        buffer += block
    return buffer

def pad_block_16(block, padding = 0):
    return block + bytes([padding] * (16 - len(block)))

def pad_bytes_16(data):
    if len(data) == 0:
        return data
    else:
        return data + bytes((16 - len(data) % 16) % 16)
    
def random_bytes(length):
    return bytes([random.randint(0, 255) for _ in range(length)])