# In this Script we colelct functions related to the user group management via API of the NOMAD Oasis

import requests

# NOMAD Base URL
OASIS_BASE_URL = 'https://solar-oasis.physik.uni-marburg.de/nomad-oasis/api/v1'

# Import authentication header
from . import AUTH_HEADER


def list_user_groups(base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER, return_value='data'):
    """
    Retrieve and display user groups from the NOMAD API.

    This function queries the `/groups` endpoint and prints available group information.
    The default return type is a list of group dictionaries, which includes:
      - group_id (str): Unique identifier of the group
      - group_name (str): Human-readable group name
      - owner (str): Owner's identifier
      - members (list): List of member identifiers

    Args:
        base_url (str): Base URL of the API (e.g., "https://solar-oasis.physik.uni-marburg.de/nomad-oasis/api/v1").
        auth_header (dict): Authorization header used for the request (e.g., {"Authorization": "Bearer {Token}"}).
        return_value (str): Determines the return type:
            - 'data': (default) returns only the group data – recommended for general use
            - 'json': returns the full parsed JSON response – for debugging
            - 'response': returns the raw requests.Response object – for advanced troubleshooting

    Returns:
        list | dict | requests.Response | None: Based on `return_value`:
            - list: when 'data' is selected (list of group dicts)
            - dict: full JSON response when 'json' is selected
            - requests.Response: raw response object when 'response' is selected
            - None: in case of errors or invalid return_value
    """
     
    endpoint = f'/groups'
    url = f'{base_url}{endpoint}'

    try:
        response = requests.get(url, headers=auth_header)
        response_json = response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError:
        print("Response content is not valid JSON.")
        return None
    
    # Print API Response Status
    print(f"Response Status Code: {response.status_code}")
    if not response.ok:
        print("Request was not successful.")
        print(f"Error response: {response_json}")
    elif not response_json.get('data'):
        print("No groups exist.")
    else:
        print("The following groups exist:")
        for group in response_json['data']:
            print(group)


    # Return appropriate value based on user input
    if return_value == "data":
        return response_json.get('data')
    elif return_value == "json":
        return response_json
    elif return_value == "response":
        return response
    else:
        print(f"Invalid return_value: '{return_value}'. Must be one of: 'data', 'json', 'response'.")
        return None
    


def create_user_group(group_name, list_user_ids, base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER, return_value='group'):
    """
    Create a new user group via the API.

    Sends a POST request to the `/groups` endpoint with the group name and list of member user IDs.
    Automatically converts a single user ID to a list if necessary.

    Args:
        group_name (str): The name of the group to be created.
        list_user_ids (list | str): A list of user IDs to be added to the group. A single string is converted to a list.
        base_url (str): Base URL of the API.
        auth_header (dict): Authorization header for the request.
        return_value (str): Determines the return type:
            - 'group': (default) returns the created group object – recommended for general use
            - 'response': returns the raw requests.Response object – for debugging/troubleshooting

    Returns:
        dict | requests.Response | None:
            - dict: created group details when 'group' is selected
            - requests.Response: full response object when 'response' is selected
            - None: in case of request failure or invalid return_value

    Example successful return (when return_value='group'):
    {
        'group_id': '...',
        'group_name': '...',
        'owner': '...',
        'members': ['...']
    }
    """

   # Ensure members are in a list format
    if not isinstance(list_user_ids, list):
        list_user_ids = [list_user_ids]

    group_data = {
        "group_name": group_name,
        "members": list_user_ids
    }

    endpoint = f'/groups'
    url = f'{base_url}{endpoint}'

    
    try:
        response = requests.post(url, headers=auth_header, json=group_data)
        response_json = response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError:
        print("Response content is not valid JSON.")
        return None
    

   # Print API response status
    print(f"Response Status Code: {response.status_code}")

    if not response.ok:
        print("Request was not successful.")
        print(f"Error response: {response_json}")
    else:
        print("Success! Group was created:")
        print(response_json)

    # Return appropriate value
    if return_value == "group":
        return response_json
    elif return_value == "response":
        return response
    else:
        print(f"Invalid return_value: '{return_value}'. Must be 'group' or 'response'.")
        return None



