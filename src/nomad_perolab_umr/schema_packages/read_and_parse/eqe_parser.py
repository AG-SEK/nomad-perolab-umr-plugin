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
from nomad.datamodel.metainfo.eln import SolarCellEQE
from nomad.units import ureg

from ..characterization.eqe_measurement import UMR_SolarCellEQE
from ..helper_functions import *
from .read_header_line import read_header_line

### HELPER FUNCTIONS TO READ LINES FOR SPECIFIC CASES ###

def read_EQEcurve_line(line, eqe_dict):
    """
    READS EQE CURVE DATA LINES AND APPENDS THE VALUES TO THE LISTS IN THE DICTIONARY
    
    Parameters:
        line (str): current line in file
        eqe_dict (dict): dictionary to be filled with data
    Returns:
        eqe_dict (dict): dictionary filled with data
    """
    
    parts=line.split()                                         # Split line at tab character
    eqe_dict["Wavelength (nm)"].append(float(parts[0]))        # Append values to list in dictionary
    eqe_dict["IPCE (%)"].append(float(parts[1]))
    eqe_dict["J device (mA/cm2)"].append(float(parts[2]))
    #eqe_dict["J integrated (mA/cm2)"].append(float(parts[3]))
    eqe_dict["J integrated (mA/cm2)"].append(float(parts[3]) if parts[3].lower() != "nan" else 0.0) # First value is NaN but should appear as "0" in data (otherwise error when updating archive)
    eqe_dict["Intensity (mW/cm2)"].append(float(parts[4]))

    return eqe_dict



### MAIN FUNCTIONS TO READ JV DATA FROM TXT FILE ###

def read_eqe_data(mainfile, encoding):
    """
    READS EQE DATA FROM THE TXT FILE AND ORGANIZES IT INTO A DICTIONARY

    Parameters:
        mainfile (str): Path to the file to be read.
        encoding (str): Encoding of the file.
    Returns:
        eqe_dict (dict): Dictionary containing the read data.
    """
    
    # Initialize the main dictionary to store data
    eqe_dict = {"Wavelength (nm)":[], "IPCE (%)": [], "J device (mA/cm2)": [], "J integrated (mA/cm2)": [], "Intensity (mW/cm2)": []}
    
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
                eqe_dict=read_header_line(line, eqe_dict)
                
            # Process data section lines
            if section == 'data': 
                # Identify start of measurement data
                if not line.startswith('Wavelength'):    
                    # Process EQE curve section
                    eqe_dict=read_EQEcurve_line(line, eqe_dict)
                

    # Convert lists to numpy arrays for numerical processing
    for measurement in ["Wavelength (nm)", "IPCE (%)", "J device (mA/cm2)", "J integrated (mA/cm2)", "Intensity (mW/cm2)"]:
        if measurement in eqe_dict:
            eqe_dict[measurement] = np.array(eqe_dict[measurement])

    return eqe_dict
    

### ACTUAL PARSING FUNCTION; WHICH WRITES THE DATA INTO AN ARCHIVE ###
def parse_eqe_data_to_archive(entry, mainfile, encoding):
    """
    Reads EQE data from a data file and parses it into the NOMAD entry.

    Parameters:
        entry (NOMADEntry): The NOMAD entry object to be filled with data.
        mainfile (str): The path to the main data file.
        encoding (str): The encoding of the data file.
    Note:
        It reads the data from the file, extracts relevant information, and populates the corresponding fields of the NOMAD entry object.

    """

    # Read data from measurement file into dictionary
    eqe_dict = read_eqe_data(mainfile, encoding)

    # Fill specific data fields for EQE Measurement
    entry.active_area = float(eqe_dict['Cell area (cm2)']) * ureg('cm^2') if 'Cell area (cm2)' in eqe_dict else None
    entry.temperature = float(eqe_dict['Temperature']) if 'Temperature' in eqe_dict else None

    entry.minimum_wavelength = float(eqe_dict['Lmin (nm)']) * ureg('nm') if 'Lmin (nm)' in eqe_dict else None
    entry.wavelength_step = float(eqe_dict['dL (nm)']) * ureg('nm') if 'dL (nm)' in eqe_dict else None
    entry.maximum_wavelength = float(eqe_dict['Lmax (nm)']) * ureg('nm') if 'Lmax (nm)' in eqe_dict else None
    entry.averaging = int(eqe_dict['Averaging']) if 'Averaging' in eqe_dict else None
    entry.delay_time = float(eqe_dict['Delay Time (s)']) * ureg('s') if 'Delay Time (s)' in eqe_dict else None
    entry.autorange = eqe_dict['Autorange'] if 'Autorange' in eqe_dict else None
    entry.bias_voltage = float(eqe_dict['Bias Voltage (V)']) * ureg('V') if 'Bias Voltage (V)' in eqe_dict else None
    entry.bias_light = float(eqe_dict['Bias light (a.u.)']) if 'Bias light (a.u.)' in eqe_dict else None
    entry.spectral_mismatch = float(eqe_dict['Spectral Mismatch']) if 'Spectral Mismatch' in eqe_dict else None

    # Create UMR_SolarCellEQE Object and append it to eqe_data subsection
    sc_eqe = UMR_SolarCellEQE(
        wavelength = eqe_dict['Wavelength (nm)'] * ureg('nm'),
        eqe = eqe_dict['IPCE (%)'] / 100,
        device_current_density = eqe_dict['J device (mA/cm2)'] * ureg('mA/cm^2'),
        integrated_current_density = eqe_dict['J integrated (mA/cm2)'] * ureg('mA/cm^2'),
        intensity = eqe_dict['Intensity (mW/cm2)'] * ureg('mW/cm^2'),
        )
    entry.eqe_data = sc_eqe

    # Create SolarCellEQE Object (because data is automatically read from file with EQE_Analyzer)
    # append to advanced_eqe-data subsection
    sc_advanced_eqe = SolarCellEQE(
        eqe_data_file = entry.data_file,
        header_lines = 23,
        )
    entry.advanced_eqe_data = sc_advanced_eqe
  
    # Check box "measurement data was extracted from data file"   
    entry.measurement_data_was_extracted_from_data_file = True

   


   










