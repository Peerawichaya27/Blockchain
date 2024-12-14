# EV-Transcript System

# Overview

The EV-Transcript system is an advanced, blockchain-based solution for managing academic records securely and efficiently. By integrating Self-Sovereign Identity (SSI) and the InterPlanetary File System (IPFS), this system provides students with control over their educational credentials while enhancing privacy, scalability, and security. The use of Decentralized Identifiers (DIDs), Verifiable Credentials (VCs), and an optimized Schnorr protocol ensures reliable, privacy-preserving verification processes between students, universities, and employers.

# Features

 - <strong>Blockchain Integration:</strong> Utilizes blockchain for secure, decentralized storage of transcript metadata, ensuring data immutability and transparency.

 - <strong>Self-Sovereign Identity (SSI):</strong> Empowers students to manage their own credentials without relying on centralized authorities.

 - <strong>InterPlanetary File System (IPFS):</strong> Stores hashed credentials securely in a distributed manner to prevent tampering and unauthorized access.

 - <strong>Optimized Schnorr Proof:</strong> Employs an optimized Schnorr protocol for privacy-preserving authentication between employers and the verification system via smart contracts.

 - <strong>Access Control Mechanisms:</strong> Verifiable Presentations (VPs) allow students to selectively disclose transcript data, with full control over access rights and duration.

# System Architecture

The EV-Transcript system consists of the following components:

 1) <strong>University Interface:</strong> Issues VCs to students and manages blockchain and IPFS interactions for credential verification.

 2) <strong>VC & DID Generator:</strong> Generates Verifiable Credentials (VCs) and Decentralized Identifiers (DIDs) to ensure data integrity and privacy.

 3) <strong>Student Wallet:</strong> A secure digital wallet for storing unhashed VCs, allowing students to manage their academic records.

 4) <strong>Employer Verification:</strong> Employers verify credentials through QR codes and a secure Schnorr proof-based process.

 5) <strong>Blockchain:</strong> Stores metadata and IPFS indices for secure credential access.

 6) <strong>IPFS:</strong> Stores hashed VCs and DID of students, ensuring decentralized, tamper-proof storage.

 7) <strong>VP & Token Generator:</strong> Produces Verifiable Presentations (VPs) and tokens for credential sharing.

 8) <strong>ZKP Schnorr Module:</strong> Generates and verifies Schnorr proofs to enable privacy-preserving verification.

## textFile Directory
The helper.txt is helping in using the truffle command.
The requirements.txt is use for installing the necessary library.

## ssi Directory
The ssi directory that located in the src folder is storing the references of the files that related to the SSI, which including the DID document, VC, and VP.

## test Directory
The test directory that located in the src folder is storing the testing files that are necessary for the evaluation.

## Run the Test
You can follow these steps below to Start our system.

Clone the project:

```bash
  git clone https://github.com/soravichpoon/Blockchain
```

Go to the textFile directory:

```bash
  cd textFile
```

Install dependencies:

```bash
  pip install --upgrade -r requirements.txt
```

Go back to main directory:

```bash
  cd ..
```

Go to the src directory:

```bash
  cd src
```

Go to the test directory:

```bash
  cd test
```

## Batch Vs UnBatch
This is going to test the Batch verification by using the Merkle Tree and the UnBatch verification that isn't use the Merkle Tree.

Go to the Batch_vs_UnBatch directory:

```bash
  cd Batch_vs_UnBatch
```

## Testing the Batch Verification
Go to the BatchVer directory:

```bash
  cd BatchVer
```

Go to the e-transcript directory:

```bash
  cd e-transcript
```

Remove the build directory:

```bash
  rmdir build
```

Change the "from" key inside the "module.exports, networks, developments" in the truffle-config file to be the chosen ACCOUNT ADDRESS of the Ganache.

Compile the smart contract:

```bash
  truffle compile
```

Migrate or Deploy the smark contract onto the blockchain:

```bash
  truffle migrate --network development
```

Go back to BatchVer directory:

```bash
  cd ..
```

Change the CONTRACT ADDRESS in the apps.py:

```bash
  contract_address = Web3.to_checksum_address('YOUR_CONTRACT_ADDRESS')           # Replace with your deployed contract address
```

Change the ACCOUNT ADDRESS in the apps.py:

```bash
  'from': w3.eth.accounts[0], 'gas': 200000000           # Replace "0" in the "accounts[0]" with your chosen ACCOUNT ADDRESS INDEX from the Ganache (Changing for all of them in the file)
```

Run the acl_create.py to create the acl.json:

```bash
  python acl_create.py           # You can input the number of student you want to test.
```

Delete the ipfs file:

```bash
  del ipfs.json
```

Delete the token file:

```bash
  del token.json
```

Run the hash_vc.py to create the ipfs.json:

```bash
  python hash_vc.py           # You can input the same number of student you used for the acl.
```

Run the vp_gen.py to create the token.json:

```bash
  python vp_gen.py           # You can input the same number of student you used for the acl.
```

Run the apps.py:

```bash
  python apps.py
```

Go to the path "/store" on the URL and click the "store_did_to_index" button.

Go to the path "/" on the URL and click the "batch_verify_json" button.

