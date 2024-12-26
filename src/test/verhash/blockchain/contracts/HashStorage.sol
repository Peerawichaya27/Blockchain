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
}
