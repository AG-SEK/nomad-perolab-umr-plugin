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


### IMPORTS ###
import numpy as np     # Import numpy for numpy arrays

from nomad.units import ureg

from .read_header_line import read_header_line
from ..helper_functions import *
from ..characterization.mpp_tracking import UMR_MPPTrackingData

### HELPER FUNCTIONS TO READ LINES FOR SPECIFIC CASES ###

def read_MPPTracking_line(line, mppt_dict):
    """
    READS MPPTRACKING DATA LINES AND APPENDS THE VALUES TO THE LISTS IN THE DICTIONARY
    
    Parameters:
        line (str): current line in file
        mppt_dict (dict): dictionary to be filled with data
    Returns:
        mppt_dict (dict): dictionary filled with data
    """
    
    parts=line.split()                                       # Split line at tab character
    mppt_dict["Time (Hours)"].append(float(parts[0]))        # Append values to list in dictionary
    mppt_dict["Voltage (V)"].append(float(parts[1]))
    mppt_dict["Current Density (mA/cm2)"].append(float(parts[2]))
    mppt_dict["Power (mW/cm2)"].append(float(parts[3]))

    return mppt_dict



### MAIN FUNCTIONS TO READ JV DATA FROM TXT FILE ###

def read_mppt_data(mainfile, encoding):
    """
    READS MPPTracking DATA FROM THE TXT FILE AND ORGANIZES IT INTO A DICTIONARY

    Parameters:
        mainfile (str): Path to the file to be read.
        encoding (str): Encoding of the file.
    Returns:
        mppt_dict (dict): Dictionary containing the read data.
    """
    
    # Initialize the main dictionary to store data
    mppt_dict = {"Time (Hours)":[], "Voltage (V)": [], "Current Density (mA/cm2)": [], "Power (mW/cm2)": []}
    
    # Initialize some helper variables
    section = None       # Current section (header or data)

    # Open File and read it line by line
    with open(mainfile, 'r', encoding=encoding) as file:
  
        for line in file:
            line = line.strip()         # Remove whitespaces from the line
            
            # Skip empty lines and title lines ([General info],[Scan Seetings], ...)
            if not line or line.startswith("["):
                continue
            
            # Identify the current section
            if line == '## Header ##':
                section = 'header'
                continue
            elif line == '## Data ##':
                section = 'data'
                continue
        
            # Process header section lines
            if section == 'header':
                mppt_dict=read_header_line(line, mppt_dict)
                
            # Process data section lines
            if section == 'data': 
                # Identify start of measurement data
                if not line.startswith('Time'):    
                    # Process MPPT data section
                    mppt_dict=read_MPPTracking_line(line, mppt_dict)
                

    # Convert lists to numpy arrays for numerical processing
    for measurement in ["Time (Hours)", "Voltage (V)", "Current Density (mA/cm2)", "Power (mW/cm2)"]:
        if measurement in mppt_dict:
            mppt_dict[measurement] = np.array(mppt_dict[measurement])

    return mppt_dict
    

### ACTUAL PARSING FUNCTION; WHICH WRITES THE DATA INTO AN ARCHIVE ###
def parse_mppt_data_to_archive(entry, mainfile, encoding):
    """
    Reads JV data from a data file and parses it into the NOMAD entry.

    Parameters:
        entry (NOMADEntry): The NOMAD entry object to be filled with data.
        mainfile (str): The path to the main data file.
        encoding (str): The encoding of the data file.
    Note:
        It reads the data from the file, extracts relevant information, and populates the corresponding fields of the NOMAD entry object.

    """
    # Read data from measurement file into dictionary
    mppt_dict = read_mppt_data(mainfile, encoding)

    # Fill specific data fields for MPPTracking Measurement
    entry.active_area = float(mppt_dict['Cell area (cm2)']) * ureg('cm^2')  if 'Cell area (cm2)' in mppt_dict else None
    entry.mpp_duration = float(mppt_dict['MPP duration (min)']) * ureg('minute') if 'MPP duration (min)' in mppt_dict else None

   # Create UMR_MPPTrackingData object and append it to mppt_data Subsection
    mppt_data = UMR_MPPTrackingData(
        time = mppt_dict['Time (Hours)'] * ureg('hours'),
        voltage = mppt_dict['Voltage (V)'] * ureg('V'),
        current_density = mppt_dict['Current Density (mA/cm2)'] * ureg('mA/cm^2'),
        power_density = mppt_dict['Power (mW/cm2)'] * ureg('mW/cm^2'),
        )
    entry.tracking_data = mppt_data

    # Check box "measurement data was extracted from data file"   
    entry.measurement_data_was_extracted_from_data_file = True

   

        
        

   




