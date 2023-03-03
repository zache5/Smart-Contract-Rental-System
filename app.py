import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import pandas as pd 
import datetime 
import time
load_dotenv()
<<<<<<< HEAD
from web3 import Web3, HTTPProvider
from PIL import Image
=======

>>>>>>> 9f4d77d9e8ee4f7b3b618d49662ba1c0f4c46eab

################################################################################
# Contract Helper function:
################################################################################
# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
<<<<<<< HEAD
st.set_page_config(page_title="Rent a Moped Here", layout="wide")

=======

accounts = w3.eth.accounts
address = st.selectbox("Select account", options=accounts)

balance = w3.eth.get_balance(address)
st.write("Account balance:", w3.fromWei(balance, "ether"))
>>>>>>> 9f4d77d9e8ee4f7b3b618d49662ba1c0f4c46eab

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

# @st.cache(allow_output_mutation=True)
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
    return vehicle_df


################################################################################
# Home page, are you a renter, or a business logic. for the purpose of this, lets maybe do 
# something where we have a simple home pager with that, and seperate pages displaying what 
# the renter, and business side will look like. 
################################################################################
def intro():
    st.title("Welcome to our rental system using smart contracts!")
<<<<<<< HEAD
    st.write("Welcome to our revolutionary new platform for renting mopeds! We're excited to introduce a cutting-edge solution that allows businesses to quickly and easily list their mopeds for rent, and renters to book directly from them. Our platform is powered by smart contract technology and blockchain, ensuring a fully decentralized, trustless transaction that's executed entirely through code. With our platform, business owners can easily add their stock of mopeds to our site and renters can browse and book rentals directly. Whether you're a business owner looking to monetize your mopeds or a renter in search of a hassle-free rental experience, our platform has everything you need. Simply head to the business tab to add your stock or the renter tab to browse rentals and start renting today!")
    # image = Image.open('image.jpg')
    # st.image(image, width = 750)
    st.write("insert image here!!!!!!! .... !!!! ... !!!!!! .... !!!!! (thats our image for now :). We will make this wide so it crosses the whole screen")
    col1, col2 = st.columns([3,3])
    with col1:
        st.header("What is a smart contract and Why are we using one?")
        st.write("A smart contract is a self-executing contract that automatically enforces the terms of an agreement between parties. It is a computer program that runs on a blockchain, a decentralized and distributed digital ledger that records transactions across a network of computers. By using a smart contract on a blockchain, we can create a transparent, trustless, and secure system for renting mopeds. The blockchain technology ensures that the transaction cannot be altered, and the smart contract automates the process, eliminating the need for intermediaries. This results in a faster, cheaper, and more efficient way to rent mopeds, which benefits both the business and the renters.")
    with col2:
        st.header('Why Should you rent a moped from us?')
        st.write("When it comes to renting a moped, there are many benefits to using a platform that utilizes smart contract and blockchain technology. With this advanced technology, there is no need to rely on intermediaries, which means the transaction process is seamless and trustless. This also means the transaction is fast, efficient, and completely transparent. By using our platform, you can have peace of mind knowing that your transaction is secure and your personal information is protected. Plus, with a 10% discount compared to renting in person, you can save money while enjoying the convenience of renting from the comfort of your own home. So why settle for a traditional rental process when you can experience the future of renting with our smart contract and blockchain technology platform?")
def business():
    col1, col2 = st.columns([3,3])
    with col1:

        st.title('Add The Moped Vehicle Information Below!')
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
    with col2:
        st.header("3 Easy Steps To Add Your Mopeds to the Fleet:")
        st.write("Step 1: Add in the information about each moped in the respective text box.")
        st.write("Step 2: View the details of your fleet and 'Check Rental Status' button to see if the vehicle is currently being rented, and if it is, then by who and for how long.")
        st.write("Step 3: Once the vehicle has returned to the store sucessfully in person, then you may click the 'End Rental' button, and the vehicle will then be up for sale again and the ethereum payment will go through.")

        
    #get the stock name for bike of choice.
    def get_stock_name(token_id):
        vehicle_df = get_fleet_data()
        try:
            stock_name = vehicle_df.loc[vehicle_df.index == token_id]['Stock Name'].values[0]
            return stock_name
        except IndexError:
            return f"No vehicle found with index {token_id}"
