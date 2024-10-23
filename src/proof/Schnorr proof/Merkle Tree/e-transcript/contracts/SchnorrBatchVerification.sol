// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SchnorrBatchVerification {

    // Mapping to store the index of each student based on their DID (Decentralized Identifier)
    mapping(string => uint256) public didToIndex;
    
    // Mapping to keep track of whether the Schnorr proof has been verified for a student
    mapping(string => bool) public schnorrProofVerified;

    // Variable to store the Merkle root on the blockchain
    bytes32 public merkleRoot;

    // Events for logging important actions (Merkle root updates, debugging)
    event DebugValues(uint256 lhs, uint256 rhs, uint256 R, uint256 s);
    event MerkleRootUpdated(bytes32 newMerkleRoot);

    // Store a student's DID and its corresponding index
    function storeDidToIndex(string calldata studentDid, uint256 index) external {
        didToIndex[studentDid] = index;
    }

    // Retrieve the index of a student using their DID
    function getIndexByDid(string calldata studentDid) external view returns (uint256) {
        return didToIndex[studentDid];
    }

    // Check if the Schnorr proof has already been verified for a given student
    function hasVerifiedSchnorrProof(string calldata studentDid) external view returns (bool) {
        return schnorrProofVerified[studentDid];
    }

    // Function to store the Merkle root on the blockchain
    function setMerkleRoot(bytes32 root) external {
        merkleRoot = root;
        emit MerkleRootUpdated(root);  // Emit an event to indicate that the Merkle root has been updated
    }

    // Internal function to verify the Schnorr proof
    // It checks if the computed values on both sides of the equation are equal
    function verifySchnorrProof(
        uint256 R,       // Public key R
        uint256 s,       // Signature part s
        uint256 g,       // Generator g
        uint256 p,       // Prime modulus p
        uint256 c,       // Challenge c
        bytes32 employerHashedEmail  // Hashed email of the employer (to act as a secret)
    ) internal view returns (bool) {
        uint256 lhs = modExp(g, s, p);  // Left-hand side: g^s % p
        uint256 rhs = calculateRHS(R, g, c, employerHashedEmail, p);  // Right-hand side: calculated from R and the challenge

        require(lhs == rhs, "Schnorr proof failed");  // If lhs != rhs, the Schnorr proof fails
        return true;
    }

    // Unified verification function that verifies the Schnorr proof and the hashed Verifiable Credential (VC)
    // This ensures that only verified students can have their credentials checked
    function verify(
        uint256 R,                     // Public key R for Schnorr proof
        uint256 s,                     // Signature part s for Schnorr proof
        uint256 g,                     // Generator g for Schnorr proof
        uint256 p,                     // Prime modulus p for Schnorr proof
        uint256 c,                     // Challenge c for Schnorr proof
        bytes32 employerHashedEmail,   // Employer's hashed email (acting as secret)
        bytes32 hashedVCFromVP,        // The hashed VC from the Verifiable Presentation (VP)
        string calldata studentDid,    // Student's DID
        bytes32 ipfsHashedVC           // The hashed VC stored in IPFS
    ) external returns (bool) {
        // If the Schnorr proof has not yet been verified for this student
        if (!schnorrProofVerified[studentDid]) {
            require(verifySchnorrProof(R, s, g, p, c, employerHashedEmail), "Schnorr proof verification failed");
            schnorrProofVerified[studentDid] = true;  // Mark the Schnorr proof as verified for this student
        }
        
        // Ensure the hashed VC from the VP matches the hashed VC stored in IPFS
        require(hashedVCFromVP == ipfsHashedVC, "Hashed VC verification failed");
        return true;  // If everything checks out, return true
    }

    // Function to verify the Merkle proof against the stored Merkle root
    // This ensures that the data being verified is part of the Merkle Tree stored on-chain
    function verifyMerkleProof(bytes32[] calldata proof, bytes32 leaf) external view returns (bool) {
        bytes32 computedHash = leaf;  // Start with the leaf (hashed data)

        // Traverse through the Merkle proof to compute the root hash
        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];
            // Combine current hash with the proof element to form a new hash (depending on order)
            computedHash = computedHash <= proofElement
                ? keccak256(abi.encodePacked(computedHash, proofElement))  // Hash computedHash + proofElement
                : keccak256(abi.encodePacked(proofElement, computedHash));  // Hash proofElement + computedHash
        }

        // Check if the computed hash (root) matches the stored Merkle root
        return computedHash == merkleRoot;
    }

    // Helper function for optimized modular exponentiation (efficiently computes base^exp % mod)
    function modExp(uint256 base, uint256 exp, uint256 mod) internal pure returns (uint256) {
        uint256 result = 1;  // Initialize result as 1
        base = base % mod;   // Reduce base modulo mod
        while (exp > 0) {
            // If exp is odd, multiply base with result
            if (exp % 2 == 1) {
                result = (result * base) % mod;
            }
            base = (base * base) % mod;  // Square the base
            exp /= 2;  // Divide exponent by 2
        }
        return result;
    }

    // Helper function to calculate the right-hand side of the Schnorr proof equation
    function calculateRHS(
        uint256 R,                     // Public key R for Schnorr proof
        uint256 g,                     // Generator g for Schnorr proof
        uint256 c,                     // Challenge c for Schnorr proof
        bytes32 employerHashedEmail,   // Employer's hashed email (used as a secret)
        uint256 p                      // Prime modulus p
    ) internal pure returns (uint256) {
        // Calculate the right-hand side of the Schnorr proof equation:
        // (R * (g^hashedEmail)^c) % p
        return (R * modExp(g, uint256(employerHashedEmail), p) ** c) % p;
    }
}
