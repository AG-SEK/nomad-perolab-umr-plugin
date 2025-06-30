# Functions for calculations on EQE measurements


import plotly.graph_objects as go  
from plotly.subplots import make_subplots

import numpy as np

from . import get_am15g_array
from ..constants import *



# Get AM1.5G spectrum
wavelength_am15g = get_am15g_array('wavelength') # in nm
   
def interpolate_eqe_data(eqe_data, wavelength_data=wavelength_am15g, showplot=False):
    """
    Interpolates EQE (External Quantum Efficiency) data to the wavelength values of the AM1.5G solar spectrum.

    Parameters:
        - eqe_data (dict): A dictionary containing EQE data with keys 'wavelength' and 'eqe'.
        - wavelength_data (numpy.ndarray, optional): Wavelength data to interpolate to. Defaults to AM1.5G spectrum wavelengths.
        - showplot (bool, optional): If True, plots the original and interpolated EQE data. Defaults to False.

    Returns:
        numpy.ndarray: Interpolated EQE data.
    """
    
    # Get EQE Data
    wavelength = np.array(eqe_data['wavelength'])
    eqe = np.array(eqe_data['eqe'])
   
    # Interpolation of the measured eqe data to the values of the AM1.5G spetrum
    eqe_interpolated = np.interp(wavelength_data, wavelength, eqe)

    # Plotting the original and interpolated data using Plotly
    if showplot==True:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=wavelength, y=eqe*100,
                                mode='markers', name='Original EQE Data'))
        fig.add_trace(go.Scatter(x=wavelength_data, y=eqe_interpolated*100,
                                mode='lines', name='Interpolated EQE Data'))
        
        fig.update_layout(
            xaxis_title='Wavelength (nm)',
            yaxis_title='EQE (%)',
            xaxis_range=[min(wavelength), max(wavelength)],  
            )
        
        fig.show()
        return eqe_interpolated, fig
    
    else:
        return eqe_interpolated


def calculate_jsc(eqe_data, device=None, showplot=False):
    """
    Calculates the short-circuit current density (Jsc) from EQE (External Quantum Efficiency) data.

    Parameters:
        - eqe_data (dict): A dictionary containing EQE data with keys 'wavelength' and 'eqe'.
        - device (str, optional): Name of the device for annotation in the plot. Defaults to None.
        - showplot (bool, optional): If True, plots the Jsc, AM1.5G power spectrum, and EQE data. Defaults to False.

    Returns:
        float: The calculated Jsc in mA/cm².
        plotly.graph_objs._figure.Figure (optional): The plotly figure object if showplot is True.
    """
     
    # Convert to numpy arrays
    wavelength_am15g = get_am15g_array('wavelength') # in nm
    photon_flux_am15g = get_am15g_array('photon_flux_per_nm') # in 1/(cm²nm)

   # Interpolate EQE data to AM1.5G data
    eqe_interpolated = interpolate_eqe_data(eqe_data)

    # Calculate Jsc using trapz (numerical integration)
    j_sc = np.trapz(eqe_interpolated * photon_flux_am15g * e, wavelength_am15g) * 1000 # in mA/cm²


    ### OPTIONAL PLOT ###

    if showplot:
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Plot product of EQE and power spectrum (current)
        current = eqe_interpolated * photon_flux_am15g * e * 1e3 # in mA/cm²/nm
        fig.add_trace(go.Scatter(x=wavelength_am15g, y=current,
                                 mode='lines', fill='tozeroy', name='Jsc'))
        
        # Plot AM1.5G power spectrum
        fig.add_trace(go.Scatter(x=wavelength_am15g, y=get_am15g_array('photon_current_per_nm'),
                                 mode='lines', name='AM1.5G photon current'))
        
        # Plot interpolated EQE
        fig.add_trace(go.Scatter(x=np.array(eqe_data['wavelength']), y=np.array(eqe_data['eqe']) * 100,
                                 mode='markers', name='Measured EQE', yaxis='y2', marker_symbol = 'circle'))
        fig.add_trace(go.Scatter(x=wavelength_am15g, y=eqe_interpolated * 100,
                                 mode='lines', name='Interpolated EQE', yaxis='y2'))
        
       
        # Annotate the Jsc value
        fig.add_annotation(
            x=890, 
            y=0.09,
            xanchor = 'right',
            yanchor = 'middle',
            text=f"<b>Device</b>: {device} <br><b>Jsc</b>: {j_sc:.2f} mA/cm²",
            font_size = 22,
            showarrow=False,
            align= 'left',
            )
        
        fig.update_layout(
            xaxis_title='Wavelength [nm]',
            yaxis=dict(
                title='Current [mA/(cm²nm)]',
                side='right',
                range = [0,0.1],

            ),
            yaxis2=dict(
                title='EQE [%]',
                side='left',
                range = [0,100],
                position=1
            ),
        )
    
        fig.update_layout(
            xaxis_range=[min(eqe_data['wavelength']), max(eqe_data['wavelength'])],
            legend_font_size=22,
            legend_xanchor = 'center',
            legend_x = 0.47,
            legend_y = 1.2,
            legend_orientation = 'h',
        )
        
        fig.show()
        return j_sc, fig
    
    # If showplot = False
    else:
        return j_sc


