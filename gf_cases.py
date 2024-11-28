from gf.types import gf128, gfpoly
from gf.primitives import gf128_mul
import gf.functions as gff

import helper

def exec_gfpoly_add(A, B):
    a = gfpoly.from_b64array(A)
    b = gfpoly.from_b64array(B)
    result = a + b

    return {"S": result.as_b64array()}

def exec_gfpoly_mul(A, B):
    a = gfpoly.from_b64array(A)
    b = gfpoly.from_b64array(B)
    result = a * b

    return {"P": result.as_b64array()}

def exec_gfpoly_pow(A, k):
    A = gfpoly.from_b64array(A)
    return {"Z": A.pow(k).as_b64array()}


def exec_gfdiv(a, b):

    a = gf128.from_b64(a)
    b = gf128.from_b64(b)

    return{"q": (a / b).b64() }

def exec_gfpoly_divmod(A, B):
    a = gfpoly.from_b64array(A)
    b = gfpoly.from_b64array(B)
    q, r = a.divmod(b)

    return {"Q": q.as_b64array(), "R": r.as_b64array()}

def exec_gfpoly_powmod(A, M, k):
    A = gfpoly.from_b64array(A)
    M = gfpoly.from_b64array(M)

    return {"Z": A.powmod(k, M).as_b64array()}

def exec_gfpoly_sort(polys):
    polys = [gfpoly.from_b64array(poly) for poly in polys]
    polys = gff.sort_polys(polys)
    return {"sorted_polys": [poly.as_b64array() for poly in polys]}

def exec_gfpoly_make_monic(A):
    A = gfpoly.from_b64array(A)
    return {"A*": A.make_monic().as_b64array()}

def exec_gfpoly_sqrt(Q):
    Q = gfpoly.from_b64array(Q)
    return {"S": Q.sqrt().as_b64array()}

def exec_gfpoly_diff(F):
    F = gfpoly.from_b64array(F)
    return {"F'": F.derivative().as_b64array()}

def exec_gfpoly_gcd(A, B):
    A = gfpoly.from_b64array(A)
    B = gfpoly.from_b64array(B)
    return {"G": gff.gcd_poly(A, B).as_b64array()}

def exec_gfpoly_sff(f):

    f = gfpoly.from_b64array(f)
    factors = []
    for factor, e in gff.sort_sff_result(gff.sff(f)):
        factors.append({"factor": factor.as_b64array(), "exponent": e})

    return {"factors": factors}

def exec_gfpoly_ddf(f):
    f = gfpoly.from_b64array(f)
    factors = []
    for factor, d in gff.sort_sff_result(gff.ddf(f)):
        factors.append({"factor": factor.as_b64array(), "degree": d})


    return {"factors": factors}

def exec_gfpoly_edf(F, d):
    F = gfpoly.from_b64array(F)
    result = gff.edf(F, d)
    sorted_result = gff.sort_polys(result)
    return {"factors": [poly.as_b64array() for poly in sorted_result]}


def exec_gfpoly(assignment):
    
    arguments = assignment["arguments"]
    action = assignment["action"]

    match action:
        case "gfpoly_add":
            return exec_gfpoly_add(arguments["A"], arguments["B"])
        
        case "gfpoly_mul":
            return exec_gfpoly_mul(arguments["A"], arguments["B"])

        case "gfpoly_pow":
            return exec_gfpoly_pow(arguments["A"], arguments["k"])

        case "gfdiv":
            return exec_gfdiv(arguments["a"], arguments["b"])
        
        case "gfpoly_divmod":
            return exec_gfpoly_divmod(arguments["A"], arguments["B"])
        
        case "gfpoly_powmod":
            return exec_gfpoly_powmod(arguments["A"], arguments["M"], arguments["k"])
        
        case "gfpoly_sort":
            return exec_gfpoly_sort(arguments["polys"])
        
        case "gfpoly_make_monic":
            return exec_gfpoly_make_monic(arguments["A"])
        
        case "gfpoly_sqrt":
            return exec_gfpoly_sqrt(arguments["Q"])
        
        case "gfpoly_diff":
            return exec_gfpoly_diff(arguments["F"])
        
        case "gfpoly_gcd":
            return exec_gfpoly_gcd(arguments["A"], arguments["B"])
        
        case "gfpoly_factor_sff":
            return exec_gfpoly_sff(arguments["F"])
        
        case "gfpoly_factor_ddf":
            return exec_gfpoly_ddf(arguments["F"])
        
        case "gfpoly_factor_edf":
            return exec_gfpoly_edf(arguments["F"], arguments["d"])



def exec_gf128_mul(assignment):
    arguments = assignment["arguments"]
    semantic = arguments["semantic"]

    if semantic == "xex":
    
        a = helper.base64_to_int16(arguments["a"])
        b = helper.base64_to_int16(arguments["b"])

        return {"product": helper.int16_to_base64(gf128_mul(a, b)) }
    
    elif semantic == "gcm":
        
        a = gf128.from_b64(arguments["a"])
        b = gf128.from_b64(arguments["b"])

        return {"product": (a * b).b64() } 
