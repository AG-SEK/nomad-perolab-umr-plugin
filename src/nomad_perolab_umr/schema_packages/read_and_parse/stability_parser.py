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
from datetime import datetime

import numpy as np  # Import numpy for numpy arrays
from nomad.units import ureg

from ..characterization.stability_test import UMR_StabilityTracking
from ..helper_functions import *
from .mppt_parser import read_MPPTracking_line
from .read_header_line import read_header_line

### MAIN FUNCTIONS TO READ JV DATA FROM TXT FILE ###

def read_stabilityTracking_data(mainfile, encoding):
    """
    READS STABILITY TRACKING DATA FROM THE TXT FILE AND ORGANIZES IT INTO A DICTIONARY

    Parameters:
        mainfile (str): Path to the file to be read.
        encoding (str): Encoding of the file.
    Returns:
        stabilityTracking_dict (dict): Dictionary containing the read data.
    """
    
    # Initialize the main dictionary to store data
    stabilityTracking_dict = {"Time (Hours)":[], "Voltage (V)": [], "Current Density (mA/cm2)": [], "Power (mW/cm2)": []}
    
    # Initialize some helper variables
    section = None       # Current section (header or data)

    # Open File and read it line by line
    with open(mainfile, encoding=encoding) as file:
  
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
                stabilityTracking_dict=read_header_line(line, stabilityTracking_dict)
                
            # Process data section lines
            if section == 'data': 
                # Identify start of measurement data
                if not line.startswith('Time'):    
                    # Process data section
                    stabilityTracking_dict=read_MPPTracking_line(line, stabilityTracking_dict)
                

    # Convert lists to numpy arrays for numerical processing
    for measurement in ["Time (Hours)", "Voltage (V)", "Current Density (mA/cm2)", "Power (mW/cm2)"]:
        if measurement in stabilityTracking_dict:
            stabilityTracking_dict[measurement] = np.array(stabilityTracking_dict[measurement])

    return stabilityTracking_dict
    

### ACTUAL PARSING FUNCTION; WHICH WRITES THE DATA INTO AN ARCHIVE ###
def parse_stabilityTracking_data_to_archive(entry, mainfile, encoding):
    """
    Reads Stability Tracking data from a data file and parses it into the NOMAD entry.

    Parameters:
        entry (NOMADEntry): The NOMAD entry object to be filled with data.
        mainfile (str): The path to the main data file.
        encoding (str): The encoding of the data file.
    Note:
        It reads the data from the file, extracts relevant information, and populates the corresponding fields of the NOMAD entry object.
    """
    # Read data from measurement file into dictionary
    stabilityTracking_dict = read_stabilityTracking_data(mainfile, encoding)

    # Fill specific data fields for MPPTracking Measurement
    entry.active_area = float(stabilityTracking_dict['Cell Area (cm2)'])

    entry.algorithm = stabilityTracking_dict['Algorithm']
    entry.voltage_step_track = float(stabilityTracking_dict['dV track (V)'])
    entry.track_delay = float(stabilityTracking_dict['track delay (s)'])
    entry.jv_interval = float(stabilityTracking_dict['JV interval (hours)'])
    entry.test_duration = float(stabilityTracking_dict['Test duration (hours)'])
    entry.start_up_time = datetime.strptime(stabilityTracking_dict['Start-up Time'], "%H:%M:%S %d/%m/%Y")

    data = UMR_StabilityTracking(
        time = stabilityTracking_dict['Time (Hours)'] * ureg('hours'),
        voltage = stabilityTracking_dict['Voltage (V)'] * ureg('V'),
        current_density = stabilityTracking_dict['Current Density (mA/cm2)'] * ureg('mA/cm^2'),
        power_density = stabilityTracking_dict['Power (mW/cm2)'] * ureg('mW/cm^2'),
    )

    entry.tracking_data = data

    # Check box "measurement data was extracted from data file"   
    entry.measurement_data_was_extracted_from_data_file = True



