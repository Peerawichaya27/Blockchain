from flask import Flask, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 1000}))
contract_address = Web3.to_checksum_address('0x79D97E5ea5C75BAAaF6CF7EE668a5E80Bc43cf91')  # Replace with your deployed contract address

# Load the contract ABI
with open('e-transcript/build/contracts/SchnorrSingleVerification.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Constants for Schnorr proof
G = 2  # Generator
P = 23  # Prime modulus

@app.route('/', methods=['GET'])
def batch_ver_page():
    return render_template('batch_ver.html')

@app.route('/batch_verify', methods=['POST'])
def batch_verify():
    try:
        # Load ACL and verification data
        with open('acl.json', 'r') as f:
            acl_data = json.load(f)['students']

        with open('batch_verification_payload.json', 'r') as f:
            students_data = json.load(f)['students']

        # Check and set precomputed value if not set
        precomputed_value = contract.functions.precomputedGHashedEmail().call()
        cumulative_gas_used = 0
        if precomputed_value == 0 and acl_data:
            first_student = acl_data[0]
            try:
                # Convert employer_hashed_email to integer format
                employer_hashed_email = int(first_student['employer_hashed_email'], 16)
                # Set precomputed value on-chain
                tx_hash = contract.functions.setPrecomputedGHashedEmail(employer_hashed_email).transact({'from': w3.eth.accounts[2]})
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                cumulative_gas_used += receipt['gasUsed']
            except ValueError:
                return jsonify({"status": "failed", "message": "Invalid hashed email format."})

        # Batch processing start
        start_time = time.time()
        verification_results = []

        # Verification loop
        for student in students_data:
            secret = student['email'].strip().lower()
            student_did = student['student_did']
            acl_entry = next((item for item in acl_data if item['student_did'] == student_did), None)
            if acl_entry is None or not acl_entry['isValid']:
                verification_results.append({'student_did': student_did, 'result': 'Invalid or missing ACL entry'})
                continue

            hashed_secret = int(hashlib.sha256(secret.encode()).hexdigest(), 16) % P
            r = random.randint(1, P - 1)
            R = pow(G, r, P)
            challenge = contract.functions.getChallenge(R).call()
            s = (r + challenge * hashed_secret) % (P - 1)

            # Define the proof structure
            proof = {
                'R': R,
                's': s,
                'c': challenge
            }

            try:
                # Verify Schnorr proof on-chain
                tx_hash = contract.functions.verifySchnorrProof(proof).transact({'from': w3.eth.accounts[2]})
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                verification_results.append({
                    'student_did': student_did,
                    'result': 'Valid',
                    'gas_used': receipt['gasUsed']
                })
                cumulative_gas_used += receipt['gasUsed']
            except Exception as e:
                verification_results.append({
                    'student_did': student_did,
                    'result': f"verification failed: {str(e)}"
                })

        # End timing for batch verification
        verification_time = time.time() - start_time

        return jsonify({
            "status": "success",
            "message": "Schnorr proofs verified",
            "verification_time": verification_time,
            "cumulative_gas_used": cumulative_gas_used,
            "verification_results": verification_results
        })

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