Result:
You will get the list of students who use the true vc and false vc.

## Testing the UnBatch Verification
Go to the UnBatchVer directory:

```bash
  cd UnBatchVer
```

Go to the e-transcript directory:

```bash
  cd e-transcript
```

Remove the build directory:

```bash
  rmdir build
```

Change the "from" key inside the "module.exports, networks, developments" in the truffle-config file to be the chosen ACCOUNT ADDRESS of the Ganache.

Compile the smart contract:

```bash
  truffle compile
```

Migrate or Deploy the smark contract onto the blockchain:

```bash
  truffle migrate --network development
```

Go back to BatchVer directory:

```bash
  cd ..
```

Change the CONTRACT ADDRESS in the apps.py:

```bash
  contract_address = Web3.to_checksum_address('YOUR_CONTRACT_ADDRESS')           # Replace with your deployed contract address
```

Change the ACCOUNT ADDRESS in the apps.py:

```bash
  'from': w3.eth.accounts[0], 'gas': 200000000           # Replace "0" in the "accounts[0]" with your chosen ACCOUNT ADDRESS INDEX from the Ganache (Changing for all of them in the file)
```

Run the acl_create.py to create the acl.json:

```bash
  python acl_create.py           # You can input the number of student you want to test.
```

Delete the ipfs file:

```bash
  del ipfs.json
```

Delete the token file:

```bash
  del token.json
```

Run the hash_vc.py to create the ipfs.json:

```bash
  python hash_vc.py           # You can input the same number of student you used for the acl.
```

Run the vp_gen.py to create the token.json:

```bash
  python vp_gen.py           # You can input the same number of student you used for the acl.
```

Run the app.py:

```bash
  python app.py
```

Go to the path "/store" on the URL and click the "store_did_to_index" button.

Go to the path "/" on the URL and click the "batch_verify_json" button.

Result:
You will get the list of students who use the true vc and false vc.

## Traditional Vs Optimize
This is going to test the Traditional Schnorr Proof and the Optimize Schnorr Proof.

Go to the Traditional_vs_Optimize directory:

```bash
  cd Traditional_vs_Optimize
```

## Testing the Traditional Schnorr Proof
Go to the TraditionalSchnorrProof directory:

```bash
  cd TraditionalSchnorrProof
```

Go to the e-transcript directory:

```bash
  cd e-transcript
```

Remove the build directory:

```bash
  rmdir build
```

Change the "from" key inside the "module.exports, networks, developments" in the truffle-config file to be the chosen ACCOUNT ADDRESS of the Ganache.

Compile the smart contract:

```bash
  truffle compile
```

Migrate or Deploy the smark contract onto the blockchain:

```bash
  truffle migrate --network development
```

Go back to BatchVer directory:

```bash
  cd ..
```

Change the CONTRACT ADDRESS in the apps.py:

```bash
  contract_address = Web3.to_checksum_address('YOUR_CONTRACT_ADDRESS')           # Replace with your deployed contract address
```

Change the ACCOUNT ADDRESS in the apps.py:

```bash
  'from': w3.eth.accounts[0]         # Replace "0" in the "accounts[0]" with your chosen ACCOUNT ADDRESS INDEX from the Ganache
```

Run the acl_create.py to create the acl.json:

```bash
  python acl_create.py           # You can input the number of student you want to test.
```

Run the app.py:

```bash
  python app.py
```

Go to the path "/" on the URL and click the "batch_verify_json" button.

Result:
You will get the time of Traditional Schnorr Proof.

## Testing the Optimize Schnorr Proof
Go to the OptimizeSchnorrProof directory:

```bash
  cd OptimizeSchnorrProof
```

Go to the e-transcript directory:

```bash
  cd e-transcript
```

Remove the build directory:

```bash
  rmdir build
```

Change the "from" key inside the "module.exports, networks, developments" in the truffle-config file to be the chosen ACCOUNT ADDRESS of the Ganache.

Compile the smart contract:

```bash
  truffle compile
```

Migrate or Deploy the smark contract onto the blockchain:

```bash
  truffle migrate --network development
```

Go back to BatchVer directory:

```bash
  cd ..
```

Change the CONTRACT ADDRESS in the apps.py:

```bash
  contract_address = Web3.to_checksum_address('YOUR_CONTRACT_ADDRESS')           # Replace with your deployed contract address
```

Change the ACCOUNT ADDRESS in the apps.py:

```bash
  'from': w3.eth.accounts[0], 'gas': 200000000           # Replace "0" in the "accounts[0]" with your chosen ACCOUNT ADDRESS INDEX from the Ganache (Changing for all of them in the file)
```

Run the acl_create.py to create the acl.json:

```bash
  python acl_create.py           # You can input the number of student you want to test.
```

Run the app.py:

```bash
  python app.py
```

Go to the path "/" on the URL and click the "batch_verify_json" button.

Result:
You will get the time of Optimize Schnorr Proof.

## Authors

- [@peerawichaya](https://github.com/Peerawichaya27)
- [@soravichpoon](https://github.com/soravichpoon)
- [@pawatpai](https://github.com/pawatpai)
