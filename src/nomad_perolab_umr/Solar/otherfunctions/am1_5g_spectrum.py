import os

import numpy as np
import pandas as pd

from ..constants import c, e, h


def get_am15g():
    '''
    Loads and cleans solar AM15G spectrum between 280 and 4000nm.
    Parameters: 
    
    Returns:
        - pandas dataframe with 
        'wavelength' in nm
        'power' in W/m²/nm (This is the spectral Irradiance)
        'photon_flux' in 1/m²/s/nm
    '''
    # Construct path to xlsx file 
    current_module_path = os.path.dirname(os.path.abspath(__file__))              # Path to this module
    print(current_module_path)
    path_to_xlsx_file = os.path.join(current_module_path, 'Data', 'AM15G_ASTMG173.xlsx')


    am15g = pd.read_excel(path_to_xlsx_file)
    am15g = am15g.iloc[2:, 1:4]
    am15g.columns = ['wavelength', 'power', 'photon_flux']
    am15g = am15g.apply(pd.to_numeric, errors='coerce')
    am15g = am15g.reset_index(drop=True)
    return am15g



def get_am15g_array(value):
    """
    Retrieve AM1.5G solar spectrum data.
    
    Parameters:
        value (str): The type of data to retrieve. It can be one of the following:
            - 'wavelength': Returns the wavelength array in nanometers (nm).
            - 'photon_energy': Returns the photon energy array in electron volts (eV).
            - 'spectral_irradiance_per_nm': Returns the spectral irradiance array per nm in milliwatts per square centimeter (mW/(cm²*nm)).
            - 'spectral_irradiance_per_eV': Returns the spectral irradiance array per eV in milliwatts per square centimeter (mW/(cm²*eV)).
            - 'photon_flux_per_nm': Returns the photon flux array per nm in 1 per square centimeter (1/(s*cm²*nm)).
            - 'photon_flux_per_eV': Returns the photon flux array per eV in 1 per square centimeter (1/(s*cm²*eV)).
            - 'photon_current_per_nm': Returns the photon crrent array per nm in milliamps per square centimeter (mA/(cm²*nm)).
            - 'photon_current_per_eV': Returns the photon crrent array per eV in milliamps per square centimeter (mA/(cm²*eV)).
    
    Returns:
        numpy.ndarray: Array containing the requested data.
    """

    # Construct path to txt file 
    current_module_path = os.path.dirname(os.path.abspath(__file__))    # Path to this module
    path_to_txt_file = os.path.join(current_module_path, 'Data', 'AM1_5G.txt')
    
    # Check if file exists
    if not os.path.exists(path_to_txt_file):
        raise FileNotFoundError(f"Data file not found at: {path_to_txt_file}")
    
    # Read data from txt file
    data = np.loadtxt(path_to_txt_file, skiprows=1)
    wavelength_nm = data[:, 0]  # in nm
    irradiance_W_per_m2_per_nm = data[:, 1]   # in W/(m²*nm)

    ## CALCULATE DATA

    # Photon energy
    photon_energy_J = h*c/(wavelength_nm*1e-9)
    photon_energy_eV = photon_energy_J/e
    
    # Spectral irradiance
    irradiance_W_per_cm2_per_nm = irradiance_W_per_m2_per_nm / 10000
    irradiance_mW_per_cm2_per_nm = irradiance_W_per_cm2_per_nm * 1000
    irradiance_W_per_cm2_per_eV = irradiance_W_per_cm2_per_nm * wavelength_nm**2 * 1e-9 /(h*c) * e
    irradiance_mW_per_cm2_per_eV = irradiance_W_per_cm2_per_eV * 1000

    # Spectral Photon Flux
    photon_flux_per_cm2_per_nm = irradiance_W_per_cm2_per_nm /photon_energy_J
    photon_flux_per_cm2_per_eV = irradiance_W_per_cm2_per_eV /photon_energy_J

    # SpectralPhoton Current
    photon_current_mA_per_cm2_per_nm = photon_flux_per_cm2_per_nm * e * 1000 # in mA/(cm²nm)
    photon_current_mA_per_cm2_per_eV = photon_flux_per_cm2_per_eV * e * 1000 # in mA/(cm²eV)

    ## RETURN DATA
    result_map = {
        "wavelength": wavelength_nm,
        "photon_energy": photon_energy_eV,
        "spectral_irradiance_per_nm": irradiance_mW_per_cm2_per_nm,
        "spectral_irradiance_per_eV": irradiance_mW_per_cm2_per_eV,
        "photon_flux_per_nm": photon_flux_per_cm2_per_nm,
        "photon_flux_per_eV": photon_flux_per_cm2_per_eV,
        "photon_current_per_nm": photon_current_mA_per_cm2_per_nm,
        "photon_current_per_eV": photon_current_mA_per_cm2_per_eV,
    }
    
    if value not in result_map:
        raise ValueError(f"Invalid value '{value}'. Choose from {list(result_map.keys())}.")
    
    return result_map[value]
    


    
