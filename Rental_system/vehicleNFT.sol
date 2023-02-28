// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract VehicleNFT is ERC721 {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    struct Vehicle {
        string VIN;
        string make;
        string model;
        string licensePlate;
        uint256 year;
        string stockName;
        uint dailyPrice;
    }

    mapping(uint256 => Vehicle) private _tokenDetails;

    event VehicleNFTCreated(
        uint256 indexed tokenId,
        string VIN,
        string make,
        string model,
        string licensePlate,
        uint256 year,
        string stockName,
        uint dailyPrice
    );

    constructor() ERC721("VehicleNFT", "VEHICLE") {}

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
        _safeMint(msg.sender, newTokenId);
        _tokenDetails[newTokenId] = Vehicle({
            VIN: VIN,
            make: make,
            model: model,
            licensePlate: licensePlate,
            year: year,
            stockName: stockName,
            dailyPrice: dailyPrice
        });
        emit VehicleNFTCreated(
            newTokenId,
            VIN,
            make,
            model,
            licensePlate,
            year,
            stockName,
            dailyPrice
        );
        return newTokenId;
    }

    function getVehicleNFTDetails(uint256 tokenId) public view returns (Vehicle memory) {
        return _tokenDetails[tokenId];
    }
    function getFleet() public view returns (Vehicle[] memory) {
        uint256 numTokens = balanceOf(msg.sender);
        Vehicle[] memory vehicles = new Vehicle[](numTokens);
        uint256 index = 0;
        for (uint256 i = 0; i < totalSupply(); i++) {
            if (_exists(i) && ownerOf(i) == msg.sender) {
                vehicles[index] = _tokenDetails[i];
                index++;
            }
        }
        return vehicles;
    }
    function totalSupply() public view returns (uint256) {
        return _tokenIds.current();
    }
    function tokenByIndex(uint256 index) public view returns (uint256) {
        require(index < totalSupply(), "VehicleNFT: Invalid index");
        return index;
    }
    function tokenOfOwnerByIndex(address owner, uint256 index) public view returns (uint256) {
        require(index < balanceOf(owner), "VehicleNFT: Invalid index");
        uint256 count = 0;
        for (uint256 i = 0; i < totalSupply(); i++) {
            if (_exists(i) && ownerOf(i) == owner) {
                if (count == index) {
                    return i;
                }
                count++;
            }
        }
        revert("VehicleNFT: Index out of bounds");
    }
}
=======
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

