from flask import Flask, request, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract_address = Web3.to_checksum_address('0x50f30D482Ad0F4B0FFF71Bc50b5fbE5FDaCDD09D')  # Replace with your deployed contract address

# Load the contract ABI
with open('e-transcript/build/contracts/SchnorrBatchVerification.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Static variables for Schnorr proof
G = 2  # Generator (example)
P = 23 # Prime modulus (example)

@app.route('/batch_verify_page', methods=['GET'])
def batch_verify_page():
    # Render the batch verification HTML page
    return render_template('batch_verify.html')

@app.route('/store_acl_page', methods=['GET'])
def store_acl_page():
    # Render the HTML form page for storing ACL
    return render_template('store_acl.html')

# Route to store ACL data from acl.json on the blockchain
@app.route('/store_acl', methods=['POST'])
def store_acl():
    try:
        # Load the ACL data from acl.json
        with open('acl.json', 'r') as f:
            acl_data = json.load(f)

        # Iterate over the student entries and store the ACL data on the blockchain
        for student in acl_data['students']:
            student_did = Web3.to_checksum_address(student['student_did'])  # Ensure valid Ethereum address
            employer_hashed_email = student['employer_hashed_email']  # Employer's hashed email
            expiration = student['expiration']  # Expiration timestamp

            # Call the smart contract function to store the ACL
            tx_hash = contract.functions.storeACL(
                student_did,         # Student DID (Ethereum address)
                employer_hashed_email,  # Hashed employer email
                expiration           # Expiration timestamp
            ).transact({'from': w3.eth.accounts[3]})  # Use an account from Ganache to make the transaction

            # Wait for the transaction to be mined
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Stored ACL for student {student_did}: Transaction receipt: {receipt}")

        return jsonify({"status": "success", "message": "ACL stored successfully!"})

    except Exception as e:
        return jsonify({"status": "failed", "message": str(e)})

# Batch verification route
@app.route('/batch_verify', methods=['POST'])
def batch_verify_schnorr_proof():
    try:
        # The request payload should contain the list of students and employer emails
        students_data = request.json.get('students')

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

        # Loop through each student's data
        for student in students_data:
            secret = student['email'].strip().lower()  # Employer's unhashed email
            student_did = Web3.to_checksum_address(student['student_did'])  # Student's DID

            # Hash the employer's email (secret)
            hashed_email = hashlib.sha256(secret.encode()).hexdigest()

            # Retrieve the stored hashed email from the blockchain
            stored_hashed_email = contract.functions.ACL(student_did).call()

            # Debugging output
            print(f"Stored Hashed Email for {student_did}: {stored_hashed_email}")
            print(f"Hashed Input Email: {hashed_email}")

            # Verify if the employer's hashed email matches the one stored on the blockchain
            if hashed_email != stored_hashed_email:
                return jsonify({"status": "failed", "message": f"Employer's secret for {secret} does not match"})

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

        # Send batch verification request to blockchain
        tx_hash = contract.functions.batchVerifySchnorrProof(
            R_batch, s_batch, g_batch, p_batch, c_batch, students_batch, employer_hashed_emails_batch
        ).transact({'from': w3.eth.accounts[3]})

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
