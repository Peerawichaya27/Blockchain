// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SchnorrSingleVerification {

    struct SchnorrProof {
        uint256 R;
        uint256 s;
        uint256 c;
    }

    uint256 public precomputedGHashedEmail; // Stores g^hashed_email mod p for reuse
    uint256 constant G = 2; // Hardcoded generator constant
    uint256 constant P = 23; // Hardcoded prime modulus constant

    // Sets precomputed value for g^hashed_email mod p once, if it hasn't been set already
    function setPrecomputedGHashedEmail(uint256 hashedEmail) public {
        if (precomputedGHashedEmail == 0) {
            precomputedGHashedEmail = modExp(G, hashedEmail, P);
        }
    }

    // Generate a challenge using R, mod P to keep the result small
    function getChallenge(uint256 R) public pure returns (uint256) {
        return uint256(keccak256(abi.encodePacked(R))) % P;
    }

    // Optimized verification using precomputed value
    function verifySchnorrProof(SchnorrProof memory proofData) public view returns (bool) {
        uint256 lhs = modExp(G, proofData.s, P); // Compute g^s mod p
        uint256 rhs = mulmod(proofData.R, modExp(precomputedGHashedEmail, proofData.c, P), P); // Compute R * (precomputedGHashedEmail)^c mod p

        // Check if left side equals the right side
        return lhs == rhs;
    }

    // Optimized modular exponentiation with binary exponentiation for efficient gas usage
    function modExp(uint256 base, uint256 exp, uint256 mod) internal pure returns (uint256) {
        uint256 result = 1;
        base %= mod; // Take base mod once at the start

        while (exp > 0) {
            if (exp & 1 == 1) { // If exp is odd
                result = mulmod(result, base, mod);
            }
            base = mulmod(base, base, mod);
            exp >>= 1; // Divide exp by 2
        }
        return result;
    }
}
