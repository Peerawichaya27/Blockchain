// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UniversityCredential {
    struct VerifiableCredential {
        address studentAddress;
        bytes32 aclHash;
        bytes32 vcHash;
        uint256 expiration;
        bool valid;
    }

    mapping(address => VerifiableCredential) public credentials;
    address public issuer;

    constructor() {
        issuer = msg.sender;
    }

    // Register a transcript with the ACL and VC hash
    function registerTranscript(address studentAddress, bytes32 aclHash, bytes32 vcHash, uint256 expiration) public {
        require(msg.sender == issuer, "Only issuer can register credentials.");
        credentials[studentAddress] = VerifiableCredential(studentAddress, aclHash, vcHash, expiration, true);
    }

    // Verify the transcript by checking the hashes and validity
    function verifyTranscript(address _student, bytes32 _aclHash, bytes32 _vcHash) public view returns (bool) {
        VerifiableCredential memory t = credentials[_student];
        require(t.valid, "Transcript is not valid");
        require(block.timestamp <= t.expiration, "Transcript has expired");
        require(t.aclHash == _aclHash && t.vcHash == _vcHash, "Hashes do not match");
        return true;
    }

    // Revoke a transcript (for example, if the student loses their right to share)
    function revokeTranscript(address _student) public {
        require(msg.sender == issuer, "Only issuer can revoke credentials.");
        credentials[_student].valid = false;
    }
}
