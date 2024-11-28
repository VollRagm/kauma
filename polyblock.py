import base64

import helper
from gf.primitives import gcm_convert128

def xex_poly2block(coefficients):
    zero_block = 0

    for index in coefficients:
        zero_block |= (1 << index)

    return zero_block

def xex_block2poly(block):
    coefficients = []

    for index in range(128):
        if block & (1 << index):
            coefficients.append(index)
    
    return coefficients

def gcm_poly2block(coefficients):
    xex_value = xex_poly2block(coefficients)
    return gcm_convert128(xex_value)

def reverse_bits(byte):
    reversed_byte = 0
    for i in range(8):
        if (byte >> i) & 1:
            reversed_byte |= 1 << (7 - i)   # GCM semantic function
    return reversed_byte

def gcm_block2poly(block):
    coefficients = []

    for i in range(16):
        byte = (block >> (i * 8)) & 0xFF  # Extract one byte
        for j in range(8):
            if byte & (1 << j):  # check if bit is set for a coeffiecient

                exponent = 8 * i + 7 - j    # remap to gcm mapping
                coefficients.append(exponent)

    coefficients.sort()
    return coefficients


def exec_poly2block(assignment):

    arguments = assignment["arguments"]
    semantic = arguments["semantic"]
    coefficients = arguments["coefficients"]

    if semantic == "xex":

        zero_block_bytes = xex_poly2block(coefficients).to_bytes(16, byteorder='little')
        return {"block": base64.b64encode(zero_block_bytes).decode("utf-8")}
    
    if semantic == "gcm":
            
        zero_block_bytes = gcm_poly2block(coefficients).to_bytes(16, byteorder='little')
        return {"block": base64.b64encode(zero_block_bytes).decode("utf-8")}
    

def exec_block2poly(assignment):

    arguments = assignment["arguments"]
    block = arguments["block"]
    semantic = arguments["semantic"]
    
    block_int = helper.base64_to_int16(block)


    if semantic == "xex":
        return {"coefficients": xex_block2poly(block_int)}
    elif semantic == "gcm":
        return {"coefficients": gcm_block2poly(block_int)}



