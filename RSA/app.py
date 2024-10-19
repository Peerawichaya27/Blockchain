from flask import Flask, request, jsonify, render_template
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import binascii
import time
from web3 import Web3
import json

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract_address = Web3.to_checksum_address('0xE673B2E9242200708c88070f5940e8434830175F')

# Load contract ABI
with open('e-transcript/build/contracts/RSAVerification.json') as f:
    contract_abi = json.load(f)['abi']
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Store the RSA keys
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
PUBLIC_KEY_PEM = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAq1U2sopY+ktpsV/stESi
cL+G5eU0j9c4zOxyGUVUbM3N/69CfmMrjG9Y57Jpuq6QXYXvg+sPNOs71Wo7JdZt
oTTpk6z89hzg6ZgT0583oxEyPZNbh657YTLNuQJayPm2LTXmbVERa884eLO/Ifvp
seRLQSXkOu+9cYaT6gtmZprf+9mRlotejLxRJvZuiCcuwVlNssM1v/nvPdN5jS1j
GrwOGgXAQyouHbO9n1Sc5zJSeJrhFu7JCeIsvcCZQrUQqM5/hYPinbHsyKSDJ3ww
y8yVnfQ9xkG0bKL942QedmN7fUuyNtGWmC8Xp21dQqdgSlz7f5T+XKm/D2qoywyJ
kQIDAQAB
-----END PUBLIC KEY-----'''

PRIVATE_KEY = RSA.import_key(PRIVATE_KEY_PEM)
PUBLIC_KEY = RSA.import_key(PUBLIC_KEY_PEM)

# Route to store the public key on blockchain
@app.route('/store_public_key', methods=['POST'])
def store_public_key():
    employer_address = request.form.get('employer_address')
    public_key = binascii.hexlify(PUBLIC_KEY.export_key(format='DER')).decode('utf-8')
    
    tx_hash = contract.functions.storePublicKey(
        Web3.to_checksum_address(employer_address),
        bytes.fromhex(public_key)
    ).transact({'from': w3.eth.accounts[0]})

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return f"Public key stored with receipt: {receipt}"

@app.route('/store_public_key_form', methods=['GET'])
def store_public_key_form():
    return render_template('store_public_key.html')


# Route to sign a message using the private key
@app.route('/sign_message', methods=['POST'])
def sign_message():
    message = request.form.get('message')
    if not message:
        return jsonify({'error': 'Message is required'}), 400

    h = SHA256.new(message.encode('utf-8'))
    signature = pkcs1_15.new(PRIVATE_KEY).sign(h)
    signature_hex = binascii.hexlify(signature).decode('utf-8')

    return jsonify({
        'message': message,
        'signature': signature_hex
    })

@app.route('/verify', methods=['GET'])
def verify_page():
    return render_template('verify.html')

@app.route('/verify_signature', methods=['POST'])
def verify_signature():
    message = request.form.get('message')
    signature_hex = request.form.get('signature')
    employer_address = request.form.get('employer_address')

    # Debugging: Print out the values to check if they are correctly received
    print(f"Received message: {message}")
    print(f"Received signature: {signature_hex}")
    print(f"Received employer address: {employer_address}")

    # Check for missing input values
    if not message or not signature_hex or not employer_address:
        print("Missing required input values")
        return jsonify({'error': 'Message, signature, and employer address are required'}), 400

    # Convert the signature from hex
    try:
        signature = binascii.unhexlify(signature_hex)
    except binascii.Error as e:
        print(f"Error converting signature: {e}")
        return jsonify({'error': 'Invalid signature format'}), 400

    # Hash the message and convert it to bytes32
    h = SHA256.new(message.encode('utf-8'))
    hashed_message = Web3.to_bytes(hexstr=h.hexdigest())[:32]  # Ensure it's a 32-byte value

    start_time = time.time()

    try:
        # Call blockchain to verify the signature
        tx_hash = contract.functions.verifySignature(
            hashed_message,
            bytes(signature),
            Web3.to_checksum_address(employer_address)
        ).transact({'from': w3.eth.accounts[0]})
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        verification_time = time.time() - start_time

        if receipt['status'] == 1:
            return jsonify({
                'status': 'success',
                'message': 'Signature verified on blockchain',
                'verification_time': verification_time
            })
        else:
            return jsonify({'status': 'failed', 'message': 'Signature verification failed'}), 400

    except Exception as e:
        print(f"Error during signature verification: {e}")
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)
