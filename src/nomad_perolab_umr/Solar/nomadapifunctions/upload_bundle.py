import os

import requests

from . import AUTH_HEADER

OASIS_BASE_URL_NEW = 'https://solar-oasis.physik.uni-marburg.de/nomad-oasis/api/v1'
OASIS_BASE_URL_OLD = 'https://vhrz1634.hrz.uni-marburg.de/nomad-oasis/api/v1'


def get_upload_bundle(
        upload_id,
        base_url=OASIS_BASE_URL_OLD, 
        auth_header=AUTH_HEADER,
        return_value='file',
        include_raw_files=True,
        include_archive_files=True,
        include_datasets=True ):
    
    """
    Retrieve an upload bundle from the OASIS API and either return the response or save it as a ZIP file.

    Parameters:
        upload_id (str): The ID of the upload bundle to retrieve.
        base_url (str): The base URL of the OASIS API. Defaults to OASIS_BASE_URL_OLD.
        auth_header (dict): Authorization headers required by the API. Defaults to AUTH_HEADER.
        return_value (str): Determines the return type. 
                            Use 'file' to save the response as a ZIP file, 
                            or 'response' to return the raw `requests.Response` object.
        include_raw_files (bool): Whether to include raw files in the bundle. Defaults to True.
        include_archive_files (bool): Whether to include archived files in the bundle. Defaults to True.
        include_datasets (bool): Whether to include datasets in the bundle. Defaults to True.

    Returns:
        str: The filename of the saved ZIP file if `return_value='file'`.
        requests.Response: The raw response object if `return_value='response'`.
        None: If an error occurs or an invalid return_value is given.
    """

    endpoint = f'/uploads/{upload_id}/bundle'
    url = f'{base_url}{endpoint}'

    query = {
        "include_raw_files": include_raw_files,
        "include_archive_files": include_archive_files,
        "include_datasets": include_datasets,
    }

    try:
        response = requests.get(url, headers=auth_header, json=query)
    except requests.RequestException as e:
        print(f"[ERROR] Request to fetch upload bundle failed: {e}")
        return None
 
   # Print API response status
    print(f"[INFO] Response Status Code: {response.status_code}")

    if not response.ok:
        print(f"[ERROR] API responded with status code {response.status_code}: {response.text}")
        return None

    if return_value == 'response':
        return response
    elif return_value == 'file':
        filename = f'upload_bundle_{upload_id}.zip'
        try:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"[INFO] Upload bundle saved as ZIP file: '{filename}'")
            return filename
        except OSError as e:
            print(f"[ERROR] Failed to write file '{filename}': {e}")
            return None
    else:
        print(f"[ERROR] Invalid return_value: '{return_value}'. Must be 'file' or 'response'.")
        return None




def post_upload_bundle(zip_path,
                       base_url=OASIS_BASE_URL_NEW,
                       auth_header=AUTH_HEADER,
                       embargo_length=None,
                       include_raw_files=True,
                       include_archive_files=True,
                       include_datasets=True,
                       include_bundle_info=True,
                       keep_original_timestamps=True,
                       set_from_oasis=True,
                       trigger_processing=True):
    
    """
    Upload a ZIP bundle to the OASIS API and initiate processing.

    Parameters:
        zip_path (str): Path to the ZIP file to upload.
        base_url (str): Base URL for the OASIS API. Defaults to OASIS_BASE_URL_NEW.
        auth_header (dict): Authorization header to use with the request.
        embargo_length (int or None): Optional embargo duration in days.
        include_raw_files (bool): Whether to include raw files in the bundle. Defaults to True.
        include_archive_files (bool): Whether to include archive files. Defaults to True.
        include_datasets (bool): Whether to include datasets. Defaults to True.
        include_bundle_info (bool): Whether to include bundle metadata. Defaults to True.
        keep_original_timestamps (bool): Whether to preserve original timestamps. Defaults to True.
        set_from_oasis (bool): Whether to use OASIS-specific settings. Defaults to True.
        trigger_processing (bool): Whether to start processing after upload. Defaults to True.

    Returns:
        dict: Parsed JSON response from the API if successful.
        None: If an error occurs during the request or file operation.
    """
    
    endpoint = '/uploads/bundle'
    url = f'{base_url}{endpoint}'
 
    # Query-Parameter
    query = {
        "embargo_length": embargo_length,
        "include_raw_files": include_raw_files,
        "include_archive_files": include_archive_files,
        "include_datasets": include_datasets,
        "include_bundle_info": include_bundle_info,
        "keep_original_timestamps": keep_original_timestamps,
        "set_from_oasis": set_from_oasis,
        "trigger_processing": trigger_processing,
    }


    try:
        with open(zip_path, 'rb') as f:
            files = {
                'file': (zip_path, f, 'application/zip')
            }
            response = requests.post(url, headers=auth_header, json=query, files=files)
    except FileNotFoundError:
        print(f"[ERROR] ZIP file not found at path: '{zip_path}'")
        return None
    except requests.RequestException as e:
        print(f"[ERROR] Failed to send POST request: {e}")
        return None

    print(f"[INFO] Response Status Code: {response.status_code}")

    if not response.ok:
        print(f"[ERROR] API responded with status code {response.status_code}: {response.text}")
        return None

    print("[INFO] The upload bundle was succesfully posted to the OASIS")
    return response



def transfer_upload_to_oasis(
                        upload_id,
                        base_url_old=OASIS_BASE_URL_OLD,
                        base_url_new=OASIS_BASE_URL_NEW,
                        auth_header=AUTH_HEADER,
                        include_raw_files=True,
                        include_archive_files=True,
                        include_datasets=True,
                        embargo_length=None,
                        include_bundle_info=True,
                        keep_original_timestamps=True,
                        set_from_oasis=True,
                        trigger_processing=True):
    """
    Transfers an upload bundle from the old OASIS system to the new one.

    This function downloads a ZIP bundle for the given upload ID from the old OASIS API
    and then re-uploads it to the new API, optionally triggering processing and setting upload options.

    Parameters:
        upload_id (str): The ID of the upload to transfer.
        base_url_old (str): Base URL of the source (old) OASIS API.
        base_url_new (str): Base URL of the destination (new) OASIS API.
        auth_header (dict): Authorization header for API calls.
        include_raw_files (bool): Include raw files in the transfer. Defaults to True.
        include_archive_files (bool): Include archive files in the transfer. Defaults to True.
        include_datasets (bool): Include datasets in the transfer. Defaults to True.
        embargo_length (int or None): Optional embargo period in days. Defaults to None.
        include_bundle_info (bool): Include metadata info in the bundle. Defaults to True.
        keep_original_timestamps (bool): Preserve original file timestamps. Defaults to True.
        set_from_oasis (bool): Apply OASIS-specific settings. Defaults to True.
        trigger_processing (bool): Trigger processing after upload. Defaults to True.

    Returns:
        dict or None: Parsed response from the upload to the new API if successful, otherwise None.
    """
    
    # Step 1: Download bundle
    print(f"[INFO] Downloading bundle for upload ID: {upload_id}")
    zip_path = get_upload_bundle(
        upload_id,
        base_url=base_url_old,
        auth_header=auth_header,
        include_raw_files=include_raw_files,
        include_archive_files=include_archive_files,
        include_datasets=include_datasets
    )

    if not zip_path or not os.path.exists(zip_path):
        print(f"[ERROR] Failed to download upload bundle for ID: {upload_id}")
        return None

    # Step 2: Upload bundle
    print("[INFO] Uploading bundle to new OASIS instance...")
    response = post_upload_bundle(
        zip_path,
        base_url=base_url_new,
        auth_header=auth_header,
        embargo_length=embargo_length,
        include_raw_files=include_raw_files,
        include_archive_files=include_archive_files,
        include_datasets=include_datasets,
        include_bundle_info=include_bundle_info,
        keep_original_timestamps=keep_original_timestamps,
        set_from_oasis=set_from_oasis,
        trigger_processing=trigger_processing
    )

    # Step 3: Delete local ZIP file
    try:
        os.remove(zip_path)
        print(f"[INFO] Temporary file deleted: {zip_path}")
    except Exception as e:
        print(f"[WARNING] Could not delete file '{zip_path}': {e}")

    return response