def renter():
    col1, col2 = st.columns([3,3])
    with col1:
        st.title("Rent a Moped Here!")
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
        st.caption("Refer to the sidebar to complete your transaction")
        # Allow the user to select a vehicle from the availability list
        vehicle_index = st.sidebar.selectbox("Select a vehicle:", vehicle_details_df.index)
        renter_address = st.sidebar.text_input("Enter Ethereum address to pay from:")
        # Get the token ID for the selected vehicle
        token_id = vehicle_index
        stock_name=get_stock_name(token_id)
    with col2:
        st.header("5 Easy Steps To Rent a Moped:")
        st.write('Step 1: Fill in your contact details')
        st.write("Step 2: Select the start and end date for your rental")
        st.write("Step 3: View the available Mopeds to rent from")
        st.write("Step 4: Refer to the sidebar and select the vehicle number you want to rent")
        st.write("Input your ethereum wallet address and click pay for rental!")
        st.caption("Once you make the payment, you will see the confirmation in your wallet and the moped will be reserved for you!")
    # Set the rental details for the selected vehicle using the setRentalDetails function
    if st.sidebar.button("Pay for Rental"):
        # Check if the NFT is already rented
        is_on_rent=[]
=======
    st.write("Are you a business owner or a renter?")
    st.write("Click on corresponding page on the left.")
    

    # st.write(os.getenv("NFT_CONTRACT_ADDRESS"))    


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
    
    counter = 1
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

        
        # st.image(NFT_contract.functions.tokenURI(new_vehicle_id).call())
    # st.write(os.getenv("NFT_CONTRACT_ADDRESS"))  

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

    if st.button("Check Availability"):
        vehicle_details_df = get_fleet_data()
        st.write(vehicle_details_df)


    def purchase_nft(token_id, price):
>>>>>>> 9f4d77d9e8ee4f7b3b618d49662ba1c0f4c46eab
        try:
            # Check if the NFT exists and is available for purchase
            rental_details = get_rental_details(token_id)
            if rental_details[0] != 0:
                st.error("NFT is not available for purchase")
                return

            # Check if the rental user has enough funds
            rental_user = w3.eth.accounts[0] # Assumes rental user is using first Ethereum account
            balance = w3.eth.get_balance(rental_user)
            if balance < price:
                st.error("Rental user does not have enough funds")
                return

            # Transfer the funds to the NFT owner
            nft_owner = rental_details[1]
            tx_hash = w3.eth.send_transaction({'to': nft_owner, 'from': rental_user, 'value': price})
            st.success(f"Transaction sent: {tx_hash.hex()}")

            # Transfer the NFT to the rental user
            tx_hash = contract.functions.safeTransferFrom(nft_owner, rental_user, token_id, "").transact({'from': rental_user})
            st.success(f"Transaction sent: {tx_hash.hex()}")

            # Delete the rental details
            tx_hash = contract.functions.deleteRentalDetails(token_id).transact({'from': rental_user})
            st.success(f"Transaction sent: {tx_hash.hex()}")

        except InvalidAddress:
            st.error("Invalid Ethereum address")
        except InvalidData:
            st.error("Invalid data")
    if st.button("Purchase NFT"):
        token_id = st.number_input("Enter the token ID:", min_value=1)
            price = st.number_input("Enter the price in wei:", min_value=1)
        # call the purchase_nft() function with the input values
        purchase_nft(token_id, price)
        # display a message to confirm the purchase
        st.success("NFT purchased successfully!")

page_names = {
    'Home Page': intro,
    'Business': business,
    'Renter':renter
}
<<<<<<< HEAD
st.sidebar.header("Get Started Here!")
=======

>>>>>>> 9f4d77d9e8ee4f7b3b618d49662ba1c0f4c46eab
page = st.sidebar.selectbox("Pages", page_names.keys())
page_names[page]()