from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

# Generate RSA key pair
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

# Save the private key and public key
with open('private_key.pem', 'wb') as f:
    f.write(private_key)

with open('public_key.pem', 'wb') as f:
    f.write(public_key)

# Message to be signed
message = b"hr123@gmail.com"

# Hash the message using SHA-256
h = SHA256.new(message)

# Sign the hashed message using the private key
private_key_rsa = RSA.import_key(private_key)
signature = pkcs1_15.new(private_key_rsa).sign(h)

# Output the signature in hex format
print(f"Signature: {signature.hex()}")

# Verify the signature using the public key
public_key_rsa = RSA.import_key(public_key)

try:
    pkcs1_15.new(public_key_rsa).verify(h, signature)
    print("Signature is valid.")
except (ValueError, TypeError):
    print("Signature is invalid.")
