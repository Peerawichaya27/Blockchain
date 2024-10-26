EV-Transcript System

Overview

The EV-Transcript system is an advanced, blockchain-based solution for managing academic records securely and efficiently. By integrating Self-Sovereign Identity (SSI) and the InterPlanetary File System (IPFS), this system provides students with control over their educational credentials while enhancing privacy, scalability, and security. The use of Decentralized Identifiers (DIDs), Verifiable Credentials (VCs), and an optimized Schnorr protocol ensures reliable, privacy-preserving verification processes between students, universities, and employers.

Features

Blockchain Integration: Utilizes blockchain for secure, decentralized storage of transcript metadata, ensuring data immutability and transparency.

Self-Sovereign Identity (SSI): Empowers students to manage their own credentials without relying on centralized authorities.

InterPlanetary File System (IPFS): Stores hashed credentials securely in a distributed manner to prevent tampering and unauthorized access.

Optimized Schnorr Proof: Employs an optimized Schnorr protocol for privacy-preserving authentication between employers and the verification system via smart contracts.

Access Control Mechanisms: Verifiable Presentations (VPs) allow students to selectively share transcript data, with full control over access rights and duration.

System Architecture

The EV-Transcript system consists of the following components:

University Interface: Issues VCs to students and manages blockchain and IPFS interactions for credential verification.

VC & DID Generator: Generates Verifiable Credentials (VCs) and Decentralized Identifiers (DIDs) to ensure data integrity and privacy.

Student Wallet: A secure digital wallet for storing unhashed VCs, allowing students to manage their academic records.

Employer Verification: Employers verify credentials through QR codes and a secure Schnorr proof-based process.

Blockchain: Stores metadata and IPFS indices for secure credential access.

IPFS: Stores hashed VCs and DID documents, ensuring decentralized, tamper-proof storage.

VP & Token Generator: Produces Verifiable Presentations (VPs) and tokens for credential sharing.

ZKP Schnorr Module: Generates and verifies Schnorr proofs to enable privacy-preserving verification.

Getting Started

To get started with the EV-Transcript system, follow these steps:

Prerequisites

Python 3.12.6 or later

Ganache for Ethereum blockchain testing

IPFS for decentralized file storage

Flask for creating the university and student interfaces

A compatible web browser for accessing the interfaces

Installation

Clone the repository:

git clone https://github.com/yourusername/ev-transcript-system.git

Install the required dependencies:

pip install -r requirements.txt

Set up the IPFS and blockchain environments:

Run IPFS daemon:

ipfs daemon

Start Ganache to test blockchain transactions.

Start the Flask server:

python app.py

Usage

University Interface: Use the provided web interface to issue Verifiable Credentials to students.

Student Wallet: Securely store issued VCs and generate Verifiable Presentations for employers.

Employer Verification: Employers can scan a QR code to verify the authenticity of a student's transcript.

Evaluation

Scalability: The system has been tested to handle a large number of transcripts with minimal overhead, demonstrating efficient credential verification.

Performance: The optimized Schnorr proof mechanism reduces computational costs for authentication, making batch verification fast and resource-efficient.

Security: Enhanced privacy through zero-knowledge proofs (ZKPs) ensures that credentials are verified without exposing sensitive information.

Future Work

Batch Verification: Explore techniques for verifying multiple credentials at once to support large-scale use cases.

Multi-Party Collaboration: Expand functionality to support verification across multiple universities and employers.
