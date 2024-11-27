from flask import Flask, jsonify, render_template, request, redirect, url_for
import hashlib
import qrcode
import json
from web3 import Web3
from datetime import datetime
from eth_utils import to_hex
from web3.exceptions import Web3RPCError
from dateutil import parser
import time
import os

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
account = "0x1E6792b7b75DD5ae09F5F18fF6F18dC8a67709fD"

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
    dt = parser.isoparse(iso_string)  # Parse ISO 8601 with timezone support
    return int(time.mktime(dt.timetuple()))  # Convert to Unix timestamp

# Helper function to convert HexBytes to hex strings
def convert_hexbytes_to_str(data):
    if isinstance(data, dict):
        return {k: convert_hexbytes_to_str(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_hexbytes_to_str(i) for i in data]
    elif isinstance(data, bytes):
        return to_hex(data)
    return data

# Updated load function for transcript and ACL data
def load_data(file_name):
    file_path = os.path.join(os.getcwd(), file_name)
    with open(file_path, 'r') as file:
        return json.load(file)

# Route to register the transcript using blockchain
@app.route('/register-transcript', methods=['GET'])
def register_transcript():
    # Load ACL data from acl.json
    acl_data = load_data('acl.json')

    # Fetch student ACL by DID (e.g., "did:university:student1")
    student_did = "did:university:student1"  # Replace with dynamic handling if necessary
    student_acl = next((student for student in acl_data["students"] if student["student_did"] == student_did), None)

    if not student_acl:
        return jsonify({"error": "Student not found in ACL"}), 404

    # Generate hashes for blockchain registration
    acl_hash = generate_hash(json.dumps(student_acl["selective_disclosure"]))
    vc_hash = generate_hash(student_did)
    expiration = student_acl["expiration"]

    # Convert hashes to bytes32 format
    acl_hash_bytes32 = str_to_bytes32(acl_hash)
    vc_hash_bytes32 = str_to_bytes32(vc_hash)

    # Call the smart contract to register the transcript
    tx_hash = contract.functions.registerTranscript(
        account,
        acl_hash_bytes32,
        vc_hash_bytes32,
        expiration
    ).transact()

    # Wait for the transaction receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    receipt_dict = convert_hexbytes_to_str(dict(receipt))

    return jsonify({"message": "Transcript registered", "transaction_receipt": receipt_dict})

@app.route('/generate-token', methods=['GET'])
def generate_token():
    # Load ACL data from acl.json
    acl_data = load_data('acl.json')

    # Fetch the specific student's ACL entry (e.g., student DID is "did:university:student1")
    student_did = "did:university:student1"  # Replace with dynamic handling if necessary
    student_acl = next((student for student in acl_data["students"] if student["student_did"] == student_did), None)

    if not student_acl:
        return jsonify({"error": "Student ACL not found"}), 404

    # Generate hash values for various fields
    vc_hash = generate_hash(student_did)
    acl_hash = generate_hash(json.dumps(student_acl["selective_disclosure"]))
    employer_hash = student_acl["employer_hashed_email"]
    validity = student_acl["expiration"]

    # Token data to include in the QR code
    token_data = {
        "student_did": student_did,
        "acl_hash": acl_hash,
        "vc_hash": vc_hash,
        "validity": validity,
        "employer_hash": employer_hash
    }

    token = json.dumps(token_data)

    # Generate the URL to input-credentials endpoint with the token data
    credentials_url = f"http://192.168.1.154:5000/input-credentials?token={token}"

    # Generate QR code from the URL with the token
    qr = qrcode.make(credentials_url)
    
    # Save the QR code in the static folder so it can be served
    qr_code_path = 'static/token_qr.png'
    qr.save(qr_code_path)

    # Provide the path to the QR code image for display
    return jsonify({"message": "QR code generated", "credentials_url": f'/{qr_code_path}'})


@app.route('/input-credentials', methods=['GET', 'POST'])
def input_credentials():
    token_json = request.args.get('token')
    
    if request.method == 'POST':
        employer_input_hash = request.form.get('email')

        # Parse the token data
        token_data = json.loads(token_json)

        employer_input_hash = generate_hash(employer_input_hash)

        # Compare the provided values with the hashes in the token
        if employer_input_hash == token_data.get('employer_hash', ''):
            # Redirect to verify token if the hash matches
            return redirect(url_for('verify_token', token=token_json))
        else:
            return jsonify({"message": "Employer attribute or email does not match"}), 403

    # Display the form for inputting credentials
    return '''
    <form method="POST">
        <label for="email">Email:</label><br>
        <input type="email" id="email" name="email"><br>
        <input type="hidden" name="token" value="{{ token }}">
        <input type="submit" value="Submit">
    </form>
    '''

# Route to verify the transcript using blockchain
@app.route('/verify-token', methods=['GET'])
def verify_token():
    token_json = request.args.get('token')

    # Parse the token data
    token_data = json.loads(token_json)

    acl_hash = str_to_bytes32(token_data['acl_hash'])
    vc_hash = str_to_bytes32(token_data['vc_hash'])

    student_did = token_data.get('student_did')  # Assume student DID is part of the token
    if not student_did:
        return jsonify({"message": "Missing student DID in token"}), 400

    try:
        # Call the smart contract to verify the transcript
        verified = contract.functions.verifyTranscript(account, acl_hash, vc_hash).call()

        if verified:
            # Load ACL data from acl.json
            acl_data = load_data('acl.json')
            student_acl = next((student for student in acl_data["students"] if student["student_did"] == student_did), None)

            if not student_acl:
                return jsonify({"message": "Student ACL not found"}), 404

            # Fetch selective disclosure fields
            selective_disclosure = student_acl.get("selective_disclosure", [])

            # Load transcript data from transcript.json
            transcript_index = "1"  # Replace with dynamic logic if necessary
            transcript_data = load_data('transcript.json')

            # Ensure transcript exists for that index
            if transcript_index not in transcript_data:
                return jsonify({"message": "Transcript not found for index"}), 404

            transcript = transcript_data[transcript_index]

            # Mask sensitive fields based on ACL
            for field in selective_disclosure:
                if field in transcript:
                    transcript[field] = "******"

            # Render the e-transcript template with the masked information
            return render_template('e_transcript.html', transcript=transcript)
        else:
            return render_template('result.html', message="Verification failed")

    except Exception as e:
        print(f"Error during verification: {e}")
        return render_template('result.html', message="Verification failed")

if __name__ == '__main__':
    app.run(host='192.168.1.154', port=5000, debug=True)  # Replace with your actual local IP