// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SchnorrBatchVerification {

    // Define a struct to hold all the proof parameters
    struct SchnorrProof {
        uint256 R;
        uint256 s;
        uint256 g;
        uint256 p;
        uint256 c;
        bytes32 employerHashedEmail;
    }

    // Function to generate a challenge based on commitment R
    function getChallenge(uint256 R) public view returns (uint256) {
        return uint256(keccak256(abi.encodePacked(R, block.timestamp))) % 23;
    }

    // Function for batch verification of Schnorr proofs
    function batchVerifySchnorrProof(SchnorrProof[] memory proofData) public view returns (bool[] memory) {
        uint256 batchSize = proofData.length;
        bool[] memory results = new bool[](batchSize);

        for (uint256 i = 0; i < batchSize; i++) {
            // Schnorr proof verification: g^s mod p == R * g^hashed_email^c mod p
            uint256 lhs = modExp(proofData[i].g, proofData[i].s, proofData[i].p); // Left-hand side: g^s mod p

            // Precompute the hashed email's exponentiation
            uint256 hashedEmailExp = modExp(proofData[i].g, uint256(proofData[i].employerHashedEmail), proofData[i].p);

            // Right-hand side: R * (g^hashed_email)^c mod p
            uint256 rhs = (proofData[i].R * hashedEmailExp ** proofData[i].c) % proofData[i].p;

            // Store the result of the comparison
            results[i] = (lhs == rhs);
        }

        return results;
    }

    // Optimized modular exponentiation (g^exp mod p)
    function modExp(uint256 base, uint256 exp, uint256 mod) internal pure returns (uint256) {
        uint256 result = 1;
        base = base % mod; // Only perform base modulo once

        while (exp > 0) {
            if (exp % 2 == 1) {
                result = mulmod(result, base, mod);  // Perform mod here to reduce the operation frequency
            }
            base = mulmod(base, base, mod);  // Use mulmod to prevent overflow and compute mod during multiplication
            exp /= 2;
        }
        return result;
    }
}
