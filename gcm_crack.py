from gf.types import gfpoly, gf128
from gf.functions import sff, ddf, edf
import gcm
import helper

class gcm_msg:
    def __init__(self, m: dict):
        self.ciphertext = (helper.base64_to_buffer(m['ciphertext']))
        self.tag = helper.base64_to_buffer(m['tag'])
        self.ad = helper.base64_to_buffer(m['associated_data'])

# This function will build the right side of the equation for the factorization
def build_ghash_poly(ad: bytes, ciphertext: bytes) -> gfpoly:
    
    # cut down input into padded 16-byte blocks
    A_blocks = helper.slice_blocks_16(helper.pad_bytes_16(ad))
    C_blocks = helper.slice_blocks_16(helper.pad_bytes_16(ciphertext))
    
    # calculation of L taken from ghash function
    ad_bit_length = len(ad) * 8
    ciphertext_bit_length = len(ciphertext) * 8
    ad_len_buf = ad_bit_length.to_bytes(8, byteorder='big')
    ciphertext_len_buf = ciphertext_bit_length.to_bytes(8, byteorder='big')

    # Concat to calculate L
    L = ad_len_buf + ciphertext_len_buf
    
    # Y blocks: A_blocks + C_blocks + [len_block]
    ghash_blocks = A_blocks + C_blocks + [L]

    # Constant term (X_0) is zero
    coeffs = [b'\x00' * 16]  # X_0 = 0

    # from left-to-right in GHASH, the leftmost block coeff is h^1 then h^2, bla bla bla...
    # thats why we need to reverse the order of the blocks to build the polynomial in the correct order
    for block in ghash_blocks[::-1]:
        coeffs.append(block)

    return gfpoly(coeffs)


# This function will build the monic polynomial equation for the factorization
def build_equation(m1: gcm_msg, m2: gcm_msg) -> gfpoly:

    right_side_1 = build_ghash_poly(m1.ad, m1.ciphertext)
    right_side_2 = build_ghash_poly(m2.ad, m2.ciphertext)

    # calculate difference polynomial
    right_side = right_side_1 + right_side_2

    # calculate left side, aka T_V + T_U
    left_side = gfpoly([m1.tag]) + gfpoly([m2.tag])

    # bring everything to the left side
    equation = right_side + left_side

    return equation.make_monic()


# This function will factorize the polynomial equation returning solutions for H
def factorize(equation: gfpoly) -> list[gf128]:
    
    # run square-free factorization
    sff_factors = sff(equation)
    
    factors = []
    for factor, multiplicity in sff_factors:
        # Further factor each factor
        ddf_factors = ddf(factor)
        for ddf_factor, degree in ddf_factors:
            # run edf on factors with degree > 1
            if ddf_factor.degree() > 1:
                edf_factors = edf(ddf_factor, degree)
                factors.extend(edf_factors)
            else:
                factors.append(ddf_factor)

    # extract roots
    candidates = []
    for factor in factors:
        # we only care about linear factors (X + c)
        if factor.degree() == 1:
            root = gf128.from_buf(factor.coeff()[0])
            candidates.append(root)
    
    return candidates

def get_mask_for_candidate(m: gcm_msg, candidate: gf128) -> bytes:
    ghash_result, _ = gcm.ghash(m.ad, m.ciphertext, candidate.as_buf())
    return helper.xor_buf(m.tag, ghash_result)


# This function will find the auth key H and mask that was used to generate the tags for the messages m1, m2, m3
def crack_auth_key(m1: gcm_msg, m2: gcm_msg, m3: gcm_msg) -> tuple[gf128, gf128]:
    equation = build_equation(m1, m2)
    # let it rip!
    candidates = factorize(equation)

    # use m3 to find the correct root
    for candidate in candidates:
        # Get the mask that gets xored at the end
        mask = get_mask_for_candidate(m1, candidate)
        # Calculate the tag for m3 with the candidate
        ghash_result, _ = gcm.ghash(m3.ad, m3.ciphertext, candidate.as_buf())
        potential_tag = helper.xor_buf(mask, ghash_result)
        if potential_tag == m3.tag:
            # Bingo!
            return candidate, gf128.from_buf(mask)


def exec_gcm_crack(assignment):
    arguments = assignment["arguments"]

    m1 = gcm_msg(arguments['m1'])
    m2 = gcm_msg(arguments['m2'])
    m3 = gcm_msg(arguments['m3'])
    
    forgery_ciphertext = helper.base64_to_buffer(arguments['forgery']['ciphertext'])
    forgery_ad = helper.base64_to_buffer(arguments['forgery']['associated_data'])

    H, mask = crack_auth_key(m1, m2, m3)

    forged_tag, _ = gcm.ghash(forgery_ad, forgery_ciphertext, H.as_buf())
    forged_tag = helper.xor_buf(forged_tag, mask.as_buf())

    return { 'tag': helper.buffer_to_base64(forged_tag), 'H': H.b64(), 'mask': mask.b64() }