def get_information_about_user_group(group_id, base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER, return_value='group'):
    """
    Retrieve detailed information about a specific user group by its ID.

    Sends a GET request to the `/groups/{group_id}` endpoint and prints details about the group.

    Args:
        group_id (str): Unique identifier of the group to be queried.
        base_url (str): Base URL of the API.
        auth_header (dict): Authorization header for the request.
        return_value (str): Determines the return type:
            - 'group': (default) returns the group object – recommended for general use
            - 'response': returns the raw requests.Response object – for debugging/troubleshooting

    Returns:
        dict | requests.Response | None:
            - dict: group information when 'group' is selected
            - requests.Response: full response object when 'response' is selected
            - None: in case of request failure or invalid return_value

    Example return (when return_value='group'):
    {
        'group_id': '...',
        'group_name': '...m',
        'owner': '...',
        'members': ['...', '...']
    }
    """
    
    endpoint = f'/groups/{group_id}'
    url = f'{base_url}{endpoint}'

    try:
        response = requests.get(url, headers=auth_header)
        response_json = response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError:
        print("Response content is not valid JSON.")
        return None

   # Print API response status
    print(f"Response Status Code: {response.status_code}")

    if not response.ok:
        print("Request was not successful.")
        print(f"Error response: {response_json}")
    else:
        print("Information about Group:")
        print(response_json)

    # Return appropriate value
    if return_value == "group":
        return response_json
    elif return_value == "response":
        return response
    else:
        print(f"Invalid return_value: '{return_value}'. Must be 'group' or 'response'.")
        return None



def delete_user_group(group_id, base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER, confirm=True):
    """
    Delete a user group by its ID.

    This function sends a DELETE request to the `/groups/{group_id}` endpoint.
    It optionally prompts the user for confirmation before proceeding with deletion.

    Args:
        group_id (str): Unique identifier of the group to delete.
        base_url (str): Base URL of the API.
        auth_header (dict): Authorization header for the request.
        confirm (bool): If True (default), prompts the user for confirmation before deleting.

    Returns:
        requests.Response | None:
            - requests.Response: The HTTP response object from the DELETE request.
            - None: If the deletion was cancelled or failed before reaching the request.
    """

    # Retrieve group information for confirmation
    group = get_information_about_user_group(group_id)
    if not group:
        print("Failed to fetch group information. Aborting deletion.")
        return None
    
    group_name = group.get('group_name', 'Unknown')

    # Ask user for confirmation unless overridden
    if confirm:
        confirmation = input(f'Are you sure you want to delete the group with name "{group_name}" and ID {group_id}? Enter (yes/no): ').strip().lower()
        if confirmation != 'yes':
            print("Group deletion cancelled.")
            return None

    # Send DELETE request
    endpoint = f'/groups/{group_id}'
    url = f'{base_url}{endpoint}'
    
    try:
        response = requests.delete(url, headers=auth_header)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    # Print API response info
    print(f"Response Status Code: {response.status_code}")
    if response.status_code == 204:
        print("Group was deleted successfully.")
    else:
        print("Request not successful. Possible validation or permission error.")
        try:
            print("Response body:", response.json())
        except ValueError:
            print("No JSON in response.")

    return response


def add_user_to_user_group(group_id, user_id, base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER, return_value="group"):
    """
    Add a user to an existing user group.

    This function retrieves the current members of a group, appends the given user ID,
    and sends an update via the `/groups/{group_id}/edit` endpoint.

    Args:
        group_id (str): Unique identifier of the group to update.
        user_id (str): User ID to be added to the group.
        base_url (str): Base URL of the API.
        auth_header (dict): Authorization header for the request.
        return_value (str): Determines the return type:
            - 'group': (default) returns the updated group object – recommended for general use
            - 'response': returns the raw requests.Response object – for debugging/troubleshooting

    Returns:
        dict | requests.Response | None:
            - dict: updated group info if 'group' is selected
            - requests.Response: response object if 'response' is selected
            - None: on failure

    Notes:
        - Will not add a user if they are already a member (no duplication).
        - Assumes the group already exists and is accessible.
    """
    # Fetch current group information
    response = get_information_about_user_group(group_id, base_url=base_url, auth_header=auth_header, return_value="response")
    if not response or not response.ok:
        print("Error retrieving group members. Please check if group_id is correct and accessible.")
        return None

    try:
        group = response.json()
    except ValueError:
        print("Invalid JSON in group response.")
        return None

    members_list = group.get("members", [])
    if user_id in members_list:
        print(f"User '{user_id}' is already a member of the group.")
    else:
        members_list.append(user_id)

    # Prepare updated group data
    group_data = {
        "members": members_list
    }

    endpoint = f'/groups/{group_id}/edit'
    url = f'{base_url}{endpoint}'

    try:
        response = requests.post(url, headers=auth_header, json=group_data)
        response_json = response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError:
        print("Response content is not valid JSON.")
        return None

    # Print API response status
    print(f"Response Status Code: {response.status_code}")
    if not response.ok:
        print("Failed to add user to the group.")
        print(response_json)
    else:
        print(f'Success! User "{user_id}" was added to group.')
        print(response_json)

    # Return appropriate value
    if return_value == "group":
        return response_json
    elif return_value == "response":
        return response
    else:
        print(f"Invalid return_value: '{return_value}'. Must be 'group' or 'response'.")
        return None



def remove_user_from_user_group(group_id, user_id, base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER, return_value="group"):
    """
    Remove a user from an existing user group.

    This function retrieves the current members of a group, removes the given user ID (if present),
    and sends an update via the `/groups/{group_id}/edit` endpoint.

    Args:
        group_id (str): Unique identifier of the group to update.
        user_id (str): User ID to be removed from the group.
        base_url (str): Base URL of the API.
        auth_header (dict): Authorization header for the request.
        return_value (str): Determines the return type:
            - 'group': (default) returns the updated group object – recommended for general use
            - 'response': returns the raw requests.Response object – for debugging/troubleshooting

    Returns:
        dict | requests.Response | None:
            - dict: updated group info if 'group' is selected
            - requests.Response: response object if 'response' is selected
            - None: on failure

    Notes:
        - If the user is not in the group, the operation will be skipped with a warning.
    """
    # Fetch current group information
    response = get_information_about_user_group(group_id, base_url=base_url, auth_header=auth_header, return_value="response")
    if not response or not response.ok:
        print("Error retrieving group members. Please check if group_id is correct and accessible.")
        return None

    try:
        group = response.json()
    except ValueError:
        print("Invalid JSON in group response.")
        return None

    members_list = group.get("members", [])

    if user_id not in members_list:
        print(f"User '{user_id}' is not a member of the group. No action taken.")
        return None

    members_list.remove(user_id)

    # Prepare updated group data
    group_data = {
        "members": members_list
    }

    endpoint = f'/groups/{group_id}/edit'
    url = f'{base_url}{endpoint}'

    try:
        response = requests.post(url, headers=auth_header, json=group_data)
        response_json = response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError:
        print("Response content is not valid JSON.")
        return None

    # Print API response status
    print(f"Response Status Code: {response.status_code}")
    if not response.ok:
        print("Failed to remove user from the group.")
        print(response_json)
    else:
        print(f'Success! User "{user_id}" was removed from the group.')
        print(response_json)

    # Return appropriate value
    if return_value == "group":
        return response_json
    elif return_value == "response":
        return response
    else:
        print(f"Invalid return_value: '{return_value}'. Must be 'group' or 'response'.")
        return None
    

    
def change_group_name(group_id, new_group_name, base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER, return_value="group"):
    """
    Change the name of an existing user group.

    This function updates the name of a group using the `/groups/{group_id}/edit` endpoint.

    Args:
        group_id (str): Unique identifier of the group to update.
        new_group_name (str): The new name to assign to the group.
        base_url (str): Base URL of the API.
        auth_header (dict): Authorization header for the request.
        return_value (str): Determines the return type:
            - 'group': (default) returns the updated group object – recommended for general use
            - 'response': returns the raw requests.Response object – for debugging/troubleshooting

    Returns:
        dict | requests.Response | None:
            - dict: Updated group info if 'group' is selected.
            - requests.Response: Response object if 'response' is selected.
            - None: On failure or if an invalid `return_value` is provided.

    Notes:
        - Assumes the group exists and the user has permission to update it.
        - Will not perform any action other than changing the group name.
    """
    
    # Prepare updated group data
    group_data = {
        "group_name": new_group_name
    }

    endpoint = f'/groups/{group_id}/edit'
    url = f'{base_url}{endpoint}'

    try:
        response = requests.post(url, headers=auth_header, json=group_data)
        response_json = response.json()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError:
        print("Response content is not valid JSON.")
        return None

    # Print API response status
    print(f"Response Status Code: {response.status_code}")
    if not response.ok:
        print("Failed to cahnge group name.")
        print(response_json)
    else:
        print(f'Success! Group name was changed to "{new_group_name}"')
        print(response_json)

    # Return appropriate value
    if return_value == "group":
        return response_json
    elif return_value == "response":
        return response
    else:
        print(f"Invalid return_value: '{return_value}'. Must be 'group' or 'response'.")
        return None
