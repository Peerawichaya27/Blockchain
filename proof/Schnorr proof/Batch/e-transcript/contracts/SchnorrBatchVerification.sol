// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SchnorrBatchVerification {

    // Function to generate a challenge based on commitment R
    function getChallenge(uint256 R) public view returns (uint256) {
        return uint256(keccak256(abi.encodePacked(R, block.timestamp))) % 23;
    }

    // Function for batch verification of Schnorr proofs
    function batchVerifySchnorrProof(
        uint256[] memory R_batch, 
        uint256[] memory s_batch, 
        uint256[] memory g_batch, 
        uint256[] memory p_batch, 
        uint256[] memory c_batch, 
        string[] memory students_batch,  // Custom DIDs as string
        string[] memory employer_hashed_emails_batch
    ) public view returns (bool[] memory) {
        uint256 batchSize = R_batch.length;
        bool[] memory results = new bool[](batchSize);

        for (uint256 i = 0; i < batchSize; i++) {
            // Perform Schnorr proof verification
            uint256 lhs = modExp(g_batch[i], s_batch[i], p_batch[i]); // g^s mod p
            uint256 rhs = (R_batch[i] * modExp(g_batch[i], uint256(keccak256(abi.encodePacked(employer_hashed_emails_batch[i]))), p_batch[i]) ** c_batch[i]) % p_batch[i]; // R * g^hashed_email^c mod p

            results[i] = (lhs == rhs); // Store the result for each verification
        }

        return results; // Return the batch results
    }

    // Modular exponentiation helper function (g^exp mod p)
    function modExp(uint256 base, uint256 exp, uint256 mod) internal pure returns (uint256) {
        uint256 result = 1;
        while (exp > 0) {
            if (exp % 2 == 1) {
                result = (result * base) % mod;
            }
            base = (base * base) % mod;
            exp /= 2;
        }
        return result;
    }
}
