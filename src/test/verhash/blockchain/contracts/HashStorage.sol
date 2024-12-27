// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HashStorage {
    struct Block {
        uint id;
        string[50] hashes; // Array to store up to 50 hashes
        uint hashCount;    // Actual number of hashes stored
    }

    mapping(uint => Block) public blocks;
    uint public blockCount;

    // Store a block with up to 50 hashes
    function storeBlock(string[] memory _hashes) public {
        require(_hashes.length <= 50, "A block can store a maximum of 50 hashes.");
        Block storage newBlock = blocks[blockCount];
        newBlock.id = blockCount;
        newBlock.hashCount = _hashes.length;

        for (uint i = 0; i < _hashes.length; i++) {
            newBlock.hashes[i] = _hashes[i];
        }

        blockCount++;
    }

    // Get hashes and their count from a specific block
    function getBlock(uint _id) public view returns (string[50] memory, uint) {
        Block storage blockData = blocks[_id];
        return (blockData.hashes, blockData.hashCount);
    }

    // Check if a specific hash exists in any block
    function hashExists(string memory _hash) public view returns (bool) {
        for (uint i = 0; i < blockCount; i++) {
            Block storage currentBlock = blocks[i];
            for (uint j = 0; j < currentBlock.hashCount; j++) {
                if (keccak256(abi.encodePacked(currentBlock.hashes[j])) == keccak256(abi.encodePacked(_hash))) {
                    return true;
                }
            }
        }
        return false;
    }

    // // Check if multiple hashes exist in the blockchain
    // function hashesExist(string[] memory _hashes) public view returns (bool[] memory) {
    //     bool[] memory results = new bool[](_hashes.length);
    //     for (uint k = 0; k < _hashes.length; k++) {
    //         results[k] = false;
    //         for (uint i = 0; i < blockCount; i++) {
    //             Block storage currentBlock = blocks[i];
    //             for (uint j = 0; j < currentBlock.hashCount; j++) {
    //                 if (keccak256(abi.encodePacked(currentBlock.hashes[j])) == keccak256(abi.encodePacked(_hashes[k]))) {
    //                     results[k] = true;
    //                     break;
    //                 }
    //             }
    //             if (results[k]) break;
    //         }
    //     }
    //     return results;
    // }
}
