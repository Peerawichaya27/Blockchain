from flask import Flask, request, jsonify, render_template
from eth_keys import keys
from eth_utils import decode_hex
import hashlib
import time
from web3 import Web3
import json

app = Flask(__name__)

# Web3 setup
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract_address = Web3.to_checksum_address('0x1d2C6A171B793087087Bc73d912f15ABcFD55150')  # Replace with your deployed contract address

# Load contract ABI
with open('e-transcript/build/contracts/PublicKeyVerification.json') as f:
    contract_abi = json.load(f)['abi']
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Example private key for signing (employer side) - for test purposes only
private_key_hex = '0x4c0883a69102937d6231471b5dbb6204fe512961708279229f15c0d2c8b2e5bb'
private_key = keys.PrivateKey(decode_hex(private_key_hex))

@app.route('/verify', methods=['GET', 'POST'])
def verify_signature():
    if request.method == 'GET':
        # Serve the HTML form for verification
        return render_template('verify.html')

    elif request.method == 'POST':
        # Start timing the verification process
        start_time = time.time()

        # Employer inputs their message and signature
        message = request.form.get("message").encode()
        signature = request.form.get("signature").strip()  # Ensure it's trimmed
        public_key = request.form.get("public_key").strip()  # Public key of the employer
        employer_address = request.form.get("employer_address").strip()

        # Debugging: Show input data for signature and public key
        print(f"Received Signature: {signature}")
        print(f"Received Public Key: {public_key}")

        # Remove '0x' from the signature if it exists
        if signature.startswith("0x"):
            signature = signature[2:]

        # Remove '0x' from the public key if it exists
        if public_key.startswith("0x"):
            public_key = public_key[2:]

        try:
            # Ensure the signature is in hex format and convert to bytes
            signature_bytes = bytes.fromhex(signature)
            print(f"Signature in bytes: {signature_bytes}")  # Debugging output
        except ValueError as e:
            print(f"Error converting signature: {e}")  # Debugging output
            return jsonify({"status": "failed", "message": "Invalid signature format. Ensure it is in hex format."})

        try:
            # Ensure the public key is in hex format and convert to bytes
            public_key_bytes = bytes.fromhex(public_key)
            print(f"Public Key in bytes: {public_key_bytes}")  # Debugging output
        except ValueError as e:
            print(f"Error converting public key: {e}")  # Debugging output
            return jsonify({"status": "failed", "message": "Invalid public key format. Ensure it is in hex format."})

        # Hash the message
        hashed_message = hashlib.sha256(message).digest()

        # Verify the signature (off-chain, for example purposes)
        signed_message = private_key.sign_msg_hash(hashed_message)  # For testing purposes only
        if signed_message.to_bytes().hex() == signature:
            # Store the signature verification result on the blockchain
            tx_hash = contract.functions.verifySignatureWithPublicKey(
                hashed_message,
                signature_bytes,
                public_key_bytes
            ).transact({'from': w3.eth.accounts[0]})

            # Wait for the transaction receipt
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            # Stop timing
            end_time = time.time()
            verification_time = end_time - start_time

            if receipt['status'] == 1:
                return jsonify({
                    "status": "success",
                    "message": "Signature verified successfully",
                    "verification_time": verification_time
                })
            else:
                return jsonify({"status": "failed", "message": "Verification failed"})
        else:
            return jsonify({"status": "failed", "message": "Signature does not match"})


# Endpoint for storing the public key (POST method)
@app.route('/store_public_key', methods=['POST'])
def store_public_key():
    public_key = request.form.get('public_key')
    employer_address = request.form.get('employer_address')
    
    # Convert to bytes and store on-chain
    tx_hash = contract.functions.storePublicKey(
        Web3.to_checksum_address(employer_address),
        bytes.fromhex(public_key)
    ).transact({'from': w3.eth.accounts[0]})
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return f"Transaction receipt: {receipt}"


if __name__ == '__main__':
    app.run(debug=True)
