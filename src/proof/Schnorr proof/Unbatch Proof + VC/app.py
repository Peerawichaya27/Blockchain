from flask import Flask, request, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 500}))
contract_address = Web3.to_checksum_address('0x87E42c7c7c8f6f5a5B51BcE3D3cAb5C9AfE68469')  # Replace with your deployed contract address

# Load the contract ABI
with open('e-transcript/build/contracts/SchnorrBatchVerification.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Static variables for Schnorr proof
G = 2  # Generator (example)
P = 23  # Prime modulus (example)
proof_verified = False  # To store the state of Schnorr proof verification

@app.route('/', methods=['GET'])
def batch_ver_page():
    # Render the HTML form page for batch verification
    return render_template('batch_ver.html')

@app.route('/store', methods=['GET'])
def store_did_page():
    # Render the HTML form page for batch verification
    return render_template('store_did.html')

@app.route('/store_did_to_index', methods=['POST'])
def store_did_to_index():
    try:
        # Load the ipfs.json file to get DID and index information
        with open('ipfs.json', 'r') as f:
            ipfs_data = json.load(f)

        # Loop through each student's DID and index
        for index, student_data in ipfs_data.items():
            student_did = student_data['student_did']
            student_index = int(index)  # Convert index from string to integer

            # Call the smart contract function to store DID and index
            tx_hash = contract.functions.storeDidToIndex(student_did, student_index).transact({
                'from': w3.eth.accounts[2], 'gas': 20000000
            })
            # Wait for the transaction to be mined
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Stored DID: {student_did} with index: {student_index} on the blockchain")

        return jsonify({
            "status": "success",
            "message": "All DIDs and indices have been stored on the blockchain"
        })

    except Exception as e:
        return jsonify({
            "status": "failed",
            "message": str(e)
        })

@app.route('/batch_verify_json', methods=['POST'])
def batch_verify_from_json():
    global proof_verified  # Mark this as global to track it across requests
    try:
        # Load the necessary data
        with open('batch_verification_payload.json', 'r') as f:
            students_data = json.load(f)['students']

        with open('token.json', 'r') as f:
            token_data = json.load(f)

        with open('ipfs.json', 'r') as f:
            ipfs_data = json.load(f)

        valid_students = []
        start_time = time.time()

        for student in students_data:
            student_did = student['student_did']
            student_index = contract.functions.getIndexByDid(student_did).call()
            ipfs_vc = ipfs_data[str(student_index)]['hashed_vc']

            if not proof_verified:
                # First-time verification, perform Schnorr proof and VC verification
                hashed_email = hashlib.sha256(student['email'].encode()).hexdigest()
                r = random.randint(1, P-1)
                R = pow(G, r, P)
                challenge = contract.functions.getChallenge(R).call()
                hashed_secret = int(hashlib.sha256(student['email'].encode()).hexdigest(), 16) % P
                s = (r + challenge * hashed_secret) % (P-1)

                # Call unified verification on blockchain (includes Schnorr and VC verification)
                tx_hash = contract.functions.verify(
                    R, s, G, P, challenge, hashed_email, token_data[str(student_index)]['verifiablePresentation']['verifiableCredential'][0]['hash'], student_did, ipfs_vc
                ).transact({'from': w3.eth.accounts[2], 'gas': 20000000})
                
                proof_verified = True  # Mark proofVerified as True after the first Schnorr verification

            else:
                # Skip Schnorr, only verify the hashed VC
                tx_hash = contract.functions.verifyHashedVC(
                    token_data[str(student_index)]['verifiablePresentation']['verifiableCredential'][0]['hash'], student_did, ipfs_vc
                ).transact({'from': w3.eth.accounts[2], 'gas': 20000000})

            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt['status'] == 1:
                valid_students.append({
                    "student_did": student_did,
                    "status": "verified and VC valid"
                })

        verification_time = time.time() - start_time

        return jsonify({
            "status": "success",
            "valid_students": valid_students,
            "verification_time": verification_time
        })

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
