from eth_keys import keys
from eth_utils import decode_hex
import hashlib

# Employer's private key
private_key_hex = '0x4c0883a69102937d6231471b5dbb6204fe512961708279229f15c0d2c8b2e5bb'
private_key = keys.PrivateKey(decode_hex(private_key_hex))

# Message to sign (e.g., email)
message = b"hr123@gmail.com"
message_hash = hashlib.sha256(message).digest()

# Sign the message hash
signature = private_key.sign_msg_hash(message_hash)

# Output the signature in hex format
print(f"Signature: {signature.to_hex()}")

# Get the corresponding public key
public_key = private_key.public_key
print(f"Public Key: {public_key.to_hex()}")
