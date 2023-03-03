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
        uint rentalId;
        string stockName;
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
      // function for setting rental details that will verify if rental is available and save rental details to an ERC721 token
    function setRentalDetails(
        uint256 tokenId,
        string memory stockName,
        uint256 startDate,
        uint256 endDate,
        address renter
    ) public {
        require(endDate > startDate, "RentalContract: end date must be after start date");
        require(!_rentalDetails[tokenId].rented, "RentalContract: NFT already rented");

        uint256 newRentalId = _rentalIds.current() + 1;
        _rentalIds.increment();

        Rental memory newRental = Rental({
            rentalId: newRentalId,
            stockName: stockName,
            startDate: startDate,
            endDate: endDate,
            renter: renter,
            rented: true
        });

        _rentalDetails[tokenId] = newRental;

        // Mint the new rental NFT to the renter
        _safeMint(renter, newRentalId);
    }

    // function for viewing active rentals on select token ids showing who it is rented too.
    function getRentalDetails(uint256 tokenId) public view returns (uint256 rentalId, string memory stockName, uint256 startDate, uint256 endDate, address renter) {
        require(_rentalDetails[tokenId].rented, "RentalContract: NFT not on rent");

        rentalId = _rentalDetails[tokenId].rentalId;
        stockName = _rentalDetails[tokenId].stockName;
        startDate = _rentalDetails[tokenId].startDate;
        endDate = _rentalDetails[tokenId].endDate;
        renter = _rentalDetails[tokenId].renter;
    }

    // function to return an NFT and end the rental period
    function returnNFT(uint256 tokenId) public {
        require(_rentalDetails[tokenId].rented, "RentalContract: NFT not rented");
        // require(block.timestamp > _rentalDetails[tokenId].endDate, "RentalContract: rental period has not yet ended");

        // Transfer the NFT back to the owner's wallet
        // _vehicleNFT.transferFrom(address(this), msg.sender, tokenId);

        // Burn the rental contract token
        _burn(_rentalDetails[tokenId].rentalId);

        // Reset the rental details
        delete _rentalDetails[tokenId];
    }
}