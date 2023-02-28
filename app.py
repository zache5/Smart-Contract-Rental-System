import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

load_dotenv()


################################################################################
# Contract Helper function:
################################################################################

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

accounts = w3.eth.accounts
address = st.selectbox("Select account", options=accounts)

balance = w3.eth.get_balance(address)
st.write("Account balance:", w3.fromWei(balance, "ether"))

@st.cache(allow_output_mutation=True)
def load_contract(path, addy):

    # Load the contract ABI
    with open(Path(path)) as f:
        _abi = json.load(f)

    contract_address = os.getenv(addy)

    # Load the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=_abi
    )

    return contract

NFT_contract = load_contract('./Rental_system/compiled/vehicleNFT_abi.json', 'NFT_CONTRACT_ADDRESS')
rental_contract = load_contract('./Rental_system/compiled/rental_abi.json', 'RENTAL_CONTRACT_ADDRESS')


################################################################################
# Home page, are you a renter, or a business logic. for the purpose of this, lets maybe do 
# something where we have a simple home pager with that, and seperate pages displaying what 
# the renter, and business side will look like. 
################################################################################

st.title("Welcome to our rental system using smart contracts!")
st.write("Are you a business owner or a renter?")

st.write("Business Owner")
st.write("You are a business owner")
vin = st.text_input("Enter the VIN of the vehicle")
make = st.text_input("Enter the make of the vehicle")
model = st.text_input("Enter the model of the vehicle")
license_plate = st.text_input("Enter the license plate of the vehicle")
year = st.number_input("Enter the year of the vehicle", min_value=1900, max_value=2100)
stock_name = st.text_input("Enter the stock name of the vehicle")
daily_price = int(st.number_input("Enter the daily rental price of the vehicle"))
# address = st.text_input("Enter the address to mint the vehicle with")

if st.button("Add Vehicle"):
    # Check if the VIN or license plate already exists in the fleet
    # existing_vehicles = NFT_contract.functions.getFleet().call()
    # for vehicle_id in existing_vehicles:
    #     vehicle_details = NFT_contract.functions.getVehicleDetails(vehicle_id).call()
    #     if vehicle_details[0] == vin or vehicle_details[3] == license_plate:
    #         st.error("Error: A vehicle with the same VIN or license plate already exists in the fleet.")
        

    # Add the vehicle to the fleet
    tx_hash = NFT_contract.functions.createVehicleNFT(vin, make, model, license_plate, year, stock_name, daily_price).transact({'from': address, 'gas': 1000000})
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    st.write("Transaction receipt mined:")
    st.write(dict(receipt))

    # Get the ID of the newly minted vehicle
    event_filter = NFT_contract.events.VehicleNFTCreated.createFilter(fromBlock="latest")
    events = event_filter.get_all_entries()
    new_vehicle_id = events[-1]['args']['tokenId']

    # Show the user the newly minted vehicle
    st.write("Vehicle added to your fleet:")
    # st.image(NFT_contract.functions.tokenURI(new_vehicle_id).call())

if st.button("Renter"):
    st.write("You are a renter")
    # Display rental options and allow the renter to select a vehicle to rent
st.write(os.getenv("NFT_CONTRACT_ADDRESS"))