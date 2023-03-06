import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import pandas as pd 
import datetime 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from math import sqrt
import streamlit as st
import plotly.graph_objs as go

load_dotenv()


################################################################################
# Contract Helper function:
################################################################################

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))
st.set_page_config(page_title="Rent a Moped Here", layout="wide")

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
    # Create empty lists to store vehicle details and owners
    vehicle_details_list = []
    vehicle_owners_list = []
    # Loop through the numbers from 1 to total_vehicles and get vehicle details and owners
    for i in range(1, total_vehicles+1):
        vehicle_details = NFT_contract.functions.getVehicleNFTDetails(i).call()
        vehicle_owners = NFT_contract.functions.ownerOf(i).call()
        vehicle_details_list.append(vehicle_details)
        vehicle_owners_list.append(vehicle_owners)
    # Convert the vehicle details and owners lists into DataFrames
    vehicle_df = pd.DataFrame(vehicle_details_list, columns=["VIN", "Make", "Model", "License Plate", "Year", "Stock Name", "Daily Price"])
    owner_df = pd.DataFrame(vehicle_owners_list, columns=['Owner'])
    # Combine the two DataFrames and return the result
    combined_df = pd.concat([vehicle_df, owner_df], axis=1)
    combined_df.index += 1  # Start index at 1 instead of 0
    return combined_df
# get current address fleet to see if they have bikes. 
def get_my_vehicles(address):
    # Get all vehicle data
    fleet_data = get_fleet_data()
    # Filter the vehicles owned by the given address
    my_vehicles = fleet_data.loc[fleet_data["Owner"] == address]
    if len(my_vehicles) == 0:
        st.warning("You currently do not own any vehicles. Please add a vehicle to your fleet.")
    return my_vehicles
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
    st.title("Welcome to The Smart Contract Rental System!")
    st.write("Welcome to our revolutionary new platform for renting mopeds! We're excited to introduce a cutting-edge solution that allows businesses to quickly and easily list their mopeds for rent, and renters to book directly from them. Our platform is powered by smart contract technology and blockchain, ensuring a fully decentralized, trustless transaction that's executed entirely through code. With our platform, business owners can easily add their stock of mopeds to our site and renters can browse and book rentals directly. Whether you're a business owner looking to monetize your mopeds or a renter in search of a hassle-free rental experience, our platform has everything you need. Simply head to the business tab to add your stock or the renter tab to browse rentals and start renting today!")
    if st.button("Check Rental Availability"):
        vehicle_details_df = get_fleet_data()
        st.write(vehicle_details_df)
    col1, col2 = st.columns([3,3])
    with col1:
        st.title("What is a smart contract and Why are we using this technology?")
        st.write(""""A smart contract is a self-executing computer program that automatically enforces the rules and regulations of an agreement. It allows parties to enter into a contract without the need for intermediaries such as lawyers or banks, reducing the time and costs involved in creating and enforcing traditional contracts.

In the context of a rental system, a smart contract can be used to automate the process of creating, signing, and enforcing rental agreements between parties. By using a smart contract, rental terms can be specified in code and executed automatically when certain conditions are met.

One advantage of using smart contracts in a rental system is the ability to ensure that both parties adhere to the terms of the agreement. For example, the smart contract can hold a renter's security deposit in escrow and automatically release it back to the renter once the rental period has ended and the moped is returned undamaged. This ensures that the rental company is compensated for any damages, while also protecting the renter from being unfairly charged for damages they did not cause.

Another advantage of using smart contracts in a rental system is the ability to use non-fungible tokens (NFTs) to represent ownership of the rented items. NFTs are unique digital assets that are verified on a blockchain network and can be used to represent ownership of physical or digital assets. By using NFTs to represent ownership of rented items, it becomes easier to track ownership and transfer of the items between parties. This can help prevent disputes and simplify the process of returning rented items at the end of the rental period.""")
    with col2:
        st.title("Why Should You Use This Platform?")
        st.write("When it comes to renting a moped, there are many benefits to using a platform that utilizes smart contract and blockchain technology. With this advanced technology, there is no need to rely on intermediaries, which means the transaction process is seamless and trustless. This also means the transaction is fast, efficient, and completely transparent. By using our platform, you can have peace of mind knowing that your transaction is secure and your personal information is protected. Plus, with a 10% discount compared to renting in person, you can save money while enjoying the convenience of renting from the comfort of your own home. So why settle for a traditional rental process when you can experience the future of renting with our smart contract and blockchain technology platform?")
        st.write("We can put a moped image here....")  


