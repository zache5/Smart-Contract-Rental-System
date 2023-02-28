// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

// importing VehicleNFT contract to get the NFTs created
import "./VehicleNFT.sol";

contract RentalContract is ERC721 {
    using Counters for Counters.Counter;
    Counters.Counter private _rentalIds;

    // Importing VehicleNFT contract to get the NFTs created
    VehicleNFT private _vehicleNFT;
    // define a struct for rental info
    struct Rental {
        uint256 startDate;
        uint256 endDate;
        address renter;
        bool rented;
    }
    // map each rental with id
    mapping(uint256 => Rental) private _rentalDetails;
    // grab nft addresses for vehicles.
    constructor(address vehicleNFTAddress) ERC721("RentalContract", "RENTAL") {
        _vehicleNFT = VehicleNFT(vehicleNFTAddress);
    }
    // function for setting rental details that will verfiy if rental is available (still need logic for price and value )
    function setRentalDetails(
        uint256 tokenId,
        uint256 startDate,
        uint256 endDate,
        address renter
    ) public {
        // require(_vehicleNFT.ownerOf(tokenId) == msg.sender, "RentalContract: only NFT owner can set rental details");

        require(endDate > startDate, "RentalContract: end date must be after start date");
        require(!_rentalDetails[tokenId].rented, "RentalContract: NFT already rented");

        _rentalDetails[tokenId] = Rental({
            startDate: startDate,
            endDate: endDate,
            renter: renter,
            rented: true
        });

        _rentalIds.increment();
        uint256 newRentalId = _rentalIds.current();
        _safeMint(renter, newRentalId);
    }
    // function for viewing active rentals on select token ids showing who it is rented too. 
    function getRentalDetails(uint256 tokenId) public view returns (uint256 startDate, uint256 endDate, address renter) {
       // require(_vehicleNFT.ownerOf(tokenId) == msg.sender || ownerOf(tokenId) == msg.sender, "RentalContract: caller is not authorized");

        require(_rentalDetails[tokenId].rented, "RentalContract: NFT not on rent");

        startDate = _rentalDetails[tokenId].startDate;
        endDate = _rentalDetails[tokenId].endDate;
        renter = _rentalDetails[tokenId].renter;
    }
    // return function for nft, im thinking only owners/business should be able to return, thereby verifying that their physical vehicle has
    // actually been returned.
    function returnNFT(uint256 tokenId) public {
        // require(_vehicleNFT.ownerOf(tokenId) == msg.sender, "RentalContract: only NFT owner can return NFT");
        require(_rentalDetails[tokenId].rented, "RentalContract: NFT not rented");
        // require(block.timestamp > _rentalDetails[tokenId].endDate, "RentalContract: rental period has not yet ended");

        // Transfer the NFT back to the owner's wallet
        // _vehicleNFT.transferFrom(address(this), msg.sender, tokenId); is this needed?

        // Reset the rental details
        delete _rentalDetails[tokenId];

        // Burn the rental contract token 
        // haha guess it makes sense to use a rental token to burn? since this whole rental contract is a contrract/nft in itself 
        _burn(tokenId);
    }
}