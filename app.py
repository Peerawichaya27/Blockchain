from flask import Flask, jsonify, render_template
import hashlib
import qrcode
import json
from web3 import Web3
from datetime import datetime
from eth_utils import to_hex
from web3.exceptions import Web3RPCError

app = Flask(__name__)

# Load contract ABI and address from the JSON file
with open('ETranscript_abi.json', 'r') as file:
    contract_data = json.load(file)

contract_address = contract_data['address']
contract_abi = contract_data['abi']

# Connect to local blockchain (e.g., Ganache)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

# Create contract instance
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Set the default account for transactions
account = "0xa04c19F2A7FDD4dD94489b31364C088DbDcd684D"

w3.eth.default_account = account  # Ensure you use a funded account from Ganache

# Helper function to generate a SHA256 hash
def generate_hash(data):
    return hashlib.sha256(data.encode()).hexdigest()

# Helper function to convert a hex string (hash) to bytes32
def str_to_bytes32(input_str):
    # Remove the "0x" from the hex string if present and convert to bytes
    return bytes.fromhex(input_str.replace('0x', '')).rjust(32, b'\0')

# Helper function to convert ISO 8601 date string to Unix timestamp
def iso_to_unix_time(iso_string):
    dt = datetime.strptime(iso_string, "%Y-%m-%dT%H:%M:%S")
    return int(dt.timestamp())

# Helper function to convert HexBytes to hex strings
def convert_hexbytes_to_str(data):
    if isinstance(data, dict):
        return {k: convert_hexbytes_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_hexbytes_to_str(i) for i in data]
    elif isinstance(data, bytes):
        return to_hex(data)
    return data

# Route to register the transcript using blockchain
@app.route('/register-transcript', methods=['GET'])
def register_transcript():
    # Load payload from the data.json file
    with open('data.json', 'r') as file:
        data = json.load(file)

    student_id = data['student_id']
    acl = data['acl']
    
    # Convert ISO 8601 validity date to Unix timestamp
    expiration = iso_to_unix_time(data['validity'])
    
    # Generate hash of the student ID and ACL
    vc_hash = generate_hash(student_id)
    acl_hash = generate_hash(json.dumps(acl))

    # Convert the hashes to bytes32 format
    vc_hash_bytes32 = str_to_bytes32(vc_hash)
    acl_hash_bytes32 = str_to_bytes32(acl_hash)

    # Call the smart contract to register the transcript
    tx_hash = contract.functions.registerTranscript(
        account,  # Specify the account
        acl_hash_bytes32,
        vc_hash_bytes32,
        expiration
    ).transact()

    # Wait for the transaction receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Convert HexBytes fields in the transaction receipt to strings
    receipt_dict = convert_hexbytes_to_str(dict(receipt))

    return jsonify({"message": "Transcript registered", "transaction_receipt": receipt_dict})

# Route to generate token and QR code from JSON payload
@app.route('/generate-token', methods=['GET'])
def generate_token():
    # Load payload from the data.json file
    with open('data.json', 'r') as file:
        data = json.load(file)

    student_id = data['student_id']
    acl = data['acl']
    
    # Generate hash of the student ID and ACL
    vc_hash = generate_hash(student_id)
    acl_hash = generate_hash(json.dumps(acl))

    # Token data to include in the QR code
    token_data = {
        "acl_hash": acl_hash,
        "vc_hash": vc_hash,
        "validity": data['validity'],
        "employer_attribute": data['employer_attribute']
    }

    # Generate QR code from the token data
    token_json = json.dumps(token_data)
    qr = qrcode.make(token_json)
    qr.save("token_qr.png")

    return jsonify({"message": "QR code generated", "token": token_json})

# Route to verify the transcript using blockchain
@app.route('/verify-token', methods=['GET'])
def verify_token():
    # Load the verification data from verify_data.json
    with open('verify_data.json', 'r') as file:
        data = json.load(file)

    student_address = data['student_address']
    
    try:
        acl_hash = str_to_bytes32(data['acl_hash'])  # Convert to bytes32
        vc_hash = str_to_bytes32(data['vc_hash'])    # Convert to bytes32
    except ValueError as e:
        return render_template('result.html', message=str(e))

    try:
        # Call the smart contract to verify the transcript
        verified = contract.functions.verifyTranscript(student_address, acl_hash, vc_hash).call()

        if verified:
            return render_template('result.html', message="Transcript verified")
        else:
            return render_template('result.html', message="Verification failed")
    except Web3RPCError as e:
        # Handle the blockchain error and return a user-friendly message
        return render_template('result.html', message="Verification failed")

if __name__ == '__main__':
    app.run(debug=True)
