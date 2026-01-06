import pandas as pd


def get_ipce(filepath):
    '''
    Loads measured ipce data from txt file.
    Parameters:
        - filepath (str): filepath of the measurement data from Cicci_Research

    Returns:
        - ipce (pandas dataframe) with
        'wavelength' in nm
        'eqe'
        'current_density' in mA/cm2
        'integrated_current_density' in mA/cm2
        'intensity' in mW/cm2

    '''
    with open(filepath) as file:
        lines = file.readlines()
    data_start = lines.index('## Data ##\t\t\t\t\n') + 3  # find the start of the data section
    column_names = ['wavelength', 'eqe', 'current_density', 'integrated_current_density', 'intensity']
    ipce = pd.read_csv(filepath, delimiter='\t', skiprows=data_start-1, names=column_names)
    ipce = ipce.apply(pd.to_numeric, errors='coerce')  # convert all columns to numeric values
    ipce['eqe'] = ipce['eqe']/100

    return ipce