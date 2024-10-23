from flask import Flask, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 1000}))
contract_address = Web3.to_checksum_address('0x7912870CA869a85e6108B0DFB033EA3D17D9b92c')  # Replace with your deployed contract address

# Load the contract ABI
with open('e-transcript/build/contracts/SchnorrBatchVerification.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Static variables for Schnorr proof
G = 2  # Generator (example)
P = 23  # Prime modulus (example)

@app.route('/', methods=['GET'])
def batch_ver_page():
    # Render the HTML form page for batch verification
    return render_template('batch_ver.html')

@app.route('/batch_verify', methods=['POST'])
def batch_verify():
    try:
        # Load the ACL data from acl.json
        with open('acl.json', 'r') as f:
            acl_data = json.load(f)['students']

        # Load the batch verification payload from batch_verification_payload.json
        with open('batch_verification_payload.json', 'r') as f:
            students_data = json.load(f)['students']

        # Start timing the batch verification process
        start_time = time.time()

        # List to store the batch tuples for Schnorr proof verification
        batch_proof_data = []

        # Loop through each student's data from the JSON file
        for student in students_data:
            secret = student['email'].strip().lower()  # Employer's unhashed email
            student_did = student['student_did']  # Student's DID (string format)

            # Get the corresponding ACL entry
            acl_entry = next((item for item in acl_data if item['student_did'] == student_did), None)

            if acl_entry is None or not acl_entry['isValid']:
                # Skip invalid or missing ACL entries
                continue

            # Get the employer's hashed email from acl.json
            hashed_email_bytes32 = Web3.to_bytes(hexstr=acl_entry['employer_hashed_email'])  # Convert hex string to bytes32

            # Generate Schnorr parameters
            r = random.randint(1, P - 1)  # Random nonce
            R = pow(G, r, P)  # R = g^r mod p
            challenge = contract.functions.getChallenge(R).call()  # Get challenge from blockchain
            hashed_secret = int(hashlib.sha256(secret.encode()).hexdigest(), 16) % P
            s = (r + challenge * hashed_secret) % (P - 1)  # Response

            # Create the proof data as a dictionary matching the SchnorrProof struct
            proof = {
                'R': R,
                's': s,
                'g': G,
                'p': P,
                'c': challenge,
                'employerHashedEmail': hashed_email_bytes32
            }

            # Add proof to the batch_proof_data list
            batch_proof_data.append(proof)

        # Send batch verification request to blockchain
        tx_hash = contract.functions.batchVerifySchnorrProof(batch_proof_data).transact({'from': w3.eth.accounts[7], 'gas': 200000000})

        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        # Calculate cumulative gas used
        gas_used = receipt['gasUsed']
        gas_price = w3.eth.gas_price  # Get current gas price from the blockchain
        cumulative_gas_cost = gas_used * gas_price  # Cumulative gas cost in Wei

        # Convert gas cost to Ether (or Gwei if needed)
        cumulative_gas_cost_in_ether = w3.from_wei(cumulative_gas_cost, 'ether')

        # Stop timing the batch verification
        end_time = time.time()
        verification_time = end_time - start_time

        # Check transaction status and return response with gas cost
        if receipt['status'] == 1:
            return jsonify({
                "status": "success",
                "message": "Batch Schnorr proofs verified successfully",
                "verification_time": verification_time,
                "gas_used": gas_used,
                "cumulative_gas_cost_in_ether": float(cumulative_gas_cost_in_ether)
            })
        else:
            return jsonify({"status": "failed", "message": "Batch verification failed"})

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
