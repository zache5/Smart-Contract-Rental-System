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

# @st.cache(allow_output_mutation=True) - code does not refresh newly added vehicles with this. 
def get_fleet_data():
    # Get total number of vehicles in the fleet
    total_vehicles = NFT_contract.functions.totalSupply().call()
    # Create an empty list to store vehicle details
    vehicle_details_list = []
    # Loop through the numbers from 1 to total_vehicles and get vehicle details
    for i in range(1, total_vehicles+1):
        vehicle_details = NFT_contract.functions.getVehicleNFTDetails(i).call()
        vehicle_details_list.append(vehicle_details)
    # Convert the vehicle details list into a DataFrame
    vehicle_df = pd.DataFrame(vehicle_details_list, columns=["VIN", "Make", "Model", "License Plate", "Year", "Stock Name", "Daily Price"])
    vehicle_df.index = vehicle_df.index +1
    return vehicle_df

#get the stock name for bike of choice.        
def get_stock_name(token_id):
        vehicle_df = get_fleet_data()
        try:
            stock_name = vehicle_df.loc[vehicle_df.index == token_id]['Stock Name'].values[0]
            return stock_name
        except IndexError:
            return f"No vehicle found with index {token_id}"   
        
@st.cache(allow_output_mutation=True)
def save_rental_details_to_dataframe(first_name, last_name, email, phone_number, stock_name, rental_id, start_date, end_date):
    rental_data = {
        "First Name": [first_name],
        "Last Name": [last_name],
        "Email": [email],
        "Phone Number": [phone_number],
        "Stock Name": [stock_name],
        "Rental ID": [rental_id],
        "Start Date": [start_date],
        "End Date": [end_date]
    }
    rental_df = pd.DataFrame(data=rental_data)
    return rental_df 

################################################################################
# Home page, are you a renter, or a business logic. for the purpose of this, lets maybe do 
# something where we have a simple home pager with that, and seperate pages displaying what 
# the renter, and business side will look like. 
################################################################################
def intro():
    st.title("Welcome to our rental system using smart contracts!")
    st.write("Are you a business owner or a renter?")
    st.write("Click on corresponding page on the left.")
  
    # st.write(os.getenv("NFT_CONTRACT_ADDRESS"))    


    if st.button("Check Availability"):
        vehicle_details_df = get_fleet_data()
        st.write(vehicle_details_df)
################################################################################
#business layout 
################################################################################
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
        tx_hash = receipt.transactionHash.hex()

        # Get the ID of the newly minted vehicle
        event_filter = NFT_contract.events.VehicleNFTCreated.createFilter(fromBlock="latest")
        events = event_filter.get_all_entries()
        new_vehicle_id = events[-1]['args']['tokenId']

        # Show the user the newly minted vehicle
        st.write("The Vehicle has been added to your fleet. Here are the details for your vehicle:")
        supply_number = NFT_contract.functions.totalSupply().call()
        nft_details = NFT_contract.functions.getVehicleNFTDetails(supply_number).call()
        st.write("Vehicle details:")
        st.write("VIN:", nft_details[0])
        st.write("Stock Name:", nft_details[5])

        st.write(f"Transaction receipt mined. The transaction hash is:{tx_hash}")
        
     # Check rental status section
    st.header("Check Rental Status")
    vehicle_details_df = get_fleet_data()
    st.write("Here are the details of your fleet:")
    st.write(vehicle_details_df)
    vehicle_index = st.selectbox("Select a vehicle:", vehicle_details_df.index)
    
    vehicle_id = int(vehicle_index)
    
        
    if st.button("Check Rental Status"):
        try:
            rental_details = rental_contract.functions.getRentalDetails(vehicle_id).call()
            if rental_details:
                rentalid,stock_name, start_unix, end_unix, renter_address = rental_details
                start_time = datetime.datetime.fromtimestamp(int(start_unix))
                end_time = datetime.datetime.fromtimestamp(int(end_unix))
                st.write("Rental details:")
                st.write(f"Rental # : {rentalid}")
                st.write(f"Vehicle rented : {stock_name}")
                st.write(f"Renter address: {renter_address}")
                st.write(f"Start time: {start_time}")
                st.write(f"End time: {end_time}")
            else:
                st.write(f"Vehicle with id {vehicle_id} is not currently rented.")
                st.write("Please select another vehicle.")
                return
        except Exception as e:
            # st.error(f"Error checking rental status: {e}")
            st.write(f"Vehicle with id {vehicle_id} is not currently rented.")
            st.write("Please select another vehicle.")
            pass
    
        # End Rental Section
    st.header("End Rental")

    # Create a button to end the rental
    if st.button("End Rental"):
        # Retrieve the rental ID associated with the vehicle
        rental_id = rental_contract.functions.getRentalDetails(vehicle_id).call()

        # End the rental using the rental ID
        try:
            # Call the returnNFT() function in the smart contract
            tx_hash = rental_contract.functions.returnNFT(vehicle_id).transact(({'from': address, 'gas': 1000000}))
            st.success("Rental ended successfully!")
        except Exception as e:
            st.error(f"Error ending rental: {e}")
         
        
################################################################################
#renter layout 
################################################################################        
    
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

    st.write("Check Availability below!")
    vehicle_details_df = get_fleet_data()
    st.write(vehicle_details_df)

    # Allow the user to select a vehicle from the availability list
    vehicle_index = st.sidebar.selectbox("Select a vehicle:", vehicle_details_df.index)
 
    renter_address = st.sidebar.text_input("Enter Ethereum address to pay from:")
    

    # Get the token ID for the selected vehicle
    token_id = vehicle_index
    stock_name=get_stock_name(token_id)
    

    # Set the rental details for the selected vehicle using the setRentalDetails function
    renter_info = ','.join([first_name, last_name, email])
    if st.sidebar.button("Pay for Rental"):
        # Check if the NFT is already rented
        is_on_rent=[]
        try:
            
            is_on_rent = rental_contract.functions.getRentalDetails(token_id).call()
        except Exception as e:
            pass
        if is_on_rent:
            st.error("This vehicle is already on rent, Please select a different vehicle.")
        else:
            tx_hash = rental_contract.functions.setRentalDetails(token_id,stock_name, renter_info, start_unix, end_unix, renter_address).transact({'from': address, 'gas': 1000000})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
            tx_hash = receipt.transactionHash.hex()
            # Show rental confirmation to user
            st.write("You have successfully rented the following vehicle:")
            st.write("- Vehicle: ", vehicle_index)
            st.write("- Rental Address: ", renter_address)
            rental_details = rental_contract.functions.getRentalDetails(token_id).call()
            st.write("- Rental #: ", rental_details[0])
            #save renter information in dataframe 
            rental_id = rental_details[0]
            rental_df = save_rental_details_to_dataframe(first_name, last_name, email, phone_number, stock_name, rental_id, start_date, end_date)
            st.write(rental_df)
            
        
    
    
page_names = {
    'Home Page': intro,
    'Business': business,
    'Renter':renter
}

page = st.sidebar.selectbox("Pages", page_names.keys())
page_names[page]()

#adding this to make a change, remove if it works