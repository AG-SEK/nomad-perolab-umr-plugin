
# Imports
import json
import os
from datetime import datetime, timedelta
from getpass import getpass

import requests

# Base URL NOMAD Oasis
oasis_base_url = 'https://vhrz1634.hrz.uni-marburg.de/nomad-oasis/api/v1'
#oasis_base_url = 'https://solar-oasis.hrz.uni-marburg.de/nomad-oasis/api/v1'






def get_new_app_token(days_until_expiration, auth_header, base_url=oasis_base_url):
    """
    Generates a new App Token by making an API request to the specified endpoint. 
    The token is valid for the specified number of days, and the expiration date 
    is included in the response.

    Parameters:
    - days_until_expiration (int): The number of days from the current date until the expiration of the new App Token.
    - auth_header (dict): A dictionary containing the authentication header (e.g., {'Authorization': 'Bearer <token>'}).
    - base_url (str, optional): The base URL of the API to make the request. Defaults to the value of `oasis_base_url`.

    Returns:
    - dict: A dictionary containing the new App Token and its expiration date, 
            or None if the API request failed (e.g., due to validation error).
    """
            
    print("Generating new App Token...")

    # Calculate expiration date
    expiration_date = datetime.now() + timedelta(days=days_until_expiration)

    # API Request
    endpoint = '/auth/app_token'
    url = f'{base_url}{endpoint}'
    params = dict(
        expires_in = days_until_expiration*24*60*60 # in seconds
    )
    response = requests.get(url, headers=auth_header, params=params)

    # Print API Response Information
    print(response)
    if response.status_code == 200:
        print("Successful Response")
    elif response.status_code == 422:
        print("Validation Error")
        return None
    
    # Parse API Response JSON
    app_token_dict = response.json()
    # Convert expiration date into String and add it to dictionary
    expiration_date_str = expiration_date.strftime("%Y-%m-%d")
    app_token_dict['expiration_date'] = expiration_date_str

    return app_token_dict



# Authentication with App Token
def get_authentication_header_with_app_token():
    """
    Authenticates with an App Token by loading a JSON file containing app tokens and their expiration dates. 
    It checks whether each token is still valid, removes expired tokens, and generates a new token 
    if one is about to expire within 10 days. The function returns an authentication header with a valid 
    app token for API requests.

    The function performs the following steps:
    1. Loads app token information from a JSON file.
    2. Iterates over the list of app tokens and checks their expiration dates.
    3. Removes expired app tokens from the list and updates the JSON file.
    4. If an app token is valid but will expire in 10 days or less, a new token is generated.
    5. Returns an authentication header with a valid app token for use in API requests.

    Returns:
    - dict: A dictionary containing the authorization header (e.g., {'Authorization': 'Bearer <app_token>'}).
    """
    
    # Construct path to json file 
    current_module_path = os.path.dirname(os.path.abspath(__file__))              # Path to this module
    parent_path = os.path.abspath(os.path.join(current_module_path, "../../"))    # Go two directories up
    path_to_json_file = os.path.join(parent_path, 'nomad_oasis_app_token.json' )  # In this json file the app token is stored

    # Import JSON file with App Tokens as list
    with open(path_to_json_file) as file:
        app_token_json_list = json.load(file)

    # Create Copy of List because when deleting items during iteration problems occur (indices are changed)
    app_token_json_list_copy = app_token_json_list

    # Iterate through all App Tokens and 
    for app_token_json in app_token_json_list_copy:
        app_token = app_token_json.get('app_token')
        expiration_date_str = app_token_json.get('expiration_date')
        
        # Check if app_token and expiration_date are available
        if not app_token or not expiration_date_str:
            print("ERROR: 'app_token' oder 'expiration_date' are missing in the json file. Please check and if neccessary add an app token manually!")
            return

        # Convert expiration date string to datetime object
        expiration_date = datetime.strptime(expiration_date_str, "%Y-%m-%d")
        current_date = datetime.now()
        remaining_days =(expiration_date.date()-current_date.date()).days  # .date() -> only use date, not time
        
        # Delete Tokens, which are not valid anymore and save changes in JSON file
        if remaining_days < 0:
            app_token_json_list.remove(app_token_json)
            with open(path_to_json_file, 'w') as file:
                json.dump(app_token_json_list, file, indent=4)
            print(f"Removed old app token. Was not valid anymore. The expiration date was: {expiration_date.date()}.")
            print("Please add a new app token manually. (via GUI -> API -> App Token)")

        # If App Token expires in less than 10 days, generate new App Token, but also return auth_header
        elif remaining_days <= 10:
        
            # Create Authentication Header
            auth_header = {'Authorization': f'Bearer {app_token}'}
            print(f"App Token will expire soon. (Expiration date: {expiration_date_str} - Remaining Days: {remaining_days}")

            # Get a new app token
            new_app_token_json = get_new_app_token(30, auth_header)
            new_expiration_date = new_app_token_json['expiration_date']
            
            # Append to list and save changes in JSON file
            app_token_json_list.append(new_app_token_json)
            with open(path_to_json_file, 'w') as file:
                json.dump(app_token_json_list, file, indent=4)
            print(f"New App Token was generated (New expiration date: {new_expiration_date.date()})")

            # Delete old App Token
            app_token_json_list.remove(app_token_json)
            with open(path_to_json_file, 'w') as file:
                json.dump(app_token_json_list, file, indent=4)
            print("Old App Token was deleted.")

            return auth_header
        
        # If valid for more than 10 days return auth_header
        elif remaining_days > 10:
            
            # Create Authentication Header
            auth_header = {'Authorization': f'Bearer {app_token}'}
            print(f"App Token is valid. Expiration date: {expiration_date.date()}")
            return auth_header
        




def get_authentication_header_with_password(base_url=oasis_base_url, username=None):
    """
    Method to retrieve an access code by giving username and password.
    The acces token can be used on subsequent API calls to authenticate you in an HTTP Authorization
    header like this: Authorization: Bearer <access token>. This method already returns the correct header.
    """
    username = username if username is not None else input('Please enter your username')
    
    # API Call
    endpoint = '/auth/token'
    url = f'{base_url}{endpoint}'
    params = dict(
        username = username,
        password = getpass('Please enter your passsword')
        )
    response = requests.get(url, params = params)
    
    # Response
    print(response)
    if response.status_code == 200:
        print("Authentification succesful")
    elif response.status_code == 401:
        print("Unauthorized. The provided credentials were not recognized.")
    elif response.status_code == 422:
        print("Validation Error succesful")

    # Retrieve Acces Token        
    access_token = response.json()['access_token']
    # Create Authentification Header
    auth_header = {'Authorization': f'Bearer {access_token}'}
    
    return auth_header