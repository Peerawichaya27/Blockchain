import json
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import binascii
import random
import string

# RSA Private Key
PRIVATE_KEY_PEM = '''-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAq1U2sopY+ktpsV/stESicL+G5eU0j9c4zOxyGUVUbM3N/69C
fmMrjG9Y57Jpuq6QXYXvg+sPNOs71Wo7JdZtoTTpk6z89hzg6ZgT0583oxEyPZNb
h657YTLNuQJayPm2LTXmbVERa884eLO/IfvpseRLQSXkOu+9cYaT6gtmZprf+9mR
lotejLxRJvZuiCcuwVlNssM1v/nvPdN5jS1jGrwOGgXAQyouHbO9n1Sc5zJSeJrh
Fu7JCeIsvcCZQrUQqM5/hYPinbHsyKSDJ3wwy8yVnfQ9xkG0bKL942QedmN7fUuy
NtGWmC8Xp21dQqdgSlz7f5T+XKm/D2qoywyJkQIDAQABAoIBACQ+Ghwx8kj9/11f
UIPAmgkWJrvGXLRJv3Dv2mH4nbeHYHpj8UGpijqCilC217E/AHhcHvKtnFGiKg3G
0zy5i4bEmd1chEUujjAztIv5O+xxdIp8e6nrsZs5wzVN53Toh84v/u6kbbY7xzMX
OMkAUCrKg1XEZW9HK/CSGoNxhmeRJalJs2yGqg4FCqVEeKpu+Soot9Aelibd46gy
V3hpKW4N9cTcgF50cfxwlpZMDmscQXxYSHRdM00ME4xP+1WXv78l7ANWw9jMjjng
A0bQOq10SrBJRFljSw0OZupuPRXYqtzMSUynsDLk3q83IQY1wrm4sR2VybYCzmQ5
xOnsb20CgYEAuWRNNHIOK1RIP0QDJIFp5oaFNzfEcS0l6sOOFLwsdBvenullveJg
ijzsL1lpxgZoQTt3v8qZAJv/SJo4qvaFIRPgRuNCwUnnPLvzsFlZPxESfRHLwkc6
7HjTpSdDHSB00aWi0WOZ0DjzNzl1S7ksin+tBQ4sAqvRG5ZbvBzn1r0CgYEA7JYq
d3F7Vo+r7A/w2Sd0QGcAY3M6OUHLKsw7moxOrvEjMXhoLprsHg+gaWmMtFpHdHW5
6M2XGVtfJv9QVgLR56cIj2RT7zkXcjZpEhd6pP18rf36s9VX9Yi52RYl9C5/dh/J
FM7lo/MfdxQ2ouxrpLIDeVSEXhYh5mOHSwwxpWUCgYAzB2e00twRkx5bw6W1y6VR
nZ9XZpM8r7erGe6myHDX+L/bL9UgYgo+oqxEEDFsH2Fc6zh34xUgNNActM56SGa2
hxkJig5a07PBZN6boMxO7q0PHfHe5OpUIqHm6Jqxjrh46EWbqvWweayAe+FMWYjo
CmKebJsylQZ2uHlBmxc5ZQKBgQCu08Tr4NsguyhzV9BF2Abq9HJwCx0yZHEq3iMJ
cLdQRXcZPn3WOrtS9381hj7oo3H8GGbaJtqKbV/iJHcMKCdOxLrpo1z3ATxXNOft
65XAyGTS+kTBkVzfXzretaQ0Tgv4kUJ5cu51edp9l11MheKBoN46UX9DO52vb0rx
5T/mlQKBgEOmENryBSG5P+/m4dXB8g/XsZ/LuhfgzqeI3MfouyWUEQGgGp21idJN
9bzKCYAuizTKz7SWemxDsiIVJ+ZBLkbQF+NW2sMpY4H9nPhUebaL16uuXd6o/iJl
2ooUfyvWvJwk31SfDt6eddHSBQTv/zuz/iLIkCI4Ra0xKh5A3Z3w
-----END RSA PRIVATE KEY-----'''

PRIVATE_KEY = RSA.import_key(PRIVATE_KEY_PEM)

def generate_random_message(length=20):
    # Generate a random string of letters (you can adjust the length)
    letters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(letters) for _ in range(length))

def sign_message(message):
    # Hash the message
    h = SHA256.new(message.encode('utf-8'))
    
    # Sign the message
    signature = pkcs1_15.new(PRIVATE_KEY).sign(h)
    
    # Convert signature to hex
    signature_hex = binascii.hexlify(signature).decode('utf-8')
    
    return {'message': message, 'signature': signature_hex}

if __name__ == '__main__':
    num_messages = int(input("Enter the number of messages to generate and sign: "))
    
    messages_data = []
    
    # Generate and sign random messages
    for _ in range(num_messages):
        random_message = generate_random_message()  # Generate a random message
        signed_message = sign_message(random_message)
        messages_data.append(signed_message)
    
    # Store all messages and their signatures in sign.json
    with open('sign.json', 'w') as f:
        json.dump(messages_data, f, indent=4)
    
    print(f"{num_messages} random messages have been signed and stored in sign.json.")