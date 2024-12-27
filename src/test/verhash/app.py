from flask import Flask, request, jsonify, render_template
from web3 import Web3
import json
import os
import random
import time

app = Flask(__name__)

# Connect to Ganache
ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

if not web3.is_connected():
    raise Exception("Failed to connect to Ganache")

# Load the smart contract
with open("blockchain/build/contracts/HashStorage.json", "r") as file:
    contract_data = json.load(file)

contract_address = "0x678e573a625d4fbbddC6D2C9a814e01D90D831c9"  # Replace with your deployed contract address
contract = web3.eth.contract(address=contract_address, abi=contract_data["abi"])


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/store_hashes_once", methods=["POST"])
def store_hashes_once():
    try:
        # Load the entire JSON file for storage
        file_path = "hashes_1000.json"  # The file should contain all the hashes to store
        if not os.path.exists(file_path):
            return jsonify({"error": "Hash file not found"}), 400

        with open(file_path, "r") as file:
            data = json.load(file)
            hashes = data["hashes"]

        # Split hashes into chunks of 50 and store them across blocks
        for i in range(0, len(hashes), 50):
            chunk = hashes[i:i + 50]
            print(f"Storing chunk: {chunk}")  # Debug log
            tx = contract.functions.storeBlock(chunk).transact({'from': web3.eth.accounts[0]})
            web3.eth.wait_for_transaction_receipt(tx)

        return jsonify({"message": f"{len(hashes)} hashes successfully stored in {len(hashes) // 50 + (1 if len(hashes) % 50 > 0 else 0)} block(s)!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/compare_shuffled/<size>", methods=["POST"])
def compare_shuffled(size):
    try:
        size = int(size)  # Parse the size of the subset to compare
        file_path = "hashes_1000.json"
        if not os.path.exists(file_path):
            return jsonify({"error": "Hash file not found"}), 400

        with open(file_path, "r") as file:
            original_hashes = json.load(file)["hashes"]

        # Shuffle the hashes and pick a subset
        shuffled_hashes = original_hashes[:]
        random.shuffle(shuffled_hashes)
        subset = shuffled_hashes[:size]

        # Compare each hash using the smart contract
        start_time = time.time()
        missing_hashes = []
        for h in subset:
            exists = contract.functions.hashExists(h).call()
            if not exists:
                missing_hashes.append(h)
        end_time = time.time()

        if missing_hashes:
            return jsonify({
                "match": False,
                "missing_hashes": missing_hashes,
                "time_taken": end_time - start_time
            })
        else:
            return jsonify({
                "match": True,
                "message": f"All {size} hashes were found in the blockchain.",
                "time_taken": end_time - start_time
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
if __name__ == "__main__":
    app.run(debug=True)
