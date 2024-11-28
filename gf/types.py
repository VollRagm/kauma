import gf.primitives as primitives
import helper

def reduce_poly(poly: list[bytes]):
    if len(poly) == 0:
        return [b'\x00' * 16]
    
    # Check if the polynomial is all zeros and reduce it to a single block
    if all([block == b'\x00' * 16 for block in poly]):
        return [b'\x00' * 16]
    
    # Remove trailing zero-blocks
    while len(poly) > 1 and poly[-1] == b'\x00' * 16:
        poly.pop()

    return poly

# Class implementation for polynomial operations in GF(2^128) with GCM conversion
class gfpoly:
    def __init__(self, coeff: list[bytes]):
        self.__coeff = coeff.copy() # Copy the list to avoid reference issues
        self.__coeff = reduce_poly(self.__coeff)
        
    def as_buf(self) -> bytes:
        block = b''.join(self.__coeff)
        return helper.pad_bytes_16(block)
    
    def coeff(self) -> list[bytes]:
        return helper.slice_blocks_16(self.as_buf())

    @staticmethod
    def from_b64array(array):
        array_bytes = [helper.base64_to_buffer(b64_string) for b64_string in array]
        return gfpoly(array_bytes)
    
    def as_b64array(self):
        return [helper.buffer_to_base64(block) for block in self.__coeff]
    
    def from_int(value: int):
        num_bytes = (value.bit_length() + 7) // 8  # Round up to the nearest byte
        block = value.to_bytes(num_bytes, byteorder='little')
        buffer = helper.pad_bytes_16(block)
        return gfpoly(helper.slice_blocks_16(buffer))
    
    @staticmethod
    def random(degree):
        random_bytes = helper.random_bytes(16 * (degree + 1))
        return gfpoly(helper.slice_blocks_16(random_bytes))

    def int(self):
        return int.from_bytes(b''.join(self.__coeff), byteorder='little')
    
    @staticmethod
    def one():
        return gfpoly.from_int(1 << 7)
    
    def X():
        return gfpoly([b'\x00' * 16, gf128(1).as_buf()])
    
    def degree(self):
        return len(self.__coeff) - 1

    def __add__(self, other):
        result = primitives.gf_add_bytes(self.as_buf(), other.as_buf())
        list_result = helper.slice_blocks_16(result)
        return gfpoly(list_result)
    
    def __mul__(self, other):

        p = self.__coeff
        q = other.__coeff
        result = []
            
        for x in range(len(p)):
            for y in range(len(q)):
            
                # Calculate product of coefficients
                a = gf128.from_buf(p[x])
                b = gf128.from_buf(q[y])
                product = (a * b).as_buf()
                
                # Increase result degree if necessary
                if len(result) <= x + y:
                    result.extend([b'\x00' * 16] * (x + y - len(result) + 1))

                result[x + y] = (gf128.from_buf(result[x + y]) + gf128.from_buf(product)).as_buf()
        
        return gfpoly(result)
    
    def pow(self, exponent):
        result = gfpoly.from_int(1 << 7)  # 1 in GCM
        base = self

        # Square and multiply algorithm
        while exponent > 0:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1

        return result
    
    def divmod(self, divisor):
        remainder = self        
        result = []
        
        while remainder.degree() >= divisor.degree() and remainder.coeff() != [b'\x00' * 16]:
            # get the lead coefficients
            remainder_highest_degree = remainder.coeff()[remainder.degree()]
            divisor_highest_degree = divisor.coeff()[divisor.degree()]
            
            rlc = gf128.from_buf(remainder_highest_degree)
            dlc = gf128.from_buf(divisor_highest_degree)
            factor = (rlc / dlc).as_buf()
            
            degree_delta = remainder.degree() - divisor.degree()

            # Increase result degree if necessary
            if len(result) <= degree_delta:
                result.extend([b'\x00' * 16] * (degree_delta - len(result) + 1))

            result[degree_delta] = factor
            
            # Prepend zeros to match degree
            scaled_res = [b'\x00' * 16] * degree_delta
            for coeff in divisor.coeff():
                scaled = gf128.from_buf(coeff) * gf128.from_buf(factor)
                scaled_res.append(scaled.as_buf())
            
            # Subtract scaled divisor from remainder
            remainder += gfpoly(scaled_res)

        return (gfpoly(result), remainder)
    
    def powmod(self, exponent, modulus):
        result = gfpoly.from_int(1 << 7)  # 1 in GCM
        base = self

       # Square and multiply algorithm with modulus
        while exponent > 0:
            if exponent & 1:
                result = (result * base).divmod(modulus)[1] # Get the remainder
            base = (base * base).divmod(modulus)[1]
            exponent >>= 1

        return result
    
    def make_monic(self):
        
        lead_coeff = gf128.from_buf(self.coeff()[-1])
        for i in range(len(self.__coeff)):
            self.__coeff[i] = (gf128.from_buf(self.__coeff[i]) / lead_coeff).as_buf()

        return self
    
    def sqrt(self):
        coeffs = self.coeff()
        sqrt_coeffs = []

        # calculate each sqrt of the coefficients at even exponents
        for i in range(0, len(coeffs), 2):
            c = coeffs[i]
            gf_c = gf128.from_buf(c)
            sqrt_c = gf_c.sqrt()
            sqrt_coeffs.append(sqrt_c.as_buf())

        return gfpoly(sqrt_coeffs)
    
    def derivative(self):
        coeffs = self.coeff()
        result = []

        for i in range(1, len(coeffs)):
            if i % 2 == 1:
                # For odd exponents, the derivative coefficient is the original coefficient
                result.append(coeffs[i])
            else:
                # For even exponents its zero
                result.append(b'\x00' * 16)

        return gfpoly(result)
    
    def __eq__(self, other):
        if not isinstance(other, gfpoly):
            return False
        
        # Compare coefficient values
        return self.coeff() == other.coeff()


        
    
# Class implementation for finite field elements in GF(2^128) with GCM conversion
class gf128:
    def __init__(self, value: int):
        self.__value = value

    @staticmethod
    def from_buf(value: bytes):
        return gf128(int.from_bytes(value, byteorder='little'))
    
    def as_buf(self):
        return self.__value.to_bytes(16, byteorder='little')
    
    @staticmethod
    def from_b64(value: str):
        return gf128.from_buf(helper.base64_to_buffer(value))
    
    def b64(self):
        return helper.buffer_to_base64(self.as_buf())
    
    def int(self):
        return self.__value

    def __add__(self, other):
        return gf128(self.__value ^ other.__value)
    
    def __mul__(self, other):
        return gf128(primitives.gf128_mul_gcm(self.__value, other.__value))
    
    def inverse(self):
        return gf128((primitives.gf128_inverse(self.__value)))
    
    def __truediv__(self, other):
        return self * other.inverse()
    
    def pow(self, exponent):
        result = gf128(1 << 7)
        base = self
        while exponent > 0:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent >>= 1
        return result

    def sqrt(self):
        exponent = 1 << 127  # 2^127
        return self.pow(exponent)