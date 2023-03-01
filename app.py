import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import pandas as pd 
import datetime 

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

# helper function getting all minted nfts on NFT contract

@st.cache(allow_output_mutation=True)
def get_fleet_data():
    # Get all vehicles in the fleet
    vehicles = NFT_contract.functions.getFleet().call()
    # Convert the vehicles list into a DataFrame
    vehicle_df = pd.DataFrame(vehicles)
    vehicle_df.index=vehicle_df.index+1
    vehicle_details_list=[]
    # get missing vehicle info after first call.
    for index in vehicle_df.index:
        vehicle_details = NFT_contract.functions.getVehicleNFTDetails(index).call()
        vehicle_details_list.append(vehicle_details)
    # add columns to all vehicles and return df
    vehicle_details_df = pd.DataFrame(vehicle_details_list, columns=["VIN", "Make", "Model", "License Plate", "Year", "Stock Name", "Daily Price"])
    return vehicle_details_df


################################################################################
# Home page, are you a renter, or a business logic. for the purpose of this, lets maybe do 
# something where we have a simple home pager with that, and seperate pages displaying what 
# the renter, and business side will look like. 
################################################################################
def intro():
    st.title("Welcome to our rental system using smart contracts!")
    st.write("Are you a business owner or a renter?")
    st.write("Click on corresponding page on the left.")
    
  
    st.write(os.getenv("NFT_CONTRACT_ADDRESS"))    


    if st.button("Check Availability"):
        vehicle_details_df = get_fleet_data()
        st.write(vehicle_details_df)

def business():
    st.title('Welcome to our rental system! please add some business information')
   
    
    st.write("Lets add some vehicles to your virtual fleet, start by adding the information assiociated with a vehicle")
    vin = st.text_input("Enter the VIN of the vehicle")
    make = st.text_input("Enter the make of the vehicle")
    model = st.text_input("Enter the model of the vehicle")
    license_plate = st.text_input("Enter the license plate of the vehicle")
    year = st.number_input("Enter the year of the vehicle", min_value=1900, max_value=2100)
    stock_name = st.text_input("Enter the stock name of the vehicle")
    daily_price = int(st.number_input("Enter the daily rental price of the vehicle"))
    
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
    st.write(os.getenv("NFT_CONTRACT_ADDRESS"))  
    
def renter():
    st.title("Welcome to our rental system using smart contracts!")
    
    st.write("Please enter your information below to get started.")
    
    # Get renter information
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
    email = st.text_input("Email")
    phone_number = st.text_input("Phone Number")
    
    st.write("Please select the dates you would like to rent:")
    
    # Display a calendar for selecting rental dates
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    
    # Convert selected dates to Unix timestamps
    start_unix = int(datetime.datetime.combine(start_date, datetime.time.min).timestamp())
    end_unix = int(datetime.datetime.combine(end_date, datetime.time.min).timestamp())
    
    # Display renter information and selected rental dates
    st.write(f"Name: {first_name} {last_name}")
    st.write(f"Email: {email}")
    st.write(f"Phone Number: {phone_number}")
    st.write(f"Rental Dates: {start_unix} to {end_unix}")
    
page_names = {
    'Home Page': intro,
    'Business': business,
    'Renter':renter
}

page = st.sidebar.selectbox("Pages", page_names.keys())
page_names[page]()