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
from ..characterization.jv_measurement import UMR_SolarCellJVCurve
from .read_header_line import read_header_line

def read_JVparameter_line(line, jv_dict, measurement, header_params):  
    """
    READS PARAMETER LINES (Intensity, Voc, Jsc, ...) AND ADDS THEM TO NESTED DICTIONARIES (Forward and Reverse)
    
    Parameters:
        line (str): current line in file
        jv_dict (dict): dictionary to be filled with data
        measurement (str): Forward or Reverse
    Returns:
        jv_dict (dict): dictionary filled with data 
    """         
    
    parts=line.split()                         # Split line at tab character

    for i, value in enumerate(parts[1:]):
        # Check if value is NaN -> set value to 0.0 (for some very bad JV curves e.g. Efficiency is NaN)
        if value.lower() == 'nan':
            value = 0.0
    
        # Add value to jv_dict
        jv_dict[measurement].update({
            header_params[i+1]: float(value)
            })

    #jv_dict[measurement].update({              # Add key-value pairs to nested dictionaries (Forward and Reverse)
    #    "Int. (SUN(%))": float(parts[1]),
    #    "Voc (V)": float(parts[2]),
    #    "Jsc (mA/cm2)": float(parts[3]),
    #    "V_MPP (V)": float(parts[4]),
    #    "J_MPP (mA/cm2)": float(parts[5]),
    #    "P_MPP (mW/cm2)": float(parts[6]),
    #    "R_series (Ohm)": float(parts[7]),
    #    "R_shunt (Ohm)": float(parts[8]),
    #    "FF (%)": float(parts[9]),
    #    "Eff. (%)": float(parts[10])
    #    })
    return jv_dict


def read_JVcurve_line(line, jv_dict):
    """
    READS JV CURVE DATA (V and J) LINES AND APPENDS THE VALUES TO THE LISTS IN THE NESTED DICTIONARIES (Forward and Reverse)
    
    Parameters:
        line (str): current line in file
        jv_dict (dict): dictionary to be filled with data
    Returns:
        jv_dict (dict): dictionary filled with data
    """
    
    parts=line.split('\t')                                         # Split line at tab character
    if len(parts) >= 4:                                         # Chekc if all data is present (sometimes only 2 (wrong) values were saved in the end -> ignore them)
        jv_dict["Forward"]["V (V)"].append(float(parts[0]) if parts[0] else None)        # Append values to list in nested dictionaries (Forward and Reverse)
        jv_dict["Forward"]["J (mA/cm2)"].append(float(parts[1]) if parts[1] else None)
        jv_dict["Reverse"]["V (V)"].append(float(parts[2]) if parts[2] else None)
        jv_dict["Reverse"]["J (mA/cm2)"].append(float(parts[3]) if parts[3] else None)
    return jv_dict



### MAIN FUNCTIONS TO READ JV DATA FROM TXT FILE ###

def read_jv_data(mainfile, encoding):
    """
    READS JV DATA FROM THE TXT FILE AND ORGANIZES IT INTO A DICTIONARY

    Parameters:
        mainfile (str): Path to the file to be read.
        encoding (str): Encoding of the file.
    Returns:
        jv_dict (dict): Dictionary containing the read data.
    """
    
    # Initialize the main dictionary (with nested dictionaries and empty lists to store data)
    jv_dict = {"Forward": {"V (V)": [], "J (mA/cm2)": []}, "Reverse": {"V (V)": [], "J (mA/cm2)": []}}
    
    # Initialize some helper variables
    section = None       # Current section (header or data)
    data_section = None   # Current measurement (parameters or JVcurve)

    # Open File and read it line by line
    with open(mainfile, 'r', encoding=encoding) as file:
  
        for line in file:
            line = line.rstrip()         # Remove trailing whitespaces from the line
            
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
                jv_dict=read_header_line(line, jv_dict)
                
            # Process data section lines
            if section == 'data': 
                
                # Identify start of parameters section
                if line.startswith("Scan"):
                    data_section = "parameters"
                    header_params = line.split()  # Get headers of parameter section
                    continue
                # Skip line with units
                elif line.startswith("SUN(%)"):
                    continue
                # Process parameters section
                elif data_section=="parameters" and line.startswith(("Forward", "Reverse", "FW", "RV")):
                    measurement = line.split()[0] # Identify current measurement (Forward or Reverse)
                    if measurement =="FW":
                        measurement = "Forward"
                    elif measurement == "RV":
                        measurement = "Reverse"
                    jv_dict=read_JVparameter_line(line, jv_dict, measurement, header_params)
                    continue
                
                # Identify start of JV curve section
                elif line.startswith("V (V)") or line.startswith("V_FW (V)"):  # old files V (V), new files V_FW (V)
                    data_section = "JVcurve"
                    continue
                # Process JV curve section
                elif data_section == "JVcurve":
                    jv_dict=read_JVcurve_line(line, jv_dict)
                    continue

    # Convert lists to numpy arrays for numerical processing
    for measurement in ['Forward', 'Reverse']:
        if measurement in jv_dict:
            for key in ['V (V)', 'J (mA/cm2)']:
                # Filter out None values
                filtered_list = [x for x in jv_dict[measurement][key] if x is not None]
                # Convert list to numpy array (float)
                jv_dict[measurement][key] = np.array(filtered_list, dtype=float)

    return jv_dict
    


