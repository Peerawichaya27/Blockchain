// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SchnorrSingleVerification {

    struct SchnorrProof {
        uint256 R;
        uint256 s;
        uint256 c;
    }

    uint256 public precomputedGHashedEmail; // Precomputed g^hashed_email mod p stored as a state variable
    uint256 public constant G = 2; // Fixed generator
    uint256 public constant P = 23; // Fixed prime modulus

    // Function to precompute g^hashed_email mod p and store it if not already set
    function setPrecomputedGHashedEmail(uint256 hashedEmail) external {
        if (precomputedGHashedEmail == 0) {
            precomputedGHashedEmail = modExp(G, hashedEmail, P);
        }
    }

    // Function to generate a challenge based on commitment R
    function getChallenge(uint256 R) external pure returns (uint256) {
        // Using modulo P directly here saves recalculation
        return uint256(keccak256(abi.encodePacked(R))) % P;
    }

    // Function to verify a single Schnorr proof using the stored precomputed value
    function verifySchnorrProof(SchnorrProof memory proofData) external view returns (bool) {
        require(precomputedGHashedEmail != 0, "Precomputed value not set");

        // g^s mod p
        uint256 lhs = modExp(G, proofData.s, P);

        // R * (precomputedGHashedEmail)^c mod p
        uint256 rhs = mulmod(proofData.R, modExp(precomputedGHashedEmail, proofData.c, P), P);

        return lhs == rhs;
    }

    // Optimized modular exponentiation using the square-and-multiply method
    function modExp(uint256 base, uint256 exp, uint256 mod) internal pure returns (uint256) {
        uint256 result = 1;
        base = base % mod;

        while (exp > 0) {
            if (exp & 1 == 1) {
                result = mulmod(result, base, mod);  // result = (result * base) % mod
            }
            base = mulmod(base, base, mod);  // base = (base * base) % mod
            exp >>= 1;
        }
        return result;
    }
}