def get_am0_array(value):
    """
    Retrieve spectrum data from an Excel file.

    Parameters:
        value (str): The type of data to retrieve. It can be one of the following:
            - 'wavelength': Returns the wavelength array in nanometers (nm).
            - 'photon_energy': Returns the photon energy array in electron volts (eV).
            - 'spectral_irradiance_per_nm': Returns the spectral irradiance in mW/(cm²*nm).
            - 'spectral_irradiance_per_eV': Returns the spectral irradiance in mW/(cm²*eV).
            - 'photon_flux_cumulative': Returns the cumulative photon flux in 1/(cm²*s).
            - 'photon_flux_per_nm': Returns the photon flux per nm in 1/(cm²*s*nm).
            - 'photon_flux_per_eV': Returns the photon flux per eV in 1/(cm²*s*eV).
            - 'photon_current_per_nm': Returns the photon current per nm in mA/(cm²*nm).
            - 'photon_current_per_eV': Returns the photon current per eV in mA/(cm²*eV).

    Returns:
        numpy.ndarray: Array containing the requested data.
    """

    # Construct path to excel file 
    current_module_path = os.path.dirname(os.path.abspath(__file__))
    path_to_excel_file = os.path.join(current_module_path, 'Data', 'AM0.xlsx')
        
    # Check if file exists
    if not os.path.exists(path_to_excel_file):
        raise FileNotFoundError(f"Data file not found at: {path_to_excel_file}")
    

    # Read data from file
    df = pd.read_excel(path_to_excel_file, sheet_name="Spectrum")
    wavelength_nm = df.iloc[:, 0].to_numpy()
    irradiance_W_per_m2_per_nm = df.iloc[:, 1].to_numpy()
    cumulative_flux_cm2_s = df.iloc[:, 2].to_numpy()

    ## CALCULATE DATA

    # Photon energy
    photon_energy_J = h*c/(wavelength_nm*1e-9)
    photon_energy_eV = photon_energy_J/e

     # Spectral irradiance
    irradiance_W_per_cm2_per_nm = irradiance_W_per_m2_per_nm / 10000
    irradiance_mW_per_cm2_per_nm = irradiance_W_per_cm2_per_nm * 1000
    irradiance_W_per_cm2_per_eV = irradiance_W_per_cm2_per_nm * wavelength_nm**2 * 1e-9 /(h*c) * e
    irradiance_mW_per_cm2_per_eV = irradiance_W_per_cm2_per_eV * 1000

    # Spectral Photon Flux
    photon_flux_per_cm2_per_nm = irradiance_W_per_cm2_per_nm /photon_energy_J
    photon_flux_per_cm2_per_eV = irradiance_W_per_cm2_per_eV /photon_energy_J

    
    # SpectralPhoton Current
    photon_current_mA_per_cm2_per_nm = photon_flux_per_cm2_per_nm * e * 1000 # in mA/(cm²nm)
    photon_current_mA_per_cm2_per_eV = photon_flux_per_cm2_per_eV * e * 1000 # in mA/(cm²eV)

    result_map = {
        "wavelength": wavelength_nm,
        "photon_energy": photon_energy_eV,
        "spectral_irradiance_per_nm": irradiance_mW_per_cm2_per_nm,
        "spectral_irradiance_per_eV": irradiance_mW_per_cm2_per_eV,
        "photon_flux_cumulative": cumulative_flux_cm2_s,
        "photon_flux_per_nm": photon_flux_per_cm2_per_nm,
        "photon_flux_per_eV": photon_flux_per_cm2_per_eV,
        "photon_current_per_nm": photon_current_mA_per_cm2_per_nm,
        "photon_current_per_eV": photon_current_mA_per_cm2_per_eV,
    }


    if value not in result_map:
        raise ValueError(f"Invalid value '{value}'. Choose from {list(result_map.keys())}.")

    return result_map[value]