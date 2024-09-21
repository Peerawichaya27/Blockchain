// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ETranscript {
    struct Transcript {
        address studentAddress;
        bytes32 aclHash;
        bytes32 vcHash;
        uint256 expiration; // Expiration timestamp
    }

    mapping(address => Transcript) public transcripts;

    // Register a transcript with the ACL and VC hash
    function registerTranscript(address _student, bytes32 _aclHash, bytes32 _vcHash, uint256 _expiration) public {
        require(_expiration > block.timestamp, "Invalid expiration date");
        transcripts[_student] = Transcript(_student, _aclHash, _vcHash, _expiration);
    }

    // Verify the transcript by checking the hashes and validity
    function verifyTranscript(address _student, bytes32 _aclHash, bytes32 _vcHash) public view returns (bool) {
        Transcript memory t = transcripts[_student];
        require(block.timestamp <= t.expiration, "Transcript has expired");
        require(t.aclHash == _aclHash && t.vcHash == _vcHash, "Hashes do not match");
        return true;
    }

    // Revoke a transcript (for example, if the student loses their right to share)
    function revokeTranscript(address _student) public {
        delete transcripts[_student];
    }
}
