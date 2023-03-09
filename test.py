import os
import json
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import pandas as pd 
import datetime 
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
import streamlit as st
import plotly.graph_objs as go
import boto3
import psycopg2 
import sys
from io import StringIO
from io import BytesIO


load_dotenv()

################################################################################
# Contract Helper function:
################################################################################

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

s3 = boto3.client('s3',
                  aws_access_key_id= os.getenv('aws_access_key_id'),
                  aws_secret_access_key=os.getenv('aws_secret_access_key'))
def upload_to_s3(bucket_name, file_name, data):
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=data)
    print(f"File {file_name} uploaded successfully to S3 bucket {bucket_name}.")
bucket_name = 'rentalinfo'

# functions for uploading and then getting data from the s3 bucket database. 
def upload_dataframe_to_s3(bucket_name, rental_id, df):
    file_name = f"Rental # {rental_id}.csv"
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue().encode())
    print(f"File {file_name} uploaded successfully to S3 bucket {bucket_name}.")
    
def query_s3_data(bucket_name, file_name):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket_name, Key=file_name)
    data = obj['Body'].read()
    df = pd.read_csv(BytesIO(data))
    return df
    
# connect to ganache accounts
accounts = w3.eth.accounts
address = st.sidebar.selectbox("Select account", options=accounts)

balance = w3.eth.get_balance(address)
st.sidebar.write("Account balance:", w3.fromWei(balance, "ether"))

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

# check if bikes are on rent and return two dataframes, one for on rent and one for not. 
def get_rental_status(fleet_data):
    on_rent_df = pd.DataFrame(columns=["First Name", "Last Name", "Email","Phone Number","Stock Name","Rental ID", "Start Date", "End Date"])
    not_on_rent_df = pd.DataFrame(columns=["VIN", "Make", "Model", "License Plate", "Year", "Stock Name", "Daily Price", "Owner"])
    for i, vehicle in fleet_data.iterrows():
        try:
            rental_details = rental_contract.functions.getRentalDetails(i).call()
            rental_id, stock_name,start_unix, end_unix, renter_addy = rental_details
            file_name = f"Rental # {rental_id}.csv"
            df = query_s3_data(bucket_name, file_name)                
            on_rent_df = on_rent_df.append(df)
        except :            
            not_on_rent_df = not_on_rent_df.append(vehicle)
            pass
            
    return on_rent_df, not_on_rent_df
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
        
# function for saving rental details to df
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
    st.caption('Come Ride around oahu and experience the island on two wheels!')
    image = open("./Images/front_page.jpg", "rb").read()
    st.image(image, use_column_width=True, output_format='JPEG',)
    st.caption('Photo is taken out by Makapuu lighthouse beach park.')

    


################################################################################
#business layout 
################################################################################
def business():
    col1, col2 = st.columns([3,3])
    with col1:
        
         # Check rental status section
        st.header("Check Rental Status for rented vehicles below")
        vehicle_details_df = get_my_vehicles(address)  
        
        if not vehicle_details_df.empty:
            on_rent_df, not_on_rent_df = get_rental_status(vehicle_details_df)
            # Loop over rows and grab specified columns
#             for index, row in on_rent_df.iterrows():
#                 stock_name = row['Stock Name']
#                 rental_id = row['Rental ID']
#                 start_date = row['Start Date']
#                 end_date = row['End Date']
#                 first_name = row['First Name'].capitalize()
#                 phone_number = row['Phone Number']
#                 email= row['Email']

#                 # Do something with the information, for example print it
#                 st.write(f'{stock_name} Is currently on rent to {first_name} with rental number #{rental_id}. This rental is/was picked up on {start_date} and returns {end_date}, the phone number for this customer is -{phone_number}, and their email address is -{email}.')
                
            st.write('Here is a quick glance at your on rent vehicles, select the vehicle ID below to end the rental')
            st.write(on_rent_df)
            vehicle_index = st.selectbox("Select a vehicle:", vehicle_details_df['Stock Name'])
            # Find the index of the row that corresponds to the selected stock name
            selected_index = vehicle_details_df.loc[vehicle_details_df['Stock Name'] == vehicle_index].index[0]
            selected_index=int(selected_index)

            # vehicle_id = int(vehicle_index)
            # End Rental Section
            st.header("End Rental")

            # Create a button to end the rental
            if st.button("End Rental"):
                # Retrieve the rental ID associated with the vehicle
                rental_id, stock_name, start_date, end_date, renter_addy = rental_contract.functions.getRentalDetails(selected_index).call()
                
                # End the rental using the rental ID
                try:
                    # Call the returnNFT() function in the smart contract
                    tx_hash = rental_contract.functions.returnNFT(selected_index, end_date,start_date).transact(({'from': address, 'gas': 1000000}))
                    st.success("Rental ended successfully!")
                except Exception as e:
                    st.error(f"Error ending rental: {e}")
                    pass

            else:
                #if no vehicles pass, and show them code for adding vehicles.
                selected_index = None
                pass

                
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
            for vehicle_id in vehicle_details_df:
                vehicle_details = NFT_contract.functions.getVehicleDetails(vehicle_id).call()
                if vehicle_details[0] == vin or vehicle_details[3] == license_plate:
                     st.error("Error: A vehicle with the same VIN or license plate already exists in the fleet.")


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

    with col2:
        st.header("Check available vehicles below")
        if not vehicle_details_df.empty:
            st.write(not_on_rent_df)
            st.subheader('Here is your whole fleet of vehicles:')
            st.write(vehicle_details_df)
        else :
            pass
        
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
        vehicle_details_df = get_fleet_data()
        # Allow the user to select a vehicle from the availability list
        vehicle_index = st.selectbox("Select a vehicle:", vehicle_details_df.index)
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
        
        # renter_address = st.sidebar.text_input("Enter Ethereum address to pay from:")
        

        # Get the token ID for the selected vehicle
        token_id = vehicle_index
        stock_name=get_stock_name(token_id)
        

        # Set the rental details for the selected vehicle using the setRentalDetails function
        renter_info = ','.join([first_name, last_name, email])
                
    with col2:
        st.header("Check Availability below!")
        onrent, available_df = get_rental_status(vehicle_details_df)
        st.write(available_df)
        st.header("5 Easy Steps To Rent a Moped:")
        st.write('Step 1: Fill in your contact details')
        st.write("Step 2: Select the start and end date for your rental")
        st.write("Step 3: View the available Mopeds to rent from")
        st.write("Step 4: Refer to the sidebar and select the vehicle number you want to rent")
        st.write("Input your ethereum wallet address and click pay for rental!")
        st.caption("Once you make the payment, you will see the confirmation in your wallet and the moped will be reserved for you!")
        rental_days = (end_unix-start_unix)/86400
        daily_price= NFT_contract.functions.dailyPricevalue(vehicle_index).call()
        rental_cost = int(rental_days * daily_price)
        # Convert eth amount to Wei
        ether = w3.fromWei(rental_cost, "ether")
        st.subheader(f'You can expect to pay {ether} ETH for the rental for {rental_days} days')
        if st.button("Pay for Rental"):
            # Check if the NFT is already rented
            is_on_rent=[]
            try:

                is_on_rent = rental_contract.functions.getRentalDetails(token_id).call()
            except Exception as e:
                pass
            if is_on_rent:
                st.error("This vehicle is already on rent, Please select a different vehicle.")
            else:
                try:
                    if not first_name.strip():
                        raise ValueError("First Name is empty. Please enter your first name.")
                    if not last_name.strip():
                        raise ValueError("Last Name is empty. Please enter your last name.")
                    if not email.strip():
                        raise ValueError("Email is empty. Please enter a valid email.")
                    if not phone_number.strip():
                        raise ValueError("Phone Number is empty. Please enter a valid phone number.")
                    tx_hash = rental_contract.functions.setRentalDetails(token_id,stock_name, start_unix, end_unix).transact({'from': address, 'gas': 2000000, 'value': rental_cost})
                    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
                    tx_hash = receipt.transactionHash.hex()
                    # Show rental confirmation to user
                    st.write("You have successfully rented the following vehicle:")
                    st.write("- Vehicle: ", vehicle_index)
                    st.write("- Rental Address: ", address)
                    rental_details = rental_contract.functions.getRentalDetails(token_id).call()
                    st.write("- Rental #: ", rental_details[0])
                    st.write("- Transaction hash for rental:" ,tx_hash)
                    #save renter information in dataframe 
                    rental_id = rental_details[0]
                    rental_df = save_rental_details_to_dataframe(first_name, last_name, email, phone_number, stock_name, rental_id, start_date, end_date)
                    st.write(rental_df)
                    upload_dataframe_to_s3('rentalinfo', rental_id, rental_df)
                    st.balloons()
                except ValueError as e:
                    st.warning(str(e))
        
        
    
################################################################################
#anaylsis layout 
################################################################################        
    
        
def analysis():
    st.title('Business Analysis')
    st.subheader('Before uploading your CSV file, please make sure that the file has columns name such as "Pickup Date" and "Return Date"')
    st.write('Upload your csv file')


    uploaded_file = st.file_uploader(
        "",
        key="1")

    if uploaded_file is not None:
        # file_container = st.expander("Check your uploaded .csv")
        df = pd.read_csv(uploaded_file)
        # uploaded_file.seek(0)
        # file_container.write(df)

        # Get date range for filtering
        min_date = pd.to_datetime(df['Pickup Date']).min().date()
        max_date = pd.to_datetime(df['Return Date']).max().date()
        start_date = st.date_input('Select start date:', value=min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input('Select end date:', value=max_date, min_value=min_date, max_value=max_date)

        # Filter the dataframe by selected date range for pickups and returns
        pickups_df = df[(pd.to_datetime(df['Pickup Date']).dt.date >= start_date) & (pd.to_datetime(df['Pickup Date']).dt.date <= end_date)]
        returns_df = df[(pd.to_datetime(df['Return Date']).dt.date >= start_date) & (pd.to_datetime(df['Return Date']).dt.date <= end_date)]

        # Calculate counts for pickups and returns for each day in the range
        date_counts = []
        for date in pd.date_range(start_date, end_date):
            pickups_count = pickups_df[(pd.to_datetime(pickups_df['Pickup Date']).dt.date == date)].shape[0]
            returns_count = returns_df[(pd.to_datetime(returns_df['Return Date']).dt.date == date)].shape[0]
            date_counts.append((date, pickups_count, returns_count))

        # # Create a dataframe with the counts for each day in the range
        counts_df = pd.DataFrame(date_counts, columns=['Date', 'Pickups', 'Returns'])

        # st.subheader(f"Moped counts for selected date range")
        # st.write(counts_df)

        # Display the chart
        fig = px.line(counts_df, x='Date', y=['Pickups', 'Returns'], labels={'x':'Date', 'y':'Count'})
        st.plotly_chart(fig)



        gb = GridOptionsBuilder.from_dataframe(df)
        # enables pivoting on all columns, however need to change ag grid to allow export of pivoted/grouped data
        gb.configure_selection(selection_mode="multiple", use_checkbox=True)
        gb.configure_side_bar()  
        gridOptions = gb.build()

        response = AgGrid(
        df,
        gridOptions=gridOptions,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=False,
        )

        df = pd.DataFrame(response["selected_rows"])

        st.subheader("Filtered data will appear below ")
        st.text("")

        st.table(df)

        st.text("")

        c29, c30, c31 = st.columns([1, 1, 2])

        if st.button('Would you like to run a forecats?'):
            df = pd.read_csv(uploaded_file)
            uploaded_file.seek(0)
            file_container.write(df)
            df = df.drop(columns=['#','Created At','Return Date', 'License Plate', 'Odometer at Pickup', 'Odometer at Return', 'Total Days'])
            df.dropna(inplace=True)
            # Convert columns to datetime
            df['Pickup Date'] = pd.to_datetime(df['Pickup Date'])
            # Create new column
            df['Pickup Count'] = df.groupby(df['Pickup Date'].dt.date)['Pickup Date'].transform('count')
            # Sorting by Pickup Date
            df.sort_values('Pickup Date', inplace=True)
            # Preparing to fit Prophet
            df_train = df[['Pickup Date','Pickup Count']]
            df_train = df.rename(columns={'Pickup Date': 'ds', 'Pickup Count': 'y'})

            # Initialize the model
            model = Prophet()
            # Fitting the model
            model.fit(df_train)
            # Create future dataframe, 30 days ahead
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)

            st.write('Forecast Data')
            fig = plot_plotly(model,forecast)
            st.plotly_chart(fig)

            st.write('Forecast components')
            fig2 = model.plot_components(forecast)
            st.write(fig2)
    
page_names = {
    'Home Page': intro,
    'Business': business,
    'Renter':renter,
    'Analysis':analysis
}

page = st.sidebar.selectbox("Pages", page_names.keys())
page_names[page]()
