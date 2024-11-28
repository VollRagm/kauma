import os
import subprocess
import sys
import json

failed_tests = []
total_tests = 0

def print_fail(fail_message, expected, got, errors, test_file):
    print(fail_message)
    print(f"Expected: {expected}")
    print(f"Got: {got}")
    if errors:
        print(f"Errors: {errors}")
    failed_tests.append(test_file)

def run_test(test_file):
    
    result_file = test_file.replace('cases', 'expected')
    with open(result_file) as f:
        expected_data = f.read()
    
    # Launch the redirector.py script with the test file
    process = subprocess.Popen([sys.executable, 'redirector.py', test_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    
    try:
        json_data = json.loads(stdout)
    except json.JSONDecodeError:
        print_fail(f"Test {test_file} failed. Invalid JSON", expected_data, stdout, stderr, test_file)
        return
    
    # compare if result matches expected data on an object level
    if sorted(json_data.items()) == sorted(json.loads(expected_data).items()):
        print(f"Test {test_file} passed.")
    else:
        print_fail(f"Test {test_file} failed.", expected_data, stdout, stderr, test_file)


test_dir = 'tests/cases/'

# Get all json files in cases directory and run tests on them
for test_file in os.listdir(test_dir):
    if test_file.endswith('.json'):
        total_tests += 1
        run_test(os.path.join(test_dir, test_file))
    
print(f"{total_tests - len(failed_tests)}/{total_tests} tests passed.")
if failed_tests:
    print(f"Failed tests: {', '.join(failed_tests)}")