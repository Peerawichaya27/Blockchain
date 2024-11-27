from flask import Flask, request, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 500}))
contract_address = Web3.to_checksum_address('0x2c7DD58032db63f428e3E315D31ccFf283093bEd')  # Replace with your deployed contract address

# Load the contract ABI
with open('e-transcript_proof/build/contracts/SchnorrBatchVerification.json') as f:
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
                'from': w3.eth.accounts[4], 'gas': 20000000
            })
            # Wait for the transaction to be mined
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Stored DID: {student_did} with index: {student_index} on the blockchain")

        return jsonify({"status": "success", "message": f"DID {student_did} stored with index {student_index}"}), 200

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)}), 500

@app.route('/batch_verify_json', methods=['POST'])
def batch_verify_from_json():
    try:
        data = request.get_json()
        employer_email = data.get('email')
        token = data.get('token')

        if not employer_email or not token:
            return jsonify({"status": "failed", "message": "Missing email or token"}), 400

        hashed_email = hashlib.sha256(employer_email.encode()).hexdigest()
        student_did = token.get('student_did')
        ipfs_hashed_vc = token.get('ipfs_hashed_vc')
        hashed_vc_from_vp = token.get('hashed_vc_from_vp')

        if not student_did or not ipfs_hashed_vc or not hashed_vc_from_vp:
            return jsonify({"status": "failed", "message": "Missing VC or student data in token"}), 400

        # Schnorr Proof variables
        r = random.randint(1, P-1)
        R = pow(G, r, P)
        challenge = contract.functions.getChallenge(R).call()
        hashed_secret = int(hashlib.sha256(employer_email.encode()).hexdigest(), 16) % P
        s = (r + challenge * hashed_secret) % (P-1)

        # Call unified verification
        tx_hash = contract.functions.verify(
            R, s, G, P, challenge, hashed_email, hashed_vc_from_vp, student_did, ipfs_hashed_vc
        ).transact({'from': w3.eth.accounts[4], 'gas': 3000000})

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt['status'] == 1:
            return jsonify({"status": "success", "message": "Verification successful"}), 200
        else:
            return jsonify({"status": "failed", "message": "Verification failed"}), 403

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)}), 500
    
@app.route('/get_index', methods=['GET'])
def get_index():
    try:
        student_did = request.args.get('student_did')

        if not student_did:
            return jsonify({"status": "failed", "message": "Missing student DID"}), 400

        student_index = contract.functions.getIndexByDid(student_did).call()
        return jsonify({"status": "success", "index": student_index}), 200

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
