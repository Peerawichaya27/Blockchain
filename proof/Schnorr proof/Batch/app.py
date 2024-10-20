from flask import Flask, request, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 1000}))
contract_address = Web3.to_checksum_address('0x03fc68eE75689B7C395ace8CB16BD5aA39246FE6')  # Replace with your deployed contract address

# Load the contract ABI
with open('e-transcript/build/contracts/SchnorrBatchVerification.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Static variables for Schnorr proof
G = 2  # Generator (example)
P = 23 # Prime modulus (example)

@app.route('/batch_ver_page', methods=['GET'])
def batch_ver_page():
    # Render the HTML form page for storing ACL
    return render_template('batch_ver.html')

@app.route('/batch_verify_json', methods=['POST'])
def batch_verify_from_json():
    try:
        # Load the ACL data from acl.json
        with open('acl.json', 'r') as f:
            acl_data = json.load(f)['students']

        # Load the batch verification payload from batch_verification_payload.json
        with open('batch_verification_payload.json', 'r') as f:
            students_data = json.load(f)['students']

        # Start timing the batch verification process
        start_time = time.time()

        # Arrays to store batch data
        R_batch = []
        s_batch = []
        g_batch = []
        p_batch = []
        c_batch = []
        students_batch = []
        employer_hashed_emails_batch = []

        # Loop through each student's data from the JSON file
        for i, student in enumerate(students_data):
            secret = student['email'].strip().lower()  # Employer's unhashed email
            student_did = student['student_did']  # Student's DID (string format)
            
            # Get the corresponding ACL entry
            acl_entry = acl_data[i]  # Use matching index to get ACL entry
            acl_hashed_email = acl_entry['employer_hashed_email']  # Hashed email from ACL
            
            # Hash the employer's email (secret)
            hashed_email = hashlib.sha256(secret.encode()).hexdigest()

            # Generate Schnorr parameters
            r = random.randint(1, P-1)  # Random nonce
            R = pow(G, r, P)  # R = g^r mod p
            challenge = contract.functions.getChallenge(R).call()  # Get challenge from blockchain
            hashed_secret = int(hashlib.sha256(secret.encode()).hexdigest(), 16) % P
            s = (r + challenge * hashed_secret) % (P-1)  # Response

            # Add to batch arrays
            R_batch.append(R)
            s_batch.append(s)
            g_batch.append(G)
            p_batch.append(P)
            c_batch.append(challenge)
            students_batch.append(student_did)
            employer_hashed_emails_batch.append(hashed_email)

        # Ensure students_batch and emails are in string array format
        students_batch = [str(student) for student in students_batch]
        employer_hashed_emails_batch = [str(email) for email in employer_hashed_emails_batch]

        # Send batch verification request to blockchain (without acl_hashed_emails_batch)
        tx_hash = contract.functions.batchVerifySchnorrProof(
            R_batch, s_batch, g_batch, p_batch, c_batch, students_batch, employer_hashed_emails_batch
        ).transact({'from': w3.eth.accounts[0], 'gas': 2000000000})

        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        # Stop timing the batch verification
        end_time = time.time()
        verification_time = end_time - start_time

        # Check transaction status and return response
        if receipt['status'] == 1:
            return jsonify({
                "status": "success",
                "message": "Batch Schnorr proofs verified successfully",
                "verification_time": verification_time
            })
        else:
            return jsonify({"status": "failed", "message": "Batch verification failed"})

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
