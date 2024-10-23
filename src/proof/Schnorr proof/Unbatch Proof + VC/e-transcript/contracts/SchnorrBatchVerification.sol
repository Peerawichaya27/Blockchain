// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SchnorrBatchVerification {
    mapping(string => bool) public schnorrProofVerified;
    mapping(string => uint256) public didToIndex;

    event DebugValues(uint256 lhs, uint256 rhs, uint256 R, uint256 s);

    function storeDidToIndex(string memory studentDid, uint256 index) public {
        didToIndex[studentDid] = index;
    }

    function getIndexByDid(string memory studentDid) public view returns (uint256) {
        return didToIndex[studentDid];
    }

    function hasVerifiedSchnorrProof(string memory studentDid) public view returns (bool) {
        return schnorrProofVerified[studentDid];
    }

    function getChallenge(uint256 R) public view returns (uint256) {
        return uint256(keccak256(abi.encodePacked(R, block.timestamp))) % 23;
    }

    // Separate function to verify only Schnorr proof
    function verifySchnorrProof(
        uint256 R, 
        uint256 s, 
        uint256 g, 
        uint256 p, 
        uint256 c, 
        string memory employerHashedEmail,
        string memory studentDid
    ) public returns (bool) {
        uint256 lhs = modExp(g, s, p);
        uint256 rhs = calculateRHS(R, g, c, employerHashedEmail, p);
        
        emit DebugValues(lhs, rhs, R, s);

        require(lhs == rhs, "Schnorr proof failed");

        // Mark the Schnorr proof as verified for this student
        schnorrProofVerified[studentDid] = true;
        return true;
    }

    function verifyHashedVC(
        string memory hashedVCFromVP, 
        string memory studentDid, 
        string memory ipfsHashedVC
    ) public view returns (bool) {
        require(schnorrProofVerified[studentDid], "Schnorr proof not verified yet");
        return keccak256(abi.encodePacked(hashedVCFromVP)) == keccak256(abi.encodePacked(ipfsHashedVC));
    }

    // Modular exponentiation with gas optimization
    function modExp(uint256 base, uint256 exp, uint256 mod) internal pure returns (uint256) {
        uint256 result = 1;
        uint256 x = base % mod;

        while (exp > 0) {
            if (exp % 2 == 1) {
                result = (result * x) % mod;
            }
            x = (x * x) % mod;
            exp /= 2;
        }
        return result;
    }

    function calculateRHS(
        uint256 R, 
        uint256 g, 
        uint256 c, 
        string memory employerHashedEmail, 
        uint256 p
    ) internal pure returns (uint256) {
        return (R * modExp(g, uint256(keccak256(abi.encodePacked(employerHashedEmail))), p) ** c) % p;
    }
}
