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
import requests

app = Flask(__name__)

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 500}))

contract_address = Web3.to_checksum_address('0xa4aDa32c554cd3C83B33d51565Fd95752bCd6D97')

with open('e-transcript/build/contracts/UniversityCredential.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Set the default account for transactions
account = "0xe2ec799087F8B5D61568e606c57CCD145a4003bA"

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
    try:
        # Load ACL data from acl.json
        acl_data = load_data('acl.json')
        print("Loaded ACL Data:", acl_data)

        # Fetch the student's ACL entry
        student_did = "did:university:student1"
        student_acl = next((student for student in acl_data["students"] if student["student_did"] == student_did), None)
        print("Student ACL Entry:", student_acl)

        if not student_acl:
            return jsonify({"error": "Student ACL not found"}), 404

        # Generate hashes
        acl_hash = generate_hash(json.dumps(student_acl["selective_disclosure"]))
        vc_hash = generate_hash(student_did)
        expiration = student_acl["expiration"]
        print("ACL Hash:", acl_hash)
        print("VC Hash:", vc_hash)

        # Call the smart contract
        tx_hash = contract.functions.registerTranscript(
            account, str_to_bytes32(acl_hash), str_to_bytes32(vc_hash), expiration
        ).transact()
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print("Transaction Receipt:", receipt)

        return jsonify({"message": "Transcript registered successfully"})
    except Exception as e:
        print(f"Error during transcript registration: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/generate-token', methods=['GET'])
def generate_token():
    try:
        # Load ACL data
        acl_data = load_data('acl.json')
        print("Loaded ACL Data:", acl_data)

        # Fetch the specific student's ACL entry
        student_did = "did:university:student1"
        student_acl = next((student for student in acl_data["students"] if student["student_did"] == student_did), None)
        print("Fetched Student ACL:", student_acl)

        if not student_acl:
            return jsonify({"error": "Student ACL not found"}), 404

        # Generate hashes
        vc_hash = generate_hash(student_did)
        acl_hash = generate_hash(json.dumps(student_acl["selective_disclosure"]))
        employer_hash = student_acl["employer_hashed_email"]
        validity = student_acl["expiration"]

        # Load token.json to fetch hashed_vc_from_vp
        token_data = load_data('token.json')
        hashed_vc_from_vp = token_data["1"]["verifiablePresentation"]["verifiableCredential"][0]["hash"]
        print("Hashed VC from VP (Token.json):", hashed_vc_from_vp)

        # Load IPFS hashed VC
        ipfs_data = load_data('ipfs.json')
        print("Loaded IPFS Data:", ipfs_data)

        # Search for the student's hashed VC by DID
        ipfs_hashed_vc = None
        for entry in ipfs_data.values():
            if entry.get("student_did") == student_did:
                ipfs_hashed_vc = entry.get("hashed_vc")
                break

        print("IPFS Hashed VC:", ipfs_hashed_vc)

        if not ipfs_hashed_vc:
            return jsonify({"error": "IPFS hashed VC not found for the student"}), 404

        # Create token
        token_data = {
            "student_did": student_did,
            "acl_hash": acl_hash,
            "vc_hash": vc_hash,
            "validity": validity,
            "employer_hash": employer_hash,
            "ipfs_hashed_vc": ipfs_hashed_vc,
            "hashed_vc_from_vp": hashed_vc_from_vp
        }
        print("Generated Token Data:", token_data)

        # Generate QR code
        token = json.dumps(token_data)
        credentials_url = f"http://192.168.1.154:5000/input-credentials?token={token}"
        qr = qrcode.make(credentials_url)
        qr_code_path = 'static/token_qr.png'
        qr.save(qr_code_path)

        return jsonify({"message": "QR code generated", "credentials_url": f'/{qr_code_path}'})
    except Exception as e:
        print(f"Error during token generation: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/input-credentials', methods=['GET', 'POST'])
def input_credentials():
    token_json = request.args.get('token')

    if request.method == 'POST':
        employer_email = request.form.get('email')  # Get employer's email
        print(f"Received Employer Email: {employer_email}")

        # Parse the token data
        token_data = json.loads(token_json)
        print(f"Parsed Token Data: {token_data}")

        # Compute hash of the input email
        input_email_hash = generate_hash(employer_email)
        print(f"Input Email Hash: {input_email_hash}")
        print(f"Expected Email Hash: {token_data.get('employer_hash')}")

        # Compare input hash with token's employer_hash
        if input_email_hash != token_data.get('employer_hash'):
            return jsonify({"message": "Employer email does not match the expected hash"}), 403

        # Send data to app.py for Schnorr proof and VC verification
        app_py_url = "http://127.0.0.1:5000/batch_verify_json"
        payload = {
            "email": employer_email,
            "token": token_data
        }
        print(f"Payload for app.py: {payload}")

        try:
            # Forward the request to app.py for verification
            response = requests.post(app_py_url, json=payload)

            if response.status_code == 200:
                verification_result = response.json()
                print(f"Response from app.py: {verification_result}")

                if verification_result.get("status") == "success":
                    # Redirect to verify-token in uni.py after successful verification
                    return redirect(url_for('verify_token', token=token_json))
                else:
                    return jsonify({"message": "Verification failed in app.py"}), 403
            else:
                return jsonify({"message": "Error during VC verification in app.py"}), 500

        except Exception as e:
            return jsonify({"message": f"Error communicating with app.py: {str(e)}"}), 500

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
    print("Received Token for Verification:", token_json)

    # Parse the token data
    token_data = json.loads(token_json)

    acl_hash = str_to_bytes32(token_data['acl_hash'])
    vc_hash = str_to_bytes32(token_data['vc_hash'])

    print("Parsed ACL Hash:", acl_hash)
    print("Parsed VC Hash:", vc_hash)

    student_did = token_data.get('student_did')  # Assume student DID is part of the token
    if not student_did:
        return jsonify({"message": "Missing student DID in token"}), 400

    try:
        # Call the smart contract to verify the transcript
        verified = contract.functions.verifyTranscript(account, acl_hash, vc_hash).call()
        print("Smart Contract Verification Result:", verified)

        if verified:
            # Load ACL data from acl.json
            acl_data = load_data('acl.json')
            print("Loaded ACL Data:", acl_data)
            
            student_acl = next((student for student in acl_data["students"] if student["student_did"] == token_data['student_did']), None)
            print("Student ACL Entry:", student_acl)

            if not student_acl:
                return jsonify({"message": "Student ACL not found"}), 404

            # Fetch selective disclosure fields
            selective_disclosure = student_acl.get("selective_disclosure", [])

            # Load transcript data from transcript.json
            transcript_index = "1"  # Replace with dynamic logic if necessary
            transcript_data = load_data('transcript.json')
            print("Loaded Transcript Data:", transcript_data)

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