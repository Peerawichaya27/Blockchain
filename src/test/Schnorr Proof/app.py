from flask import Flask, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 1000}))
contract_address = Web3.to_checksum_address('0x9D31c15bd9c44F4D0a1FB91e84235FD106Db70C1')  # Replace with your deployed contract address

# Load the contract ABI
with open('e-transcript/build/contracts/SchnorrSingleVerification.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Static variables for Schnorr proof
G = 2  # Generator
P = 23  # Prime modulus

@app.route('/', methods=['GET'])
def batch_ver_page():
    # Render the HTML form page for batch verification
    return render_template('batch_ver.html')

@app.route('/batch_verify', methods=['POST'])
def batch_verify():
    try:
        # Load data
        with open('acl.json', 'r') as f:
            acl_data = json.load(f)['students']

        with open('batch_verification_payload.json', 'r') as f:
            students_data = json.load(f)['students']

        # Start timing the batch verification process
        start_time = time.time()

        # List to store the verification results
        verification_results = []
        cumulative_gas_used = 0  # Variable to track cumulative gas used

        # Loop through each student's data
        for student in students_data:
            secret = student['email'].strip().lower()  # Employer's unhashed email
            student_did = student['student_did']  # Student's DID

            # Get the corresponding ACL entry
            acl_entry = next((item for item in acl_data if item['student_did'] == student_did), None)

            if acl_entry is None or not acl_entry['isValid']:
                # Skip invalid or missing ACL entries
                verification_results.append({
                    'student_did': student_did,
                    'result': 'Invalid or missing ACL entry'
                })
                continue

            try:
                # Convert the employer_hashed_email from ACL (hex string to int)
                employer_hashed_email = int(acl_entry['employer_hashed_email'], 16)  # Hex to int conversion
            except ValueError:
                # If the employer_hashed_email is not a valid hex, log it
                verification_results.append({
                    'student_did': student_did,
                    'result': 'Invalid'
                })
                continue

            # Hash the secret (email from batch_verification_payload.json)
            hashed_secret = int(hashlib.sha256(secret.encode()).hexdigest(), 16) % P
            employer_hashed_email = employer_hashed_email % P  # Ensure it's modded by P

            # Generate Schnorr parameters
            r = random.randint(1, P - 1)  # Random nonce
            R = pow(G, r, P)  # R = g^r mod p

            challenge = contract.functions.getChallenge(R).call()  # Get challenge from blockchain
            s = (r + challenge * hashed_secret) % (P - 1)  # Response

            # Create the proof data
            proof = {
                'R': R,
                's': s,
                'g': G,
                'p': P,
                'c': challenge,
                'employerHashedEmail': employer_hashed_email  # Use employer_hashed_email from ACL
            }

            try:
                # Send each proof verification request to the smart contract one by one
                tx_hash = contract.functions.verifySchnorrProof(proof).transact({'from': w3.eth.accounts[0]})
                receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

                # Get the gas used by the transaction
                gas_used = receipt['gasUsed']
                cumulative_gas_used += gas_used  # Add to cumulative gas

                # Append the result (True/False) to the verification_results list
                verification_results.append({
                    'student_did': student_did,
                    'result': 'Valid',  # Assuming successful verification
                    'gas_used': gas_used  # Gas used for this proof
                })
            except Exception as e:
                # Log any error that happens during the smart contract call
                verification_results.append({
                    'student_did': student_did,
                    'result': f"verification failed: {str(e)}"
                })

        # Stop timing the batch verification
        verification_time = time.time() - start_time

        # Return the results as a JSON response
        return jsonify({
            "status": "success",
            "message": "Schnorr proofs verified",
            "verification_time": verification_time,
            "cumulative_gas_used": cumulative_gas_used,  # Return the cumulative gas used
            "verification_results": verification_results
        })

    except Exception as e:
        # Return the error message
        return jsonify({"status": "failed", "message": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
