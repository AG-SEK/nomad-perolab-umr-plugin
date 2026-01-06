#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

### Imports ###

# Python libraries
import os
from datetime import datetime

import pytz

# HZB methods
from baseclasses.helper.utilities import (
    get_reference,
)

# Nomad Classes
# My classes and methods
from ..helper_functions import *
from ..suggestions_lists import *
from ..umr_reference_classes import UMR_EntityReference, UMR_InstrumentReference
from .read_header_line import read_header_line


def read_general_info(mainfile, encoding):
    """
    This function adds genral infos from the header 
    """       
    
    header_dict = {}

    # Open File and read it line by line
    with open(mainfile, encoding=encoding) as file:
        for raw_line in file:
            # Remove whitespaces from the line
            line = raw_line.strip() 
            # Check if header ended -> stop loop
            if line == '## Data ##':
                break
            # Skip empty lines and title lines ([General info],[Scan Seetings], ...) and ## Data ##
            if not line or line.startswith("[") or line.startswith("##"):
                continue
            # Fill header_dict with keys and values
            header_dict = read_header_line(line, header_dict)
    
    return header_dict


def parse_general_info(entry, mainfile, encoding):


    # Extract directory for helper quantity
    directory = os.path.dirname(mainfile).split("raw/", 1)[-1]
    entry.directory = directory.replace('/', '_') # Replace "/"" with "_", because otherwise API search fails
    
    # Read data
    header_dict = read_general_info(mainfile, encoding)

    # Add general info (device, datetime, user) to the entry using the corresponding keys
    # Device name (lab_id)
    entry.device = header_dict['Device']
    # User
    entry.user = header_dict['User']
    # Datetime
    datetime_str = header_dict['Date'] + " " + header_dict['Time']
    initial_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')     # Parse the date and time without timezone information
    berlin_tz = pytz.timezone('Europe/Berlin')                                  # Define the Berlin timezone
    localized_datetime = berlin_tz.localize(initial_datetime)                   # Localize the initial datetime to the Berlin timezone
    entry.datetime = localized_datetime                                         # Enter localized datetime in entry -> But Datetime is saved in UTC (+00:00) in NOMAD
                                                                                # Without these lines the timezone would be always UTC+0
    

    # Adds notes to description, if not already done (keeps previously entered notes)
    if 'Note' in header_dict:
        note = f"Notes from measurement file: {header_dict['Note']}"
        if entry.description:
            if note not in entry.description:
                entry.description = note + " " + entry.description    
        else:
            entry.description = note


def reference_sample(entry, logger, archive):

    # Search for sample named in the txt-file (device) and reference it in Subsection: samples
    query = {
        'entry_type:any': ['UMR_ExternalSolarCell', 'UMR_InternalSolarCell', 'UMR_BasicSample'],
        'results.eln.lab_ids': entry.device
    }
    search_result = UMR_search(archive, query)

    # Continue if only one sample with this sample_id was found otherwise log error
    if len(search_result.data) == 1:
        data = search_result.data[0]
        upload_id, entry_id = data["upload_id"], data["entry_id"]
        # Create Reference (in samples subsection)
        entry.samples = [UMR_EntityReference(
            #name = "Solar Cell",
            reference = get_reference(upload_id, entry_id))]
            #lab_id = entry.device)]
        entry.samples[0].normalize(archive, logger)
        # Log search information
        entry.solar_cell_was_referenced = True
        log_info(entry, logger, f'INFORMATION ABOUT REFERENCING SAMPLE | SEARCH SAMPLE RESULTS: UPLOAD_ID: {upload_id} | ENTRY_ID: {entry_id} | LAB_ID: {entry.device}')
        archive.metadata.comment = ""
    elif len(search_result.data) > 1:
        log_error(entry, logger, "INFO ABOUT REFERENCING SAMPLE | There is more then one entry with this lab_id.")
        log_info(entry, logger, f'SEARCH RESULT DATA:{search_result.data} | LENGTH: {len(search_result.data)} ')
        archive.metadata.comment = "More than 1 SC found!"
    elif len(search_result.data) == 0:
        log_error(entry, logger, "INFO ABOUT REFERENCING SAMPLE | There is no entry with this lab_id. Please check.")
        archive.metadata.comment = "No SC found!"
        #log_info(entry, logger, "INFO ABOUT REFERENCING SAMPLE | There is no entry with this lab_id. Start search for the name of the device in the additional other_device_names subsection")
        
    #    # IF SEARCH VIA LAB_ID WAS NOT SUCCESFUL, SEARCH VIA DEVICE_NAME IS STARTED
    #    search_result = search_entry_by_device_name(archive, entry.device)
    #    if len(search_result.data) == 1:
    #        data = search_result.data[0]
    #        upload_id, entry_id = data["upload_id"], data["entry_id"]
    #        # Create Reference (in samples subsection)
    #        entry.samples = [UMR_EntityReference(
    #            reference = get_reference(upload_id, entry_id))]
    #            #lab_id = get_lab_id(upload_id, entry_id))]
    #        # Log search information
    #        entry.solar_cell_was_referenced = True
    #        log_info(entry, logger, f'INFO ABOUT REFERENCING SAMPLE | SEARCH SAMPLE WITH DEVICE NAME RESULTS: UPLOAD_ID: {upload_id} | ENTRY_ID: {entry_id} | LAB_ID: {get_lab_id(upload_id, entry_id)}') 
    #        archive.metadata.comment = ""
    #    elif len(search_result.data) == 0:
    #        log_error(entry, logger, "INFO ABOUT REFERENCING SAMPLE | There is no entry with this lab_id or other_device_name.")
    #        log_info(entry, logger, f'SEARCH RESULT DATA:{search_result.data}')
    #        archive.metadata.comment = "No SC found!"
    #    elif len(search_result.data) > 1:
    #        log_error(entry, logger, "INFO ABOUT REFERENCING SAMPLE | There is more then one entry with this other_device_name.")
    #        log_info(entry, logger, f'SEARCH RESULT DATA:{search_result.data} | LENGTH: {len(search_result.data)} ')
    #        archive.metadata.comment = "More than 1 SC found !"


def add_data_file(entry, mainfile):
    """
    This function adds the name and datafile to the entry (used directly in Parser)
    """
        
    # Add name
    entry.name = os.path.splitext(os.path.basename(mainfile))[0]    # Set short name of entry (use filename)
    # Add data file to measurement (Quantity: data_file)
    path_to_file = mainfile.split('raw/')[-1]                       # path to file is everything after ".volumes/fs/staging/oU/{upload_id/raw/"
    entry.data_file = path_to_file



def add_standard_instrument(entry, archive, logger):
    # Get list with lab_ids from dictionary
    list_lab_ids = standard_instruments_dictionary[entry.m_def.name]

    query = {
        'entry_type': 'UMR_Instrument',
        'results.eln.lab_ids:any': list_lab_ids}
    search_result = UMR_search(archive, query)

    list_references = []
    # Extract data from search results
    if len(search_result.data) >= 1:
        for res in search_result.data:
            try:
                upload_id, entry_id = res['upload_id'], res['entry_id']
                # Create reference
                reference = get_reference(upload_id, entry_id)
                list_references.append(reference)
                log_info(entry, logger, f'INFORMATION ABOUT COLLECTED STANDARD INSTRUMENT: upload_id: {upload_id} | entry_id: {entry_id}')
            except Exception as e:
                log_error(entry, logger, f"Error during processing (Collecting standard instruments) --- EXEPTION:{e}")
    else: 
        log_warning(entry, logger, f'No Standard Instrument found: search result data: {search_result.data} | length: {len(search_result.data)}')

    # Add instruments to entry
    entry.instruments = []
    for ref in list_references:
        instrument_ref = UMR_InstrumentReference(reference=ref)
        entry.instruments.append(instrument_ref)
