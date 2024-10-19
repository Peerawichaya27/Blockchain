from eth_keys import keys
from eth_utils import decode_hex

# The private key provided
private_key_hex = '0x4c0883a69102937d6231471b5dbb6204fe512961708279229f15c0d2c8b2e5bb'
private_key = keys.PrivateKey(decode_hex(private_key_hex))

# Get the public key corresponding to the private key
public_key = private_key.public_key

# Convert public key to hexadecimal format
public_key_hex = public_key.to_hex()
print(public_key_hex)
