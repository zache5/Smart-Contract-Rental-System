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
        string memory stockName
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
        });

        return newTokenId;
    }
    // return the nft details
    function getVehicleNFTDetails(uint256 tokenId) public view returns (Vehicle memory) {
        return _tokenDetails[tokenId];
    }
    function getStartDate(uint256 tokenId) public view returns (uint256) {
    require(_exists(tokenId), "VehicleNFT: token does not exist");
    return _tokenDetails[tokenId].startDate;
}
    
    // will probably need to add streamlit here to get these details
    // checks for start and end date, also if tokenid exists
    function setRentalDetails(
        uint256 tokenId,
        uint256 startDate,
        uint256 endDate,
        address renter
        ) public {
            require(_exists(tokenId), "VehicleNFT: token does not exist");
            require(endDate > startDate, "VehicleNFT: end date must be after start date");

            _tokenDetails[tokenId].startDate = startDate;
            _tokenDetails[tokenId].endDate = endDate;
            _tokenDetails[tokenId].renter = renter;
    }
    // return renter details, 
    function getRentalDetails(uint256 tokenId) public view returns (
            uint256 startDate,
            uint256 endDate,
            address renter
        )
    {
    require(_exists(tokenId), "VehicleNFT: token does not exist");

    // set start end and renter details
    startDate = _tokenDetails[tokenId].startDate;
    endDate = _tokenDetails[tokenId].endDate;
    renter = _tokenDetails[tokenId].renter;
    }
    function returnNFT(uint256 tokenId) public {
        require(_exists(tokenId), "VehicleNFT: token does not exist");
        require(msg.sender == _tokenDetails[tokenId].renter, "VehicleNFT: only renter can return NFT");
        require(block.timestamp > _tokenDetails[tokenId].endDate, "VehicleNFT: rental period has not yet ended");

        // transfer the NFT back to the owner's wallet
        _transfer(msg.sender, ownerOf(tokenId), tokenId);

        // reset the rental details
        _tokenDetails[tokenId].startDate = 0;
        _tokenDetails[tokenId].endDate = 0;
        _tokenDetails[tokenId].renter = address(0);
    }


}
