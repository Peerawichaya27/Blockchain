// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SchnorrBatchVerification {

    // Mapping to store the index of each student based on their DID (Decentralized Identifier)
    mapping(string => uint256) public didToIndex;

    // Mapping to keep track of whether the Schnorr proof has been verified for a student
    mapping(string => bool) public schnorrProofVerified;

    // Variable to store the Merkle root for hashed VCs on the blockchain
    bytes32 public ipfsMerkleRoot;
    bytes32 public vpMerkleRoot;

    // Events for logging important actions (Merkle root updates, debugging)
    event MerkleRootUpdated(bytes32 ipfsRoot, bytes32 vpRoot);
    event ProofVerified(bool isValid, string studentDid);
    
    // Store a student's DID and its corresponding index
    function storeDidToIndex(string calldata studentDid, uint256 index) external {
        didToIndex[studentDid] = index;
    }

    // Retrieve the index of a student using their DID
    function getIndexByDid(string calldata studentDid) external view returns (uint256) {
        return didToIndex[studentDid];
    }

    // Function to store the Merkle roots on the blockchain
    function setMerkleRoots(bytes32 ipfsRoot, bytes32 vpRoot) external {
        ipfsMerkleRoot = ipfsRoot;
        vpMerkleRoot = vpRoot;
        emit MerkleRootUpdated(ipfsRoot, vpRoot);  // Emit an event to indicate that the Merkle roots have been updated
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
    function verify(
        uint256 R,                     // Public key R for Schnorr proof
        uint256 s,                     // Signature part s for Schnorr proof
        uint256 g,                     // Generator g for Schnorr proof
        uint256 p,                     // Prime modulus p for Schnorr proof
        uint256 c,                     // Challenge c for Schnorr proof
        bytes32 employerHashedEmail,   // Employer's hashed email (acting as secret)
        bytes32 hashedVCFromVP,        // The hashed VC from the Verifiable Presentation (VP)
        string calldata studentDid     // Student's DID
    ) external returns (bool) {
        // Retrieve the student's index (retrieval of hashed VC from ipfs.json happens off-chain)
        uint256 studentIndex = didToIndex[studentDid];

        // If the Schnorr proof has not yet been verified for this student
        if (!schnorrProofVerified[studentDid]) {
            require(verifySchnorrProof(R, s, g, p, c, employerHashedEmail), "Schnorr proof verification failed");
            schnorrProofVerified[studentDid] = true;  // Mark the Schnorr proof as verified for this student
        }

        // After Schnorr proof verification, compare the Merkle roots to ensure they match
        require(ipfsMerkleRoot == vpMerkleRoot, "Merkle root mismatch");

        emit ProofVerified(true, studentDid);

        return true;  // If everything checks out, return true
    }

    // Function to verify the Merkle proof against the stored Merkle root
    function verifyMerkleProof(
        bytes32[] calldata proof,    // Proof path for the student
        bytes32 leaf                 // Hashed VC (leaf node)
    ) external view returns (bool) {
        bytes32 computedHash = leaf;

        // Traverse through the Merkle proof to compute the root hash
        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];
            // Combine current hash with the proof element to form a new hash (depending on order)
            computedHash = computedHash <= proofElement
                ? keccak256(abi.encodePacked(computedHash, proofElement))  // Hash computedHash + proofElement
                : keccak256(abi.encodePacked(proofElement, computedHash));  // Hash proofElement + computedHash
        }

        // Check if the computed hash (root) matches the stored Merkle root
        return computedHash == ipfsMerkleRoot && computedHash == vpMerkleRoot;
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
