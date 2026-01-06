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

def read_parameters_line(line, parameters_dict):  
    """
    READS PARAMETER LINES (Voc, Jsc, ...) AND ADDS THEM TO NESTED DICTIONARIES (Forward and Reverse)
    
    Parameters:
        line (str): current line in file
        parameters_dict (dict): dictionary to be filled with data
        measurement (str): Forward or Reverse
    Returns:
        parameters_dict (dict): dictionary filled with data 
    """         
    
    parts=line.split()                         # Split line at tab character   
    
    # Append values to list in nested dictionaries (Forward and Reverse)
    parameters_dict["Forward"]["Time (Hours)"].append(float(parts[0]))
    parameters_dict["Forward"]["Voc (V)"].append(float(parts[1]))
    parameters_dict["Forward"]["Jsc (mA/cm2)"].append(float(parts[2]))
    parameters_dict["Forward"]["V_MPP (V)"].append(float(parts[3]))
    parameters_dict["Forward"]["J_MPP (mA/cm2)"].append(float(parts[4]))
    parameters_dict["Forward"]["P_MPP (mW/cm2)"].append(float(parts[5]))
    parameters_dict["Forward"]["R_series (Ohm)"].append(float(parts[6]))
    parameters_dict["Forward"]["R_shunt (Ohm)"].append(float(parts[7]))
    parameters_dict["Forward"]["FF (%)"].append(float(parts[8]))
    parameters_dict["Forward"]["Eff. (%)"].append(float(parts[9]))

    parameters_dict["Reverse"]["Time (Hours)"].append(float(parts[0]))
    parameters_dict["Reverse"]["Voc (V)"].append(float(parts[10]))
    parameters_dict["Reverse"]["Jsc (mA/cm2)"].append(float(parts[11]))
    parameters_dict["Reverse"]["V_MPP (V)"].append(float(parts[12]))
    parameters_dict["Reverse"]["J_MPP (mA/cm2)"].append(float(parts[13]))
    parameters_dict["Reverse"]["P_MPP (mW/cm2)"].append(float(parts[14]))
    parameters_dict["Reverse"]["R_series (Ohm)"].append(float(parts[15]))
    parameters_dict["Reverse"]["R_shunt (Ohm)"].append(float(parts[16]))
    parameters_dict["Reverse"]["FF (%)"].append(float(parts[17]))
    parameters_dict["Reverse"]["Eff. (%)"].append(float(parts[18]))

    return parameters_dict


### MAIN FUNCTIONS TO READ STABILITY PARAMETERS FROM TXT FILE ###

def read_parameters_data(mainfile, encoding):
    """
    READS STABILITY PARAMETERS DATA FROM THE TXT FILE AND ORGANIZES IT INTO A DICTIONARY

    Parameters:
        mainfile (str): Path to the file to be read.
        encoding (str): Encoding of the file.
    Returns:
        parameters_dict (dict): Dictionary containing the read data.
    """
    
    # Initialize the main dictionary (with nested dictionaries=
    parameters_dict = {"Forward": {"Time (Hours)":[],"Voc (V)":[],"Jsc (mA/cm2)":[],"V_MPP (V)":[],"J_MPP (mA/cm2)":[],"P_MPP (mW/cm2)":[],"R_series (Ohm)":[],"R_shunt (Ohm)":[],"FF (%)":[],"Eff. (%)":[] },
                                "Reverse": {"Time (Hours)":[],"Voc (V)":[],"Jsc (mA/cm2)":[],"V_MPP (V)":[],"J_MPP (mA/cm2)":[],"P_MPP (mW/cm2)":[],"R_series (Ohm)":[],"R_shunt (Ohm)":[],"FF (%)":[],"Eff. (%)":[] },
                                }

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
                parameters_dict=read_header_line(line, parameters_dict)
                
            # Process data section lines
            if section == 'data': 
                # Identify start of measurement data
                if not line.startswith('Time'):    
                    # Process MPPT data section
                    parameters_dict=read_parameters_line(line, parameters_dict)
                

    # Convert lists to numpy arrays for numerical processing
    for measurement in ['Forward', 'Reverse']:
        if measurement in parameters_dict:
            for key in ["Time (Hours)",	"Voc (V)", "Jsc (mA/cm2)", "V_MPP (V)", "J_MPP (mA/cm2)", "P_MPP (mW/cm2)", "R_series (Ohm)", "R_shunt (Ohm)", "FF (%)", "Eff. (%)"]:
                parameters_dict[measurement][key] = np.array(parameters_dict[measurement][key])

    return parameters_dict
    

### ACTUAL PARSING FUNCTION; WHICH WRITES THE DATA INTO AN ARCHIVE ###
def parse_parameters_data_to_archive(entry, mainfile, encoding):
    """
    Reads Stability Parameters data from a data file and parses it into the NOMAD entry.

    Parameters:
        entry (NOMADEntry): The NOMAD entry object to be filled with data.
        mainfile (str): The path to the main data file.
        encoding (str): The encoding of the data file.
    Note:
        It reads the data from the file, extracts relevant information, and populates the corresponding fields of the NOMAD entry object.

    """

    # Read data from measurement file into dictionary
    parameters_dict = read_parameters_data(mainfile, encoding)
  
    # Fill specific data fields for parameters Measurement
    for measurement in ['Reverse','Forward']:   
        if entry.scan == measurement:
            entry.time = parameters_dict[measurement]["Time (Hours)"] * ureg('hour')
            entry.open_circuit_voltage=parameters_dict[measurement]['Voc (V)'] * ureg('V')
            entry.short_circuit_current_density=parameters_dict[measurement]['Jsc (mA/cm2)'] * ureg('mA/cm^2')
            entry.fill_factor=parameters_dict[measurement]['FF (%)'] / 100
            entry.efficiency=parameters_dict[measurement]['Eff. (%)']
            entry.potential_at_maximum_power_point=parameters_dict[measurement]['V_MPP (V)'] * ureg('V')
            entry.current_density_at_maximum_power_point=parameters_dict[measurement]['J_MPP (mA/cm2)'] * ureg('mA/cm^2')
            entry.power_at_maximum_power_point=parameters_dict[measurement]['P_MPP (mW/cm2)'] * ureg('mW/cm^2')
            entry.series_resistance_ohm=parameters_dict[measurement]['R_series (Ohm)'] * ureg('ohm')
            entry.shunt_resistance_ohm=parameters_dict[measurement]['R_shunt (Ohm)'] * ureg('ohm')    

    # Check box "measurement data was extracted from data file"   
    entry.measurement_data_was_extracted_from_data_file = True

   