################################################################################
#business layout 
################################################################################
def business():
    col1, col2 = st.columns([3,3])
    with col1:    
    
        st.title('Add The Moped Vehicle Information Below!')
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
         
    with col2:
        st.header("3 Easy Steps To Add Your Mopeds to the Fleet:")
        st.write("Step 1: Add in the information about each moped in the respective text box.")
        st.write("Step 2: View the details of your fleet and 'Check Rental Status' button to see if the vehicle is currently being rented, and if it is, then by who and for how long.")
        st.write("Step 3: Once the vehicle has returned to the store sucessfully in person, then you may click the 'End Rental' button, and the vehicle will then be up for sale again and the ethereum payment will go through.")   
################################################################################
#renter layout 
################################################################################        
    
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
    with col2:
        st.header("5 Easy Steps To Rent a Moped:")
        st.write('Step 1: Fill in your contact details')
        st.write("Step 2: Select the start and end date for your rental")
        st.write("Step 3: View the available Mopeds to rent from")
        st.write("Step 4: Refer to the sidebar and select the vehicle number you want to rent")
        st.write("Input your ethereum wallet address and click pay for rental!")
        st.caption("Once you make the payment, you will see the confirmation in your wallet and the moped will be reserved for you!")
        
def predictor():
        # load data
    moped_df = pd.read_csv('./Resources/rentaldata.csv')
    # drop unnecessary columns
    moped_df = moped_df.drop(columns=['#', 'License Plate', 'Odometer at Pickup', 'Odometer at Return', 'Total Days'])


    # convert columns to datetime
    moped_df['Created At'] = pd.to_datetime(moped_df['Created At'])
    moped_df['Pickup Date'] = pd.to_datetime(moped_df['Pickup Date'])
    moped_df['Return Date'] = pd.to_datetime(moped_df['Return Date'])

    # set index as created date
    moped_df.set_index('Created At', inplace=True)
    moped_df.index.rename('Created At', inplace=True)

    # Create a new column for the number of days rented
    moped_df['Total Days'] = (moped_df['Return Date'] - moped_df['Pickup Date']).dt.days

    # Resample the data by day and sum the number of rental days for each day
    daily_rentals = moped_df['Total Days'].resample('D').sum()
    # Split data into train and test sets
    daily_rentals = daily_rentals.replace(0,1)

    train = daily_rentals.iloc[:-30]
    test = daily_rentals.iloc[-30:]

    # Build Model
    model = ARIMA(train, order=(1, 2, 3))  
    fitted = model.fit()  

    # Forecast
    forecast_values = fitted.forecast(30, alpha=0.05)  # 95% confidence interval

    # Extract required values from forecast
    fc = forecast_values[0]
    conf = forecast_values[2]
    st.write(forecast_values)
    # Make as pandas dataframe
    fc_df = pd.DataFrame(fc, columns=['forecast'], index=test.index)
    conf_df = pd.DataFrame(conf, columns=['lower_bound', 'upper_bound'], index=test.index)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=train.index, y=train, name='Training'))
    fig.add_trace(go.Scatter(x=test.index, y=test, name='Actual'))
    fig.add_trace(go.Scatter(x=fc_df.index, y=fc_df['forecast'], name='Forecast'))

    fig.add_shape(
        type='rect',
        x0=conf_df.index[0], y0=conf_df['lower_bound'][0],
        x1=conf_df.index[-1], y1=conf_df['upper_bound'][-1],
        line=dict(color='gray', width=0),
        fillcolor='gray',
        opacity=0.2
    )

    fig.update_layout(title='Forecast vs Actuals', xaxis_title='Date', yaxis_title='Value')

    st.plotly_chart(fig)
    
page_names = {
    'Home Page': intro,
    'Business': business,
    'Renter':renter,
    'Predictor':predictor
}

page = st.sidebar.selectbox("Pages", page_names.keys())
page_names[page]()

#adding this to make a change, remove if it works