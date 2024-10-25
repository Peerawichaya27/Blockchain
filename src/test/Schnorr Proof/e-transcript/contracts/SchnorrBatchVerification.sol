// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SchnorrSingleVerification {

    // Define a struct to hold all the proof parameters
    struct SchnorrProof {
        uint256 R;
        uint256 s;
        uint256 g;
        uint256 p;
        uint256 c;
        uint256 employerHashedEmail; // employer's hashed email provided as uint256
    }

    // Function to generate a challenge based on commitment R
    function getChallenge(uint256 R) public pure returns (uint256) {
        return uint256(keccak256(abi.encodePacked(R))) % 23;
    }

    // Function to verify a single Schnorr proof
    function verifySchnorrProof(SchnorrProof memory proofData) public view returns (bool) {
        // Schnorr proof verification: g^s mod p == R * g^hashed_email^c mod p
        uint256 lhs = modExp(proofData.g, proofData.s, proofData.p); // Left-hand side: g^s mod p

        // Precompute the hashed email's exponentiation
        uint256 hashedEmailExp = modExp(proofData.g, proofData.employerHashedEmail, proofData.p);

        // Right-hand side: R * (g^hashed_email)^c mod p
        uint256 rhs = (proofData.R * modExp(hashedEmailExp, proofData.c, proofData.p)) % proofData.p;

        // Return true if the proof is valid, false otherwise
        return (lhs == rhs);
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
