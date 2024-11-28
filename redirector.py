import os
import sys
import json

import add_sub_number
import padding_oracle.attack
import polyblock
import gf_cases
import sea128
import xex
import padding_oracle
import gcm
import gcm_crack

# Handler table holds maps the assignment action to the corresponding handler function
handler_table = {
    "add_numbers": add_sub_number.add_numbers,
    "subtract_numbers": add_sub_number.subtract_numbers,
    "poly2block": polyblock.exec_poly2block,
    "block2poly": polyblock.exec_block2poly,
    "gfmul": gf_cases.exec_gf128_mul,
    "sea128": sea128.exec_cipher,
    "xex": xex.exec_cipher,
    "padding_oracle": padding_oracle.attack.exec_attack,
    "gcm_encrypt": gcm.exec_cipher,
    "gcm_decrypt": gcm.exec_cipher,
    "gfpoly_add": gf_cases.exec_gfpoly,
    "gfpoly_mul": gf_cases.exec_gfpoly,
    "gfpoly_pow": gf_cases.exec_gfpoly,
    "gfdiv": gf_cases.exec_gfpoly,
    "gfpoly_divmod": gf_cases.exec_gfpoly,
    "gfpoly_powmod": gf_cases.exec_gfpoly,
    "gfpoly_sort": gf_cases.exec_gfpoly,
    "gfpoly_make_monic": gf_cases.exec_gfpoly,
    "gfpoly_sqrt": gf_cases.exec_gfpoly,
    "gfpoly_diff": gf_cases.exec_gfpoly,
    "gfpoly_gcd": gf_cases.exec_gfpoly,
    "gfpoly_factor_sff": gf_cases.exec_gfpoly,
    "gfpoly_factor_ddf": gf_cases.exec_gfpoly,
    "gfpoly_factor_edf": gf_cases.exec_gfpoly,
    "gcm_crack": gcm_crack.exec_gcm_crack
}

if len(sys.argv) != 2:
	print("syntax: %s <jsonfile>" % (sys.argv[0]))
	sys.exit(1)

json_file = sys.argv[1]

with open(json_file) as f:
    assignment = json.load(f)

responses = {"responses": {}}

def add_response(testcase_id, response):
    responses["responses"][testcase_id] = response

for testcase, testcase_content in assignment["testcases"].items():

    action = testcase_content["action"]
    handler = handler_table.get(action) # Get the handler for the action
    if handler is None:
        print(f"Handler for action '{action}' not found")
        continue

    response = handler(testcase_content)
    add_response(testcase, response)

print(json.dumps(responses, indent=4))
