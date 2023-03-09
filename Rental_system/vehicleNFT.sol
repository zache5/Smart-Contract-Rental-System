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
    function dailyPricevalue(uint256 tokenId) public view returns (uint256) {
    // retrieve the Vehicle struct for the specified token ID
        Vehicle memory vehicle = _tokenDetails[tokenId];

    // return the dailyPrice field of the Vehicle struct
    return vehicle.dailyPrice;
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