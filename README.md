# EV-Transcript System

# Overview

The EV-Transcript system is an advanced, blockchain-based solution for managing academic records securely and efficiently. By integrating Self-Sovereign Identity (SSI) and the InterPlanetary File System (IPFS), this system provides students with control over their educational credentials while enhancing privacy, scalability, and security. The use of Decentralized Identifiers (DIDs), Verifiable Credentials (VCs), and an optimized Schnorr protocol ensures reliable, privacy-preserving verification processes between students, universities, and employers.

# Features

 - <strong>Blockchain Integration:</strong> Utilizes blockchain for secure, decentralized storage of transcript metadata, ensuring data immutability and transparency.

 - <strong>Self-Sovereign Identity (SSI):</strong> Empowers students to manage their own credentials without relying on centralized authorities.

 - <strong>InterPlanetary File System (IPFS):</strong> Stores hashed credentials securely in a distributed manner to prevent tampering and unauthorized access.

 - <strong>Optimized Schnorr Proof:</strong> Employs an optimized Schnorr protocol for privacy-preserving authentication between employers and the verification system via smart contracts.

 - <strong>Access Control Mechanisms:</strong> Verifiable Presentations (VPs) allow students to selectively share transcript data, with full control over access rights and duration.

# System Architecture

The EV-Transcript system consists of the following components:

 1) <strong>University Interface:</strong> Issues VCs to students and manages blockchain and IPFS interactions for credential verification.

 2) <strong>VC & DID Generator:</strong> Generates Verifiable Credentials (VCs) and Decentralized Identifiers (DIDs) to ensure data integrity and privacy.

 3) <strong>Student Wallet:</strong> A secure digital wallet for storing unhashed VCs, allowing students to manage their academic records.

 4) <strong>Employer Verification:</strong> Employers verify credentials through QR codes and a secure Schnorr proof-based process.

 5) <strong>Blockchain:</strong> Stores metadata and IPFS indices for secure credential access.

 6) <strong>IPFS:</strong> Stores hashed VCs and DID documents, ensuring decentralized, tamper-proof storage.

 7) <strong>VP & Token Generator:</strong> Produces Verifiable Presentations (VPs) and tokens for credential sharing.

 8) <strong>ZKP Schnorr Module:</strong> Generates and verifies Schnorr proofs to enable privacy-preserving verification.
