from gf.primitives import gf128_mul
import sea128

import helper

# Splits the input blocks, prepare the tweak and split the key
def prepare_input(key: bytes, tweak: bytes, data: bytes) -> tuple[bytes, bytes, list[bytes]]:
    blocks = helper.slice_blocks_16(data)
    key1, key2 = helper.slice_blocks_16(key)[:2]
    tweak = sea128.encrypt(key2, tweak)

    return (key1, tweak, blocks)

def gf128_mul_alpha(tweak: bytes ) -> bytes:
    numeric_tweak = int.from_bytes(tweak, byteorder="little")
    return gf128_mul(numeric_tweak, 0x2).to_bytes(16, byteorder="little") # multiply with 0x2 ^= 0010 ^= alpha


def encrypt(key: bytes, tweak: bytes, data: bytes) -> list[bytes]:

    encrypted_blocks = []
    key1, tweak, blocks = prepare_input(key, tweak, data)

    for i in range(len(blocks)):
        plaintext = blocks[i]

        tweaked_plaintext = helper.xor_buf(plaintext, tweak)
        encrypted_plaintext = sea128.encrypt(key1, tweaked_plaintext)
        encrypted_block = helper.xor_buf(encrypted_plaintext, tweak)

        encrypted_blocks.append(encrypted_block)

        tweak = gf128_mul_alpha(tweak)

    return encrypted_blocks


def decrypt(key: bytes, tweak: bytes, data: bytes) -> list[bytes]:
    
    decrypted_blocks = []
    key1, tweak, blocks = prepare_input(key, tweak, data)

    for i in range(len(blocks)):
        encrypted_block = blocks[i]

        decrypted_block = helper.xor_buf(encrypted_block, tweak)
        decrypted_plaintext = sea128.decrypt(key1, decrypted_block)
        plaintext = helper.xor_buf(decrypted_plaintext, tweak)

        decrypted_blocks.append(plaintext)
        
        tweak = gf128_mul_alpha(tweak)

    return decrypted_blocks


def exec_cipher(assignment):

    arguments = assignment["arguments"]
    mode = arguments["mode"]
    key = helper.base64_to_buffer(arguments["key"])
    tweak = helper.base64_to_buffer(arguments["tweak"])
    input = helper.base64_to_buffer(arguments["input"])

    if mode == "encrypt":
        encrypted_blocks = encrypt(key, tweak, input)
        return {"output": helper.buffer_to_base64(helper.merge_blocks_16(encrypted_blocks))}
    
    elif mode == "decrypt":
        decrypted_blocks = decrypt(key, tweak, input)
        return {"output": helper.buffer_to_base64(helper.merge_blocks_16(decrypted_blocks))}
    