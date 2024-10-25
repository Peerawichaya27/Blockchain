from flask import Flask, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 500}))
contract_address = Web3.to_checksum_address('0x958bfbA300587F4F4A379bDd47361Df39A4F5083')  # Replace with your deployed contract address

# Load the contract ABI
with open('e-transcript/build/contracts/SchnorrSingleVerification.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

@app.route('/', methods=['GET'])
def batch_ver_page():
    return render_template('batch_ver.html')

@app.route('/batch_verify', methods=['POST'])
def batch_verify():
    try:
        # Load data from ACL and verification payload files
        with open('acl.json', 'r') as f:
            acl_data = json.load(f)['students']

        with open('batch_verification_payload.json', 'r') as f:
            students_data = json.load(f)['students']

        # Retrieve G and P constants only once
        G = contract.functions.G().call()
        P = contract.functions.P().call()
        cumulative_gas_used = 0
        verification_results = []

        # Check if precomputed g^hashed_email mod p is already set
        if acl_data:
            first_student = acl_data[0]
            try:
                employer_hashed_email = int(first_student['employer_hashed_email'], 16)
                if contract.functions.precomputedGHashedEmail().call() == 0:
                    tx_hash = contract.functions.setPrecomputedGHashedEmail(employer_hashed_email).transact({'from': w3.eth.accounts[1]})
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    cumulative_gas_used += receipt['gasUsed']
            except ValueError:
                return jsonify({"status": "failed", "message": "Invalid hashed email format."})

        # Start timing the batch verification process
        start_time = time.time()

        # Process each student's proof
        for student in students_data:
            secret = student['email'].strip().lower()  # Employer's unhashed email
            student_did = student['student_did']  # Student's DID

            # Get corresponding ACL entry
            acl_entry = next((item for item in acl_data if item['student_did'] == student_did), None)
            if acl_entry is None or not acl_entry['isValid']:
                verification_results.append({'student_did': student_did, 'result': 'Invalid or missing ACL entry'})
                continue

            # Hash the secret
            hashed_secret = int(hashlib.sha256(secret.encode()).hexdigest(), 16) % P

            # Generate Schnorr parameters
            r = random.randint(1, P - 1)
            R = pow(G, r, P)

            # Get challenge using on-chain function
            challenge = contract.functions.getChallenge(R).call()
            s = (r + challenge * hashed_secret) % (P - 1)

            # Create proof to match the contract
            proof = {
                'R': R,
                's': s,
                'c': challenge
            }

            try:
                # Verify proof on-chain
                tx_hash = contract.functions.verifySchnorrProof(proof).transact({'from': w3.eth.accounts[1]})
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

                # Append results
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

        # Stop timing the batch verification
        verification_time = time.time() - start_time

        # Return results as a JSON response
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
