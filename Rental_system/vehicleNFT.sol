// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
// importing erc721 files from openzeppelin

contract VehicleNFT is ERC721 {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;
    // creating vehicle struct to store vehicle data and then link to nft.
    struct Vehicle {
        string VIN;
        string make;
        string model;
        string licensePlate;
        uint256 year;
        string stockName;
        uint dailyPrice;
    }
    // mapping each token id to the vehicle struct data
    mapping(uint256 => Vehicle) private _tokenDetails;

    constructor() ERC721("VehicleNFT", "VEHICLE") {}
    // function for minting new inventory with vehicle data, basically adding items to virtual fleet.
    function createVehicleNFT(
        string memory VIN,
        string memory make,
        string memory model,
        string memory licensePlate,
        uint256 year,
        string memory stockName,
        uint dailyPrice
    ) public returns (uint256) {
        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();
        // using built in functions to safely mint. 
        _safeMint(msg.sender, newTokenId);

        _tokenDetails[newTokenId] = Vehicle({
            VIN: VIN,
            make: make,
            model: model,
            licensePlate: licensePlate,
            year: year,
            stockName: stockName
            dailyPrice: dailyPrice
        });

        return newTokenId;
    }

    function getVehicleNFTDetails(uint256 tokenId) public view returns (Vehicle memory) {
        return _tokenDetails[tokenId];
    }
}
