REDUCT_POLY = 0x100000000000000000000000000000087 # a^128 + a^7 + a^2 + a + 1
REVERSE_BYTE_TABLE = [int(f'{i:08b}'[::-1], 2) for i in range(256)]

def gcm_convert_bytes(value: bytes) -> bytes:
    return bytes([REVERSE_BYTE_TABLE[byte] for byte in value])

def gcm_convert128(value: int) -> int:
    return int.from_bytes(gcm_convert_bytes(value.to_bytes(16, byteorder='little')), byteorder='little')

# Arbitrary length GCM conversion
def gcm_convert(value: int) -> int:
    num_bytes = (value.bit_length() + 7) // 8  # Round up to the nearest byte
    block = value.to_bytes(num_bytes, byteorder='little')
    return int.from_bytes(gcm_convert_bytes(block), byteorder='little')

# Galois field multiplication for 128 bit non-GCM polynomials
def gf128_mul(a: int, b: int) -> int:
    result = 0
    while b:
        if b & 1:
            result ^= a  # Add (XOR) a to result if b's lowest bit is 1
        a <<= 1  # Multiply a by x (shift left)
        if a & (1 << 128):  # If a overflows 128 bits
            a ^= REDUCT_POLY  # Reduce by modulus
        b >>= 1  # Move to the next bit in b
    return result

# Galois field multiplication for 128 bit GCM elements
def gf128_mul_gcm(a: int, b: int) -> int:
    a = gcm_convert(a)
    b = gcm_convert(b)
    result = gf128_mul(a, b)
    return gcm_convert(result)

# Galois field exponentiation for 128 bit GCM elements
def gf128_pow_gcm(base: int, exponent: int) -> int:

    base = gcm_convert(base)
    exponent = gcm_convert(exponent)

    result = 1
    while exponent > 0:
        if exponent & 1:
            result = gf128_mul(result, base)
        base = gf128_mul(base, base)
        exponent >>= 1
    return gcm_convert128(result)

# Galois field inverse for 128 bit GCM elements
# Done by exponentiation with the power of 2^128 - 2
def gf128_inverse(a: int) -> int:
    negative_one =  gcm_convert128((1 << 128) - 2)
    inverse = gf128_pow_gcm(a, negative_one)
    return inverse

def gf_add_bytes(a: bytes, b: bytes) -> bytes:

    # Pad shorter byte array with zeros to match length
    if len(a) < len(b):
        a = a + bytes(len(b) - len(a))
    elif len(b) < len(a):
        b = b + bytes(len(a) - len(b))

    return bytes(x ^ y for x, y in zip(a, b))