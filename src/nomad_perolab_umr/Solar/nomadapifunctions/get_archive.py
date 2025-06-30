# Imports
import requests
import json

# Base URL NOMAD Oasis
OASIS_BASE_URL = 'https://vhrz1634.hrz.uni-marburg.de/nomad-oasis/api/v1'


# Load app token for the functions in this script
#from . import AUTH_HEADER
AUTH_HEADER=None


############################### GET ARCHIVE BY ENTRY ID ###############################

def get_archive_by_entry_id(entry_id, base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER, owner='admin', pagination=None,):
    """
        Retrieves archive data for a specified entry ID using the NOMAD Oasis API.

        Parameters:
        - entry_id (str): The unique identifier of the entry for which archive data is requested.
        - base_url (str, optional): The base URL of the NOMAD Oasis API. Defaults to the global OASIS_BASE_URL.
        - auth_header (dict, optional): The authentication header containing the App Token. Defaults to the global AUTH_HEADER.

        Returns:
        - If the API request is successful (status_code 200):
            A dictionary containing the archive data for the specified entry ID.
        - If the entry is not found (status_code 404):
            Prints an error message indicating that the entry with the given ID was not found.
        - If there is a validation error (status_code 422):
            Prints a message indicating that a validation error occurred.

        API Response JSON Structure:
        {
            "data": {
                "archive": {
                    "data": {
                        # ... Archive data for the specified entry ...
                    },
                    "m_ref_archives": ...,
                    "metadata": ...,
                    "processing_logs": ...,
                    "results": ...,
                    "workflow2": ...
                },
                "entry_id": ...,
                "required": ...
            }
        }

        Usage:
        archive_data = getArchive('your_entry_id_here')
        """

    # API Request
    endpoint = f'/entries/{entry_id}/archive'
    url = f'{base_url}{endpoint}'

    json=dict(
        owner=owner,
        pagination=pagination,
    )

    response = requests.get(url, headers=auth_header, json=json)

    # Print API Response Information
    print(response)
    if response.status_code == 200:
        print("Successful Response")
    elif response.status_code == 404:
        print("Entry not found. The given id does not match any entry.")
        return
    elif response.status_code == 422:
        print("Validation Error successful")
        return
    
    # Parse API Response JSON
    response_json = response.json()
    response_data = response_json['data']
    response_archive = response_data['archive']
    response_archive_data = response_archive['data']

    return response_archive_data





############################### GET ARCHIVE BY QUERY ###############################


def get_archive_by_query(query, owner='shared', pagination=None, required=None, base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER, return_value='archive_data'):
    """
        Retrieves archive data for a specified query (and optional specified owner, pagination and required keys) using the NOMAD Oasis API.

        Parameters:
        # TODO
        - base_url (str, optional): The base URL of the NOMAD Oasis API. Defaults to the global OASIS_BASE_URL.
        - auth_header (dict, optional): The authentication header containing the App Token. Defaults to the global AUTH_HEADER.

        Returns:
        - If the API request is successful (status_code 200):
            A dictionary containing the archive data for the specified entry ID.
        - If the entry is not found (status_code 404):
            Prints an error message indicating that the entry with the given ID was not found.
        - If there is a validation error (status_code 422):
            Prints a message indicating that a validation error occurred.

        API Response JSON Structure:
        {
            "data": {
                "archive": {
                    "data": {
                        # ... Archive data for the specified entry ...
                    },
                    "m_ref_archives": ...,
                    "metadata": ...,
                    "processing_logs": ...,
                    "results": ...,
                    "workflow2": ...
                },
                "entry_id": ...,
                "required": ...
            }
        }

        Usage:

    """

    # API Request
    endpoint = f'/entries/archive/query'
    url = f'{base_url}{endpoint}'

    json=dict(
        owner=owner,
        query=query,
        pagination=pagination,
        required=required,
    )

    # API call
    response = requests.post(url, headers=auth_header, json=json)

   # Print API Response Information
    print(response)
    if response.status_code == 200:
        print("Successful Response")
    elif response.status_code == 400:
        print("The given required specification could not be understood.")
        return
    elif response.status_code == 401:
        print("Unauthorized. The given owner requires authorization, but no or bad authentication credentials are given.")
        return
    elif response.status_code == 422:
        print("Validation Error")
        return
    
    # Parse API Response JSON
    response_json = response.json()
    response_data = response_json['data']

    response_archive = [res["archive"] for res in response_data]
    response_archive_data = [res["data"] for res in response_archive]

    # Print information about page size and total serach results
    total = response_json['pagination']['total']
    page_size = response_json['pagination']['page_size']
    if total > page_size:
        print(f"There were {total} entries found, but only {page_size} entries returend in this response. Either increase the page_size or use the next_page_after_value.")
        next_page_after_value = response_json['pagination']['next_page_after_value']
    else:
        print(f"{len(response_data)} entries were found and returned")

    # Print information about Ordering
    order_by = response_json['pagination']['order_by']
    order = response_json['pagination']['order']
    print(f"Results are ordered by '{order_by}' in '{order}' order.")


    # Return data based on given return_value
    if return_value == 'full_response':
        return response_json
    elif return_value == 'data':
        return response_data
    elif return_value == 'archive':
        return response_archive
    elif return_value == 'archive_data':
        return response_archive_data

    elif return_value == 'next_page_after_value':
        return next_page_after_value




############################### GET BATCH ARCHIVE BY LAB ID ###############################

def get_batch_by_id(lab_id, owner='shared', query=None, required=None, return_value='archive_data'):
    """
    Retrieves batch data from the archive based on the provided lab_id.

    Parameters:
    - lab_id (str): The lab_id of the batch to retrieve.
    - owner (str): The owner of the data (default is 'shared').
    - query (dict or None): Additional query parameters to refine the search 
                          (default is None). If None, a default query is constructed.
    - required (list or None): A list of required fields to be included in the response 
                             (default is None).
    - return_value (str): Specifies what type of data to return. Possible values:
                        - 'archive_data': Returns the raw archive data (default).
                        - 'parsed_data': Returns parsed and structured data.

    Returns:
    dict or list: The retrieved batch data. If return_value is 'archive_data' and 
                 only one result is found, returns a dictionary. Otherwise, returns 
                 a list of dictionaries.
    """

    if not query:
        # Standard Query
        query = {
            'entry_type:any': ['UMR_InternalBatch', 'UMR_ExternalBatch'],
            'or': [
                {'data.lab_id#UMR_schemas.batch.UMR_InternalBatch': lab_id},
                {'data.lab_id#UMR_schemas.batch.UMR_ExternalBatch': lab_id}
            ]
        }
        
    response = get_archive_by_query(query, owner=owner, required=required, return_value=return_value)

    if return_value == 'archive_data' and len(response) == 1:
        # If only 1 result return first element of list (because only 1 element)
        return response[0]
    else:
        # Else return full result list
        return response 



############################### GET EQE Measurements BY DEVICE LIST ###############################

def get_eqe_measurements_by_device_list(device_list, owner='shared', query=None, pagination=None, required=None, best_measurement=False, show_devices=True, return_value='archive_data'):
    """
    Retrieves EQE (External Quantum Efficiency) measurements for a list of devices from the archive.

    Parameters:
    - device_list (list): A list of device identifiers for which EQE measurements 
                        should be retrieved.
    - best_measurement (bool): If True, filters to retrieve only the best measurement 
                        or each device (default is False).

    ADVANCED PARAMETERS
    - owner (str): The owner of the data (default is 'shared').
    - query (dict or None): Additional query parameters to refine the search 
                          (default is None). If None, a default query is constructed.
    - pagination (dict or None): Parameters for pagination including 'page_size' 
                               and 'order_by' (default is None).
    - required (dict or None): A dictionary specifying the required fields in the 
                             response data (default is None).
    - return_value (str): Specifies what type of data to return. Possible values:
                        - 'archive_data': Returns the raw archive data (default).
                        - 'parsed_data': Returns parsed and structured data.

    Returns:
    dict or list: The retrieved EQE measurement data. If return_value is 'archive_data' 
                 and only one result is found, returns a dictionary. Otherwise, returns 
                 a list of dictionaries.
    """

    if not query:
        # Standard Query
        query = {
            'entry_type': 'UMR_EQEMeasurement',
            'data.device#UMR_schemas.characterization.eqe_measurement.UMR_EQEMeasurement:any': device_list,
            }
        # Append best_measurement search if flag is true
        if best_measurement:
            query['data.best_measurement#UMR_schemas.characterization.eqe_measurement.UMR_EQEMeasurement'] = True

    if not pagination:
        # Page Size should be equal to nuber of given devices (Orderd by lab id of device)    
        pagination = {
            'page_size': len(device_list),
            'order_by': "data.device#UMR_schemas.characterization.eqe_measurement.UMR_EQEMeasurement",
            }

    if not required:
        # Do not return figures and advanced_eqe_data
        required = {
            'data': {
                # general properties
                'name': '*',
                'datetime': '*',
                'method': '*',
                'data_file': '*',
                'user': '*',
                'solar_cell_was_referenced': '*',
                'measurement_data_was_extracted_from_data_file': '*',
                'device': '*',
                'active_area': '*',
                'temperature': '*',
                'directory': '*',
                'samples':'*',
                'instruments': '*',
                #'figures':'*',

                # eqe properties
                'minimum_wavelength': '*',
                'maximum_wavelength': '*',
                'wavelength_step': '*',
                'averaging': '*',
                'autorange': '*',
                'delay_time': '*',
                'bias_voltage': '*',
                'bias_light': '*',
                'spectral_mismatch':'*',
                'eqe_data':'*',
                #'advanced_eqe_data':'*',

                }
            }

    response = get_archive_by_query(query, owner=owner, pagination=pagination, required=required, return_value=return_value)
    
    # Print device names of found measurements
    if show_devices:
        print("For the following devices measurements were found:")
        for measurement in response:
            print(measurement['device'])

    return response


    
############################### GET JV Measurements BY DEVICE LIST ###############################

def get_jv_measurements_by_device_list(device_list, owner='shared', query=None, pagination=None, required=None, base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER, best_measurement=False, show_devices=True, return_value='archive_data'):
    """
    Retrieves JV (Current-Voltage) measurements for a list of devices from the archive.

    Parameters:
    - device_list (list): A list of device identifiers for which JV measurements 
                        should be retrieved.
    - best_measurement (bool): If True, filters to retrieve only the best measurement 
                        for each device (default is False).
    
    ADVANCED PARAMETERS
    - owner (str): The owner of the data (default is 'shared').
    - query (dict or None): Additional query parameters to refine the search 
                          (default is None). If None, a default query is constructed.
    - pagination (dict or None): Parameters for pagination including 'page_size' 
                               and 'order_by' (default is None).
    - required (dict or None): A dictionary specifying the required fields in the 
                             response data (default is None).
    - base_url (str): The base URL for the archive API (default is OASIS_BASE_URL).
    - auth_header (str): The authorization header for API authentication 
                       (default is AUTH_HEADER).
    - return_value (str): Specifies what type of data to return. Possible values:
                        - 'archive_data': Returns the raw archive data (default).
                        - 'parsed_data': Returns parsed and structured data.

    Returns:
    dict or list: The retrieved JV measurement data. If return_value is 'archive_data' 
                 and only one result is found, returns a dictionary. Otherwise, returns 
                 a list of dictionaries.
    """

    if not query:
        # Standard Query
        query = {
            'entry_type': 'UMR_JVMeasurement',
            'data.device#UMR_schemas.characterization.jv_measurement.UMR_JVMeasurement:any': device_list,
            }
        
        # Append best_measurement search if flag is true
        if best_measurement:
            query['data.best_measurement#UMR_schemas.characterization.jv_measurement.UMR_JVMeasurement'] = True

    ## PAGINATION
    default_pagination = {
        'page_size': len(device_list),
        'order_by': "data.device#UMR_schemas.characterization.jv_measurement.UMR_JVMeasurement",
    }
    # If no pagination object entered use default pagination
    if pagination is None:
        pagination = default_pagination
    else:
        # Combine default pagination with given customized pagination
        for key, value in default_pagination.items():
            pagination.setdefault(key, value)
   

    if not required:
        # Do not return figure data
        required = {
            'data': {
                # general properties
                'name': '*',
                'datetime': '*',
                'method': '*',
                'data_file': '*',
                'user': '*',
                'solar_cell_was_referenced': '*',
                'measurement_data_was_extracted_from_data_file': '*',
                'device': '*',
                'active_area': '*',
                'temperature': '*',
                'directory': '*',
                'samples': '*',
                'instruments': '*',
                'description': '*',
                #'figures':'*',

                # jv properties
                'minimum_voltage': '*',
                'maximum_voltage': '*',
                'voltage_step': '*',
                'auto_detect_voc': '*',
                'scan_rate': '*',
                'initial_delay': '*',
                'scan_order': '*',
                'jv_curve': '*',

                }
            }

    response = get_archive_by_query(query, owner=owner, pagination=pagination, required=required, return_value=return_value)
        # Print device names of found measurements
    if show_devices:
        print("For the following devices measurements were found:")
        for measurement in response:
            print(measurement['device'])

    return response













################## OLD FUNCTIONS - DO NOT USE ANYMORE

##### GET JV MEASUREMENT BY DEVICE ######
# This was a demo function for Lea

def get_jvmeasurement_by_device(device, base_url=OASIS_BASE_URL, auth_header=AUTH_HEADER):
    """
    Retrieves archive data for UMR_JVmeasurement entries associated with a specified device using the NOMAD Oasis API.

    Parameters:
    - device (str): The identifier of the device for which UMR_JVmeasurement archive data is requested.
    - base_url (str, optional): The base URL of the NOMAD Oasis API. Defaults to the global OASIS_BASE_URL.
    - auth_header (dict, optional): The authentication header containing the App Token. Defaults to the global AUTH_HEADER.

    Returns:
    - If the API request is successful (status_code 200):
        A list containing dictionaries of archive data for UMR_JVmeasurement entries associated with the specified device.

    API Response JSON Structure:
    {
        "data": [
            {
                "archive": {
                    "data": {
                        # ... Archive data for UMR_JVmeasurement entry ...
                    },
                    "m_ref_archives": ...,
                    "metadata": ...,
                    "processing_logs": ...,
                    "results": ...,
                    "workflow2": ...
                },
                "entry_id": ...,
                "required": ...
            },
            # ... Additional results if any ...
        ]
    }

    Usage:
    archive_data_list = get_JVmeasurement_archive('device')
    """

    # API Request
    endpoint = f'/entries/archive/query'
    url = f'{base_url}{endpoint}'

    json = {
        'owner': 'visible',
        'query': {
            'entry_type': 'UMR_JVmeasurement',
            'search_quantities': {
                'id': 'data.device#UMR_schemas.umr_characterization_classes.UMR_JVmeasurement',
                'str_value': device
                },
            }
    }

    response = requests.post(url, headers=auth_header, json=json)

    # Print API Response Information
    print(response)
    #print(response.text)
    if response.status_code == 200:
        print("Successful Response")
    elif response.status_code == 400:
        print("The given required specification could not be understood.")
    elif response.status_code == 401:
        print("Unauthorized. The given owner requires authorization, but no or bad authentication credentials are given.")
    elif response.status_code == 422:
        print("Validation Error")
    
    # Parse API Response JSON
    response_json = response.json()
    response_data = response_json['data']
    print(f"{len(response_data)} results found")
    
    # Iterate through result list and get archives
    response_archive_data = [result['archive']['data'] for result in response_data]

    # return list with JVmeasurement_archives
    return response_archive_data