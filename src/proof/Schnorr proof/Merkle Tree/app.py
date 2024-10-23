from flask import Flask, request, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs={'timeout': 500}))
contract_address = Web3.to_checksum_address('0xF9b0c13b475B93A09aa93901f657d62127b1AE80')  # Replace with your deployed contract address

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
                'from': w3.eth.accounts[0], 'gas': 20000000
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

# Helper function to compute SHA256 hash
def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()

# Build the Merkle Tree
def build_merkle_tree(hashed_vcs):
    """ Constructs a Merkle Tree from a list of hashed VCs """
    tree = []
    current_layer = hashed_vcs

    # While there's more than 1 node, reduce by hashing pairs
    while len(current_layer) > 1:
        tree.append(current_layer)
        next_layer = []

        # Hash pairs of nodes
        for i in range(0, len(current_layer), 2):
            # Handle odd-length layers by duplicating the last node
            if i + 1 < len(current_layer):
                combined_hash = sha256(current_layer[i] + current_layer[i + 1])
            else:
                combined_hash = sha256(current_layer[i] + current_layer[i])  # Duplicate last hash
            next_layer.append(combined_hash)

        current_layer = next_layer

    tree.append(current_layer)  # Root is the only node left in the last layer
    return tree

# Retrieve Merkle root from the Merkle Tree
def get_merkle_root(tree):
    return tree[-1][0] if tree else None

# Generate a Merkle proof for a particular index
def get_merkle_proof(tree, index):
    proof = []
    for layer in tree[:-1]:  # Skip the last layer (the root)
        if index % 2 == 0 and index + 1 < len(layer):
            proof.append(layer[index + 1])
        elif index % 2 == 1:
            proof.append(layer[index - 1])
        index //= 2
    return proof

@app.route('/batch_verify_json', methods=['POST'])
def batch_verify_from_json():
    global proof_verified  # Track Schnorr proof state globally
    cumulative_gas_used = 0  # Initialize cumulative gas counter
    invalid_students = []  # List to hold invalid students
    try:
        # Load data
        with open('batch_verification_payload.json', 'r') as f:
            students_data = json.load(f)['students']

        with open('token.json', 'r') as f:
            token_data = json.load(f)

        with open('ipfs.json', 'r') as f:
            ipfs_data = json.load(f)

        valid_students = []
        start_time = time.time()

        # Collect hashed VCs from students
        hashed_vcs = []
        for student in students_data:
            student_index = contract.functions.getIndexByDid(student['student_did']).call()
            ipfs_hashed_vc = ipfs_data[str(student_index)]['hashed_vc']  # Get the hashed VC from IPFS data
            vp_hashed_vc = token_data[str(student_index)]['verifiablePresentation']['verifiableCredential'][0]['hash']  # Get hashed VC from the VP
            hashed_vcs.append(vp_hashed_vc)

            # Compare hashed VC from VP and hashed VC from IPFS
            if vp_hashed_vc != ipfs_hashed_vc:
                # Log invalid student but continue to next
                invalid_students.append({
                    "student_did": student['student_did'],
                    "status": "Hashed VC mismatch"
                })
                continue  # Skip to the next student

            # If valid, continue with Merkle proof and verification
            merkle_tree = build_merkle_tree(hashed_vcs)
            merkle_root = get_merkle_root(merkle_tree)

            # Submit the root to the blockchain
            tx_hash = contract.functions.setMerkleRoot(bytes.fromhex(merkle_root)).transact({
                'from': w3.eth.accounts[0], 'gas': 2000000
            })
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            cumulative_gas_used += receipt['gasUsed']  # Add the gas used for this transaction

            # Generate the Merkle Proof for the student
            merkle_proof = get_merkle_proof(merkle_tree, len(valid_students))

            # Verify the proof on the blockchain
            tx_hash = contract.functions.verifyMerkleProof(
                [bytes.fromhex(p) for p in merkle_proof], 
                bytes.fromhex(vp_hashed_vc)
            ).transact({'from': w3.eth.accounts[0], 'gas': 2000000})

            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            cumulative_gas_used += receipt['gasUsed']  # Add the gas used for this transaction

            if receipt['status'] == 1:
                valid_students.append({
                    "student_did": student['student_did'],
                    "status": "verified and VC valid"
                })

        verification_time = time.time() - start_time

        return jsonify({
            "status": "success",
            "valid_students": valid_students,
            "invalid_students": invalid_students,  # Return the invalid students as well
            "verification_time": verification_time,
            "cumulative_gas_used": cumulative_gas_used  # Return the total gas used
        })

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)})


if __name__ == '__main__':
    app.run(debug=True)