### ACTUAL PARSING FUNCTION; WHICH WRITES THE DATA INTO AN ARCHIVE ###
def parse_jv_data_to_archive(entry, mainfile, encoding):
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
    jv_dict = read_jv_data(mainfile, encoding)

    # Fill specific data fields for JV Measurement from dictionary
    entry.active_area = float(jv_dict['Cell area (cm2)']) * ureg('cm^2') if 'Cell area (cm2)' in jv_dict else None  # Maybe use Cell Area (cm2) instead
    entry.temperature = float(jv_dict['Temperature']) if 'Temperature' in jv_dict else None                 #* ureg('°C') -> lead to error

    entry.minimum_voltage = float(jv_dict['Vmin (V)']) * ureg('V')  if 'Vmin (V)' in jv_dict else None
    entry.maximum_voltage = float(jv_dict['Vmax (V)']) * ureg('V') if 'Vmax (V)' in jv_dict else None
    entry.voltage_step = float(jv_dict['dV (V)']) * ureg('V') if 'dV (V)' in jv_dict else None
    entry.scan_rate = float(jv_dict['Scan rate (mV/s)']) * ureg('mV/s') if 'Scan rate (mV/s)' in jv_dict else None
    entry.auto_detect_voc = jv_dict['Auto-detect Voc']  if 'Auto-detect Voc' in jv_dict else None
    entry.initial_delay = float(jv_dict['Inital delay (s)']) * ureg('s') if 'Inital delay (s)' in jv_dict else None
    entry.scan_order = jv_dict['Scan Order'] if 'Scan Order' in jv_dict else None

    
    # keys from Stability JV curves
    entry.scan_order = jv_dict['Scan direction'] if 'Scan direction' in jv_dict else entry.scan_order
    # entry.voltage_range = jv_dict['Voltage Range'] if 'Voltage Range' in jv_dict else None
    # Es gibt noch mehr Einträge zu ranges

    # old key names
    entry.voltage_step = float(jv_dict['dV (mV)']) * ureg('V') if 'dV (mV)' in jv_dict else entry.voltage_step  # mV is false, it should be V
    entry.scan_rate = float(jv_dict['Scan Rate (mV/s)']) if 'Scan Rate (mV/s)' in jv_dict else entry.scan_rate
    entry.voltage_step = float(jv_dict['Voltage Step (mV)']) * ureg('mV')  if 'Voltage Step (mV)' in jv_dict else entry.voltage_step

    # for attributes which reappear for different keys set else to attribute not None (otherwise attribut is set to None)
    # If conditions are neccesary, because otherhwise one would get KeyErrors in cases were the key does not exist
    # ureg: UnitRegistry imported from pint -> merges value and unit 

    # JV Curve data will be added in the next step
    entry.jv_curve = [] 
    for measurement in ['Reverse','Forward']:   
        JVCurve = UMR_SolarCellJVCurve()            
        JVCurve.scan = measurement

        # JV Data
        JVCurve.voltage = jv_dict[measurement]['V (V)']* ureg('V')
        JVCurve.current_density = jv_dict[measurement]['J (mA/cm2)'] * ureg('mA/cm^2')
        
        # Parameters
        JVCurve.light_intensity=jv_dict[measurement]['Int.'] / 100 * 100 * ureg('mW/cm^2') if 'Int.' in jv_dict[measurement] else None                # originally in SUN(%)
            # TODO Check Intensity (currently given values is SUN(100mW/cm²) in %)
        JVCurve.open_circuit_voltage=jv_dict[measurement]['Voc'] * ureg('V') if 'Voc' in jv_dict[measurement] else None                               # originally in V
        JVCurve.short_circuit_current_density=jv_dict[measurement]['Jsc'] * ureg('mA/cm^2') if 'Jsc' in jv_dict[measurement] else None                # originally in mA/cm2                                                         # originally in %
        JVCurve.potential_at_maximum_power_point=jv_dict[measurement]['V_MPP'] * ureg('V') if 'V_MPP' in jv_dict[measurement] else None               # originally in V
        JVCurve.current_density_at_maximum_power_point=jv_dict[measurement]['J_MPP'] * ureg('mA/cm^2') if 'J_MPP' in jv_dict[measurement] else None   # originally in mA/cm2
        JVCurve.power_density_at_maximum_power_point=jv_dict[measurement]['P_MPP'] * ureg('mW/cm^2') if 'P_MPP' in jv_dict[measurement] else None     # originally in mW/cm2
        JVCurve.series_resistance_ohm=jv_dict[measurement]['R_series'] * ureg('ohm') if 'R_series' in jv_dict[measurement] else None                  # originally in Ohm
        JVCurve.shunt_resistance_ohm=jv_dict[measurement]['R_shunt'] * ureg('ohm') if 'R_shunt' in jv_dict[measurement] else None                     # originally in Ohm
        JVCurve.fill_factor=round(jv_dict[measurement]['FF'] / 100, 4) if 'FF' in jv_dict[measurement] else None                                                # originally in %
        JVCurve.efficiency=jv_dict[measurement]['Eff.'] if 'Eff.' in jv_dict[measurement] else None                                                   # originally in %

        # Data from Stability JV Files
        JVCurve.efficiency=jv_dict[measurement]['Eff'] if 'Eff' in jv_dict[measurement] else JVCurve.efficiency                                       # originally in %
        JVCurve.series_resistance_ohm=jv_dict[measurement]['Rs'] * ureg('ohm') if 'Rs' in jv_dict[measurement] else JVCurve.series_resistance_ohm     # originally in Ohm
        JVCurve.shunt_resistance_ohm=jv_dict[measurement]['R//'] * ureg('ohm') if 'R//' in jv_dict[measurement] else JVCurve.shunt_resistance_ohm     # originally in Ohm

        # Append JV Curve to entry
        entry.jv_curve.append(JVCurve)
        
    # Check box "measurement data was extracted from data file"   
    entry.measurement_data_was_extracted_from_data_file = True

    return jv_dict










