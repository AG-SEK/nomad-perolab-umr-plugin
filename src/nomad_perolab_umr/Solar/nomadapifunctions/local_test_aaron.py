
###################################### TEST FUNCTIONS - DO NOT USE! ######################################

from getpass import getpass

import requests

# Authentication (Retrieving Accces Token)

local_base_url = 'http://localhost/nomad-oasis/api/v1'

def getAuthenticationHeader_AccessToken(base_url=local_base_url, username=None):
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



    # response = requests.post(url, data = query)  # Alternative method


def searchEntry(auth_header, query, base_url=local_base_url):
                
    endpoint = '/entries/archive/query'
    url = f'{base_url}{endpoint}'

    json = {
        'owner': 'visible',
        'query': {
            #'entry_type': 'UMR_StabilityTest',
            'search_quantities': {
                'id': 'data.directory#UMR_schemas.umr_characterization_classes.UMR_StabilityTest',
                'str_value': "16.17.13"
                },
            }}
    
    json=query

    response = requests.post(url, headers=auth_header, json=json)
    # response = requests.post(url, data = query)  # Alternative method
    print(response)
    print(response.json())

    response_json = response.json()
    
# Parse API Response JSON
    response_json = response.json()
    response_data = response_json['data']
    print(len(response_data))
    #response_archive = response_data['archive']
    #response_archive_data = response_archive['data']

    return response_data





# Get full archive data for a specified entry
def getJSON(entry_id, auth_header, base_url=local_base_url, ):
    

    # API Request
    endpoint = f'/entries/{entry_id}/archive'
    url = f'{base_url}{endpoint}'
    response = requests.get(url, headers=auth_header)

    # Print API Response Information
    print(response)
    if response.status_code == 200:
        print("Successful Response")
    elif response.status_code == 404:
        print("Entry not found. The given id does not match any entry.")
    elif response.status_code == 422:
        print("Validation Error successful")
    

    # Parse API Response JSON
    response_json = response.json()
    response_data = response_json['data']
    response_archive = response_data['archive']
    response_archive_data = response_archive['data']

    return response_json
