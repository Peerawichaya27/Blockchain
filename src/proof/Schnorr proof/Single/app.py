from flask import Flask, request, jsonify, render_template
from web3 import Web3
import json
import random
import hashlib
import time

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract_address = Web3.to_checksum_address('0x5428bda599BfD5b3820fd38fF1868e9d114156De')

# Load the contract ABI and Address (from the Truffle build folder)
with open('e-transcript/build/contracts/SchnorrVerification.json') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Static variables for Schnorr proof
G = 2  # Generator (example)
P = 23 # Prime modulus (example)

@app.route('/store_acl', methods=['GET', 'POST'])
def store_acl():
    # Load the ACL data from acl.json
    with open('acl.json', 'r') as f:
        acl_data = json.load(f)

    # Extract values from the JSON
    student_did = Web3.to_checksum_address(acl_data['student_did'])  # Ensure it's a valid Ethereum address
    hashed_email = acl_data['employer_hashed_email']
    acl_link = acl_data['acl_link']
    expiration = acl_data['expiration']
    is_valid = acl_data['isValid']

    # Store the ACL data on-chain
    tx_hash = contract.functions.storeACL(
        student_did,         # Student DID (Ethereum address)
        acl_link,            # ACL link
        hashed_email,        # Employer's hashed email
        expiration           # Expiration timestamp
    ).transact({'from': w3.eth.accounts[0]})  # Use an account from Ganache to make the transaction

    # Wait for the transaction to be mined
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return f"Transaction receipt: {receipt}"

# Flask route to render the verification page
@app.route('/verify', methods=['GET', 'POST'])
def verify_schnorr_proof():
    if request.method == 'GET':
        # Extract the student DID from the query string in the link
        student_did = request.args.get('did')
        print(request.args)  # Add this line to print the received arguments
        if not student_did:
            return jsonify({"status": "error", "message": "Student DID not found in the link!"})

        # Serve the HTML page, passing the student DID to the template
        return render_template('verify.html', student_did=student_did)

    elif request.method == 'POST':
        # Employer inputs their unhashed email (secret)
        secret = request.form.get("secret").strip().lower()  # Ensure clean and consistent email formatting
        student_did = request.form.get("student_did")

        # Convert the student DID to a checksum address
        student_did = Web3.to_checksum_address(student_did)

        # Retrieve the stored hashed email from the blockchain (provided by the student)
        stored_hashed_email = contract.functions.ACL(student_did).call()

        # Debugging output
        print(f"Stored Hashed Email: {stored_hashed_email}")
        print(f"Hashed Input Email: {hashlib.sha256(secret.encode()).hexdigest()}")

        # Verify that the employer's hashed email matches the one provided by the student
        if hashlib.sha256(secret.encode()).hexdigest() != stored_hashed_email:
            return jsonify({"status": "failed", "message": "Employer's secret does not match"})

        # Generate the commitment (R)
        r = random.randint(1, P-1)  # Random nonce
        R = pow(G, r, P)  # R = g^r mod p

        # Send commitment (R) to blockchain to get the challenge
        challenge = contract.functions.getChallenge(R).call()

        # Calculate response (s)
        hashed_secret = int(hashlib.sha256(secret.encode()).hexdigest(), 16) % P
        s = (r + challenge * hashed_secret) % (P-1)

        # Send the Schnorr proof (R, s) back to the blockchain
        tx_hash = contract.functions.verifySchnorrProof(
            R,
            s,
            G,
            P,
            challenge,
            student_did,  # DID from the link
            secret
        ).transact({'from': w3.eth.accounts[0]})

        # Wait for transaction receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt['status'] == 1:
            return jsonify({"status": "success", "message": "Schnorr proof verified successfully"})
        else:
            return jsonify({"status": "failed", "message": "Verification failed"})

if __name__ == '__main__':
    app.run(debug=True)
