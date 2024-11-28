from gf.types import gfpoly, gf128
import gf.primitives as primi

# Sort by .degree(). If Degree is equal, sort by .coeff() values.
def sort_polys(polys: list[gfpoly]) -> list[gfpoly]:
    polys.sort(key=lambda x: (x.degree(), primi.gcm_convert(x.int())))
    return polys

def sort_sff_result(results):
    results.sort(key=lambda x: (x[0].degree(), primi.gcm_convert(x[0].int())))
    return results
    
def gcd_poly(a: gfpoly, b: gfpoly) -> gfpoly:
    # Create copies
    a = gfpoly(a.coeff())
    b = gfpoly(b.coeff())

    if a.degree() < b.degree():
        a, b = b, a

    while not b.coeff() == [b'\x00' * 16]:
        _, r = a.divmod(b)
        a, b = b, r

    return a.make_monic()

# Square-free factorization
def sff(f: gfpoly) -> list[tuple[gfpoly, int]]:
    f_diff = f.derivative()
    
    c = gcd_poly(f, f_diff)
    
     # f = f / c
    f_div_c, remainder = f.divmod(c)
    f = f_div_c

    z = []  # result list for factors
    e = 1   # exponent

    while f != gfpoly.one():
        # y = gcd(f, c)
        y = gcd_poly(f, c)

        if f != y:
            # Factor found: f / y
            factor, remainder = f.divmod(y)
            z.append((factor, e))

        f = y

        # c = c / y
        c_div_y, remainder = c.divmod(y)
        c = c_div_y

        e += 1

    if c != gfpoly.one():
        # Recursive call with sqrt_c
        sqrt_c = c.sqrt()
        r = sff(sqrt_c)

        for (f_star, e_star) in r:
            # Double all exponents
            z.append((f_star, 2 * e_star))

    return z

# Distinct degree factorization
def ddf(f: gfpoly) -> list[tuple[gfpoly, int]]:
    z = []
    d = 1
    f_monic = gfpoly(f.coeff()).make_monic() # f*

    # Bingo, let it rip
    while f_monic.degree() >= 2 * d:
        # h = X^{2^{128d}} + X mod f*
        h = gfpoly.X().powmod(2 ** (128 * d), f_monic)
        h = h + gfpoly.X()

        # g = gcd(h, f*)
        g = gcd_poly(h, f_monic)

        if g != gfpoly.one():
            z.append((g.make_monic(), d))
            # f* = f* / g
            f_monic, _ = f_monic.divmod(g)

        d += 1

    if f_monic != gfpoly.one():
        z.append((f_monic.make_monic(), f_monic.degree()))
    elif len(z) == 0:
        z.append((f.make_monic(), 1))

    return z

# Equal degree factorization (Cantor-Zassenhaus)
def edf(f: gfpoly, d: int) -> list[gfpoly]:
    q = 2**128
    z = [f]
    
    while any(u.degree() > d for u in z):
        h = gfpoly.random(f.degree() - 1)  # random poly with deg(h) < deg(f)
        
        e = (q**d - 1) // 3
        # h^e = h^[(q^d - 1) / 3]
        h_pow_e = h.powmod(e, f)
        # g = h^e - 1
        g = h_pow_e + gfpoly.one()  
        
        for u in z[:]:  # Iterate over a copy of z to avoid modifying the list while iterating
            if u.degree() > d:
                
                j = gcd_poly(u, g)
                
                if  j != gfpoly.one() and j != u:
                    # Replace u with j and u / j in z
                    z.remove(u)
                    z.append(j.make_monic())
                    quotient, _ = u.divmod(j)
                    z.append(quotient.make_monic())
    return z