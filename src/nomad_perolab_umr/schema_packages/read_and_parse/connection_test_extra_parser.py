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
import numpy as np  # Import numpy for numpy arrays
from nomad.units import ureg

from ..helper_functions import *
from .read_header_line import read_header_line

### HELPER FUNCTIONS TO READ LINES FOR SPECIFIC CASES ###

def read_ConnectionTestExtra_line(line, connectionTest_dict):
    """
    READS CONNECTION TEST DATA LINES AND APPENDS THE VALUES TO THE LISTS IN THE DICTIONARY
    
    Parameters:
        line (str): current line in file
        connectionTest_dict (dict): dictionary to be filled with data
    Returns:
        connectionTest_dict (dict): dictionary filled with data
    """
    
    parts=line.split()                                                          # Split line at tab character
    connectionTest_dict["Time (s)"].append(float(parts[0]))                 # Append values to list in dictionary
    connectionTest_dict["Temperature"].append(float(parts[1]))

    return connectionTest_dict



### MAIN FUNCTIONS TO READ JV DATA FROM TXT FILE ###

def read_connectionTestExtra_data(mainfile, encoding):
    """
    READS CONNECTION TEST DATA FROM THE TXT FILE AND ORGANIZES IT INTO A DICTIONARY

    Parameters:
        mainfile (str): Path to the file to be read.
        encoding (str): Encoding of the file.
    Returns:
        connectionTest_dict (dict): Dictionary containing the read data.
    """
    
    # Initialize the main dictionary to store data
    connectionTest_dict = {"Time (s)":[], "Temperature": []}
    
    # Initialize some helper variables
    section = None       # Current section (header or data)

    # Open File and read it line by line
    with open(mainfile, encoding=encoding) as file:
  
        for raw_line in file:
            line = raw_line.strip()         # Remove whitespaces from the line
            
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
                connectionTest_dict=read_header_line(line, connectionTest_dict)
                
            # Process data section lines
            if section == 'data': 
                # Identify start of measurement data
                if not line.startswith('Time'):    
                    # Process MPPT data section
                    connectionTest_dict=read_ConnectionTestExtra_line(line, connectionTest_dict)
                

    # Convert lists to numpy arrays for numerical processing
    for measurement in ["Time (s)", "Temperature"]:
        if measurement in connectionTest_dict:
            connectionTest_dict[measurement] = np.array(connectionTest_dict[measurement])

    return connectionTest_dict
    

### ACTUAL PARSING FUNCTION; WHICH WRITES THE DATA INTO AN ARCHIVE ###
def parse_connectionTestExtra_data_to_archive(entry, mainfile, encoding):
    """
    Reads Connection Test data from a data file and parses it into the NOMAD entry.

    Parameters:
        entry (NOMADEntry): The NOMAD entry object to be filled with data.
        mainfile (str): The path to the main data file.
        encoding (str): The encoding of the data file.
    Note:
        It reads the data from the file, extracts relevant information, and populates the corresponding fields of the NOMAD entry object.

    """
    # Read data from measurement file into dictionary
    connectionTest_dict = read_connectionTestExtra_data(mainfile, encoding)

    entry.time = connectionTest_dict['Time (s)'] * ureg('s')
    entry.temperature = connectionTest_dict['Temperature'] * ureg('°C')

    # Check box "measurement data was extracted from data file"   
    entry.measurement_data_was_extracted_from_data_file = True



        
        

   




