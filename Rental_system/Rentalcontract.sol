/// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
// importing VehicleNFT contract to get the NFTs created
import "./VehicleNFT.sol";

contract RentalContract is ERC721 {
    using Counters for Counters.Counter;
    Counters.Counter private _rentalIds;
    using SafeMath for uint256;

    mapping(address => uint) balances;
    // Importing VehicleNFT contract to get the NFTs created
    VehicleNFT private _vehicleNFT;

    uint256 private _balance;
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
        uint256 endDate
    ) public payable {
        require(endDate > startDate, "RentalContract: end date must be after start date");
        require(!_rentalDetails[tokenId].rented, "RentalContract: NFT already rented");
        
        // calculate total rental fee based on duration and daily price
        // Calculate the total cost of the rental
        uint256 rentalDays = endDate.sub(startDate).div(86400); // Divide by number of seconds in a day
        uint256 totalRentalFee = rentalDays * _vehicleNFT.dailyPricevalue(tokenId);

        // ensure user has sent enough ether for rental fee
        require(msg.value >= totalRentalFee, "RentalContract: insufficient payment");
        // balances[msg.sender] -= totalRentalFee;
        // // transfer rental fee to contract
        _balance += totalRentalFee;
    
        // _balance = address(this).balance;
        // create new rental with details
        uint256 newRentalId = _rentalIds.current() + 1;
        _rentalIds.increment();

        Rental memory newRental = Rental({
            rentalId: newRentalId,
            stockName: stockName,
            startDate: startDate,
            endDate: endDate,
            renter: msg.sender,
            rented: true
        });
        // balances[_vehicleNFT.ownerOf(tokenId)] += totalRentalFee;
        _rentalDetails[tokenId] = newRental;
        // Transfer the total cost of the rental to the contract
        // address payable contractAddress = payable(address(this));
        // contractAddress.transfer(totalRentalFee);
        // Mint the new rental NFT to the owner of the vehicle NFT
        address owner = _vehicleNFT.ownerOf(tokenId);
        _safeMint(owner, newRentalId);
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
    function returnNFT(uint256 tokenId, uint256 endDate, uint256 startDate) public {
        require(_rentalDetails[tokenId].rented, "RentalContract: NFT not rented");
        require(msg.sender == _vehicleNFT.ownerOf(tokenId), "You are not the Owner of this vehicle!");
        // Transfer the NFT back to the owner's wallet
        // calculate total rental fee based on duration and daily price
        uint256 rentalDays = endDate.sub(startDate).div(86400); // Divide by number of seconds in a day
        uint256 totalRentalFee = rentalDays * _vehicleNFT.dailyPricevalue(tokenId);
        // transfer rental fee to contract
        address payable vehicleOwner = payable(_vehicleNFT.ownerOf(tokenId));
        vehicleOwner.transfer(totalRentalFee);
        // Burn the rental contract token
        _burn(_rentalDetails[tokenId].rentalId);
        // Reset the rental details
        delete _rentalDetails[tokenId];
    }
    receive() external payable {
    // code to handle received ether
    }   
}