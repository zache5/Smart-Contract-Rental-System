# Smart Contract Rental System
**Project 3 for Fintech bootcamp through UC Berkeley.**

# Project Description
...


## Package Requirements and versions
First before installing any packages and getting setup make sure you are in a `dev` environment or an environment you are comfortable downloading packages into. If you don't know what a `dev` environment is follow along below. 
To get your `dev` environment setup do the following in your command line:

- Creating a dev environment for python 3.7 called 'dev' - if you do not already have an environment setup 
    - Get setup in your preferred CLI (Gitbash, terminal, etc)
    - `conda create -n dev python=3.7 anaconda`
    - Once you have created the environment, type the following to activate and deactivate.
    ### To activate: `conda activate dev`
    ### To deactivate: `conda deactivate dev`

Once you have cloned the repo and have a `dev` or similar env with python 3.7 or higher the next step is to make sure you have the packages installed locally. Navigate to the newly cloned repo and make sure you are in the right directory. 
Then type `pip install requirements.txt`, this will install any necessary packages to your env. 

*NOTE if you get errors installing requirements with ta-lib, use conda install -c conda-forge ta-lib"*

## File Navigation
- `App.py` -- File used for deplyoing code to streamlit website
- `Rental_system` -- The folder contains our smart contracts that were created through Solidity and is connected with `Ganache` with `MetaMask` to deploy the smart contract.

## Usage Streamlit Dashboard
To get streamlit running locally and to start browsing the site, start by making sure your `dev` env is running and has the `requirements.txt` installed. Finally, inside your preferred CLI make sure you in the right directory with the `Main.py` file, and type the following command - ` streamlit run Main.py` -. You should see the terminal run some code and a website with a local host IP address will pop up on your terminal.

## Contributors
[Robin Thorsen](https://www.linkedin.com/in/robin-thorsen-079819120/), [Kaio Farkouh](https://www.linkedin.com/in/kaio-farkouh/), [Zach Eras](https://www.linkedin.com/in/zachary-eras-24b5a8149/) are the developers/analysts who worked on this project.