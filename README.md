
# Kauma

## Description

Kauma is a tool developed for Cryptoanalysis. It includes various real-world cryptographic implementations and attacks, providing a program for studying and testing cryptographic concepts.

**A performance enhanced version using the PCLMULQDQ will be available soon.**

## Disclaimer

The algorithms displayed in this repository are for cryptoanalysis purposes only. While they produce correct results, they must not be used in production environments. Use them solely for educational and testing purposes.


## Algorithms and attacks included

  

-  **redirector**: This is the top-level execution script that routes different cryptographic operations and attacks to their respective handler functions based on the provided action in the test case.

-  **gcm**: Implements the Galois/Counter Mode (GCM) for authenticated encryption and decryption as specified by [NIST](https://csrc.nist.rip/groups/ST/toolkit/BCM/documents/proposedmodes/gcm/gcm-spec.pdf). It includes functions for encrypting and decrypting data using AES-128 and SEA-128 algorithms, as well as generating and verifying authentication tags. The SEA-128 algorithm is a custom defined algorithm in sea128.py

  -  **gcm_crack**: Implements an attack to crack the authentication key used in GCM and completely break it on nonce re-use. It includes functions for building polynomial equations from GCM messages, factorizing these equations, and identifying the correct authentication key and mask used to generate message tags. The authentication key is used to create a tag forgery that can be used to authenticate modified messages.

-  **padding_oracle**: Contains the implementation of a padding oracle attack. It includes functions for generating prepend-blocks, decrypting single blocks, and executing the attack by interacting with a server that simulates the padding oracle.

-  **xex**: Implements the XEX/XTS mode of encryption and decryption. It includes functions for preparing input, encrypting, and decrypting data blocks with a given key and tweak. 

-  **gf.types/primitives/functions**: Implements various operations for Galois Fields (GF). This includes polynomial arithmetic, multiplication, inversion, and other helper functions for working with GF(2^128) used in cryptographic algorithms.

## Running the Script with Test Case
Make sure the cryptography module is installed.
```sh
pip3 install cryptography
```

To run the script with specific test cases, use the following command:

```sh

python redirector.py <test_case_name>

```

Replace `<test_case_name>` with the name of the test case in json you want to run. Bytes-arguments in testcases are encoded in Base64.

  

## Running All Tests

To run all test cases, use the following command:

```sh

python  run_tests.py

```

Ensure that all testcases are present both in tests/cases with their expected output in tests/expected.

  

## Server Simulator

The server simulator is designed to mimic the behavior of the real server used in the padding-oracle testcases, facilitating the testing of cryptographic protocols and attacks in a controlled environment. It responds to requests with predefined responses, allowing for detailed analysis of how different cryptographic implementations handle various server responses, including errors and edge cases. To launch the server simulator, specify `server_simulator` as the host in the test case configuration.