from flask import Flask, request, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 500}))
contract_address = Web3.to_checksum_address('0x86F78E10E05162b87F59fD6fcF96F986D1fbF125')  # Replace with your deployed contract address

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
    # Render the HTML form page for storing DIDs
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
        total_gas_used_schnorr = 0
        total_gas_used_vc = 0

        for student in students_data:
            student_did = student['student_did']
            student_index = contract.functions.getIndexByDid(student_did).call()
            ipfs_vc = ipfs_data[str(student_index)]['hashed_vc']

            # Perform Schnorr proof verification
            hashed_email = hashlib.sha256(student['email'].encode()).hexdigest()
            r = random.randint(1, 22)
            R = pow(2, r, 23)
            challenge = contract.functions.getChallenge(R).call()
            hashed_secret = int(hashlib.sha256(student['email'].encode()).hexdigest(), 16) % 23
            s = (r + challenge * hashed_secret) % 22

            # Gas used for Schnorr proof verification
            tx_hash_schnorr = contract.functions.verifySchnorrProof(
                R, s, 2, 23, challenge, hashed_email, student_did
            ).transact({'from': w3.eth.accounts[5], 'gas': 20000000})
            
            receipt_schnorr = w3.eth.wait_for_transaction_receipt(tx_hash_schnorr)
            schnorr_gas_used = receipt_schnorr['gasUsed']
            total_gas_used_schnorr += schnorr_gas_used

            # Perform VC verification
            tx_hash_vc = contract.functions.verifyHashedVC(
                token_data[str(student_index)]['verifiablePresentation']['verifiableCredential'][0]['hash'],
                student_did,
                ipfs_vc
            ).transact({'from': w3.eth.accounts[5], 'gas': 20000000})

            receipt_vc = w3.eth.wait_for_transaction_receipt(tx_hash_vc)
            vc_gas_used = receipt_vc['gasUsed']
            total_gas_used_vc += vc_gas_used

            if receipt_vc['status'] == 1:
                valid_students.append({
                    "student_did": student_did,
                    "status": "verified and VC valid"
                })

        verification_time = time.time() - start_time

        return jsonify({
            "status": "success",
            "valid_students": valid_students,
            "verification_time": verification_time,
            "total_gas_used_schnorr": total_gas_used_schnorr,
            "total_gas_used_vc": total_gas_used_vc
        })

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
