from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


import sea128
from gf.types import gf128
import helper

def encrypt_aes128(key, data):
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()

    return ciphertext

def encrypt_sea128(key, data):
    return sea128.encrypt(key, data)


# Encrypts the plaintext using CTR mode with the given cipher func
def encrypt_ctr(key: bytes, nonce: bytes, plaintext: bytes, cipher_func) -> bytes:

    blocks = helper.slice_blocks_16(plaintext)

    counter = 2 # CTR in GCM starts at 2 due to H and Y0
    keystream_plain = nonce + counter.to_bytes(4, byteorder='big')

    encrypted_blocks = []
    for block in blocks:
        keystream_plain = cipher_func(key, keystream_plain)     # Generate current block-key
        encrypted_block = helper.xor_buf(block, keystream_plain)
        encrypted_blocks.append(encrypted_block)
        counter += 1
        keystream_plain = nonce + counter.to_bytes(4, byteorder='big')

    return helper.merge_blocks_16(encrypted_blocks)


def ghash(ad: bytes, ciphertext: bytes, auth_key: bytes) -> tuple[bytes, bytes]:

    hash = b'\x00' * 16

    for ad_block in helper.slice_blocks_16(ad):
        assoc_data = helper.pad_block_16(ad_block)
        hash = helper.xor_buf(hash, assoc_data)
        hash = (gf128.from_buf(hash) * gf128.from_buf(auth_key)).as_buf()

    # Apply Auth Key to each ciphertext block
    for block in helper.slice_blocks_16(ciphertext):
        padded_block = helper.pad_block_16(block)
        hash = helper.xor_buf(hash, padded_block)
        hash = (gf128.from_buf(hash) * gf128.from_buf(auth_key)).as_buf()
    
    # Calculate bit lengths of AD and Ciphertext and convert to 64 bit big endian
    ad_bit_length = len(ad) * 8
    ciphertext_bit_length = len(ciphertext) * 8
    ad_len_buf = ad_bit_length.to_bytes(8, byteorder='big')
    ciphertext_len_buf = ciphertext_bit_length.to_bytes(8, byteorder='big')

    # Concat to calculate L
    L = ad_len_buf + ciphertext_len_buf

    hash = helper.xor_buf(hash, L)
    hash = (gf128.from_buf(hash) * gf128.from_buf(auth_key)).as_buf()

    return (hash, L)


def encrypt_gcm(key: bytes, nonce: bytes, plaintext: bytes, ad: bytes, cipher_func) -> tuple[bytes, bytes, bytes, bytes]:
    
    # Generate H (Auth key) and Y0
    auth_key = cipher_func(key, b'\x00' * 16)

    y0 = nonce + (1).to_bytes(4, byteorder='big')
    y0 = cipher_func(key, y0)

    ciphertext = encrypt_ctr(key, nonce, plaintext, cipher_func)

    hash, L = ghash(ad, ciphertext, auth_key)
    tag = helper.xor_buf(hash, y0)

    return ciphertext, tag, L, auth_key

def decrypt_gcm(key: bytes, nonce: bytes, ciphertext: bytes, ad: bytes, tag_given: bytes, cipher_func) -> tuple[bytes, bool]:

    # Generate H (Auth key) and Y0
    auth_key = cipher_func(key, b'\x00' * 16)

    y0 = nonce + (1).to_bytes(4, byteorder='big')
    y0 = cipher_func(key, y0)

    hash, L = ghash(ad, ciphertext, auth_key)
    plaintext = encrypt_ctr(key, nonce, ciphertext, cipher_func)

    tag = helper.xor_buf(hash, y0)

    return (plaintext, tag == tag_given)

def exec_cipher(assignment):

    action = assignment["action"]
    arguments = assignment["arguments"]

    algorithm = arguments["algorithm"]
    nonce = helper.base64_to_buffer(arguments["nonce"])
    key = helper.base64_to_buffer(arguments["key"])
    ad = helper.base64_to_buffer(arguments["ad"])

    if action == "gcm_encrypt":

        plaintext = helper.base64_to_buffer(arguments["plaintext"])

        if algorithm == "aes128":
            ciphertext, tag, L, auth_key = encrypt_gcm(key, nonce, plaintext, ad, encrypt_aes128)
            
        elif algorithm == "sea128":
            ciphertext, tag, L, auth_key = encrypt_gcm(key, nonce, plaintext, ad, encrypt_sea128)
        
        return {
            "ciphertext": helper.buffer_to_base64(ciphertext), 
            "tag": helper.buffer_to_base64(tag), 
            "L": helper.buffer_to_base64(L), 
            "H": helper.buffer_to_base64(auth_key)
            }
    
    elif action == "gcm_decrypt":
        
        ciphertext = helper.base64_to_buffer(arguments["ciphertext"])
        tag = helper.base64_to_buffer(arguments["tag"])

        if algorithm == "aes128":
            plaintext, authentic = decrypt_gcm(key, nonce, ciphertext, ad, tag, encrypt_aes128)
        elif algorithm == "sea128":
            plaintext, authentic = decrypt_gcm(key, nonce, ciphertext, ad, tag, encrypt_sea128)

        return {"plaintext": helper.buffer_to_base64(plaintext), "authentic": authentic}
    
