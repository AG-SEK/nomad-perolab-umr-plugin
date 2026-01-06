from datetime import datetime

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

from ..constants import e
from ..otherfunctions import get_am15g_array
from .update_layout import update_layout_umr


################## EQE CURVE PLOT ##################
def plot_eqe(
    eqe_data=None, full_eqe_data=None, names="lab_id", grid=False, toggle_grid_button=False, 
    fig=None, linemode='lines', showplot=True, normalized=False, normalization_wavelength=400,
    show_marker=False, marker_wavelengths=[700], delta_marker_wavelengths=25, marker_opacity=1,
    normalize_to_jsc=False, measured_jsc=None, line_width=4
):
    """
    Plots external quantum efficiency (EQE) curves for photovoltaic cells using Plotly.

    Parameters:
    - eqe_data (list of dict, optional): List of dictionaries representing EQE curves.
        Each dictionary should have the keys:
            - 'wavelength': List of wavelength values for the EQE curve.
            - 'eqe': List of corresponding external quantum efficiency values (between 0 and 1).
    - full_eqe_data (list of dict, optional): List of dictionaries containing full EQE data from NOMAD Oasis (for trace metadata).
    - names (list or str, optional): List of cell names or a string indicating the naming method ('lab_id' or 'datetime').
    - grid (bool, optional): Flag to control the visibility of the grid in the plot (default: False).
    - toggle_grid_button (bool, optional): Flag to add a toggle button for the grid (default: False).
    - fig (plotly.graph_objects.Figure, optional): Existing Plotly figure. If None, a new figure will be created.
    - linemode (str, optional): Line mode for the scatter plot ('lines', 'markers', 'lines+markers', etc.). Default is 'lines'.
    - showplot (bool, optional): Whether to display the plot (default: True).
    - normalized (bool, optional): Whether to normalize EQE curves to a given wavelength (default: False).
    - normalization_wavelength (int, optional): Wavelength used for normalization (required if `normalized` is True).
    - show_marker (bool, optional): Whether to show markers at specific wavelengths (default: False).
    - marker_wavelengths (list, optional): List of wavelengths where markers should be placed.
    - delta_marker_wavelengths (int, optional): Shift applied to marker positions for different traces.
    - marker_opacity (float, optional): Opacity of markers (default: 1).
    - normalize_to_jsc (bool, optional): Whether to normalize EQE to a measured short-circuit current (Jsc).
    - measured_jsc (list, optional): List of measured Jsc values (required if `normalize_to_jsc` is True).

    Returns:
    - fig (plotly.graph_objects.Figure): Plotly figure object.
    """

    # If marker wavelengths are given (also given by default)
    if show_marker:
        linemode=='lines+markers'
        marker_opacity = 0

    if measured_jsc:
        normalize_to_jsc=True

   # Extract EQE data from full_eqe_data and create corresponding metadata list
    metadata = []
    if full_eqe_data:
        eqe_data = [eqe['eqe_data'] for eqe in full_eqe_data]
        metadata = [
            {"datetime": datetime.fromisoformat(eqe["datetime"]), "device": eqe["device"]}
            for eqe in full_eqe_data
        ]
    elif not eqe_data:
        raise ValueError("Either 'eqe_data' or 'full_eqe_data' must be provided.")

    # Create a Plotly figure
    if not fig:
        fig = go.Figure()

    # Define names for the curves
    if isinstance(names, list):
        list_names = names
    elif names == 'lab_id':
        if not full_eqe_data:
            raise ValueError("'full_eqe_data' must be provided to use 'lab_id' as names.")
        list_names = [eqe["device"] for eqe in full_eqe_data]
    elif names == "datetime":
        if not full_eqe_data:
            raise ValueError("'full_eqe_data' must be provided to use 'datetime' as names.")
        list_names = [meta['datetime'].strftime("%Y-%m-%d %H:%M:%S") for meta in metadata]
    else:
        list_names = [f"EQE {i+1}" for i in range(len(eqe_data))]

    # Add traces for each EQE curve
    for i, eqe in enumerate(eqe_data):
        try:
            # Versuche, die Werte aus dem Dictionary zu extrahieren
            wavelengths = np.array(eqe['wavelength'])
            eqe_values = np.array(eqe['eqe'])  # Convert to percentage
        except KeyError:
            # Falls der Schlüssel nicht gefunden wird
            print("There is no wavelength in the eqe_data given. Most probably you want to enter data in full_eqe_data")

        # Normalize EQE if requested
        if normalized:
            if normalization_wavelength is None:
                raise ValueError("Normalization wavelength must be specified when `normalized` is True.")
            if normalization_wavelength not in wavelengths:
                raise ValueError(f"Normalization wavelength {normalization_wavelength} not found in wavelength data.")
            normalization_index = np.where(wavelengths == normalization_wavelength)[0][0]
            normalization_factor = eqe_values[normalization_index]
            print(f"Normalized at {normalization_wavelength} with normalization factor {normalization_factor}")
            eqe_values = (eqe_values / normalization_factor) / 100  # division by 100, because in plot trace * 100 (The other EQEs are displayed in %)
        
        # Normalize EQE to Jsc if requested
        if normalize_to_jsc:
            if measured_jsc is None:
                raise ValueError("'measured_jsc' must be provided for Jsc normalization.")
            
            # Get AM1.5G spectrum
            am15g_wavelengths = get_am15g_array("wavelength")
            am15g_photon_flux = get_am15g_array('photon_flux_per_nm') # in 1/(cm²nm)
            
            # Interpolate AM1.5G spectrum to match EQE wavelengths
            am15g_photon_flux_interp = np.interp(wavelengths, am15g_wavelengths, am15g_photon_flux)
            # Calculate integral of EQE * AM1.5G spectrum
            integral_value = np.trapezoid(eqe_values * am15g_photon_flux_interp * e , wavelengths)*1000 # in mA/cm²
            # Compute normalization factor
            normalization_factor = measured_jsc[i] / integral_value

            # Adjust eqe data based on normalization factor
            eqe_values = eqe_values * normalization_factor
            print(f"Integrated current of bare EQE measurement: {integral_value} mA/cm²")
            print(f"Normalized to measured Jsc of {measured_jsc[i]} mA/cm² with normalization factor {normalization_factor}")

        colors = pio.templates["UMR"].layout.colorway
        trace_color = colors[i % len(colors)]  # Modulo-Operator for repeating colors

        trace = go.Scatter(
            x=wavelengths,            # x-values
            y=eqe_values*100,             # y-values (normalized or raw) in %
            name=list_names[i],
            mode=linemode,
            meta=metadata[i] if metadata else None,
            marker_opacity=marker_opacity,
            line_color = trace_color,
            line_width=line_width,
            hovertext=metadata[i]["device"],
        )

        # Add the trace to the figure
        fig.add_trace(trace)    

        # Add marker traces at specific wavelengths if requested
        if show_marker:
            for original_marker_wavelength in marker_wavelengths:
                marker_wavelength = original_marker_wavelength
                if delta_marker_wavelengths:
                    marker_wavelength = marker_wavelength + i*delta_marker_wavelengths # Shift marker for each trace
                # Find the index of the nearest wavelength to the marker wavelength
                closest_idx = np.argmin(np.abs(wavelengths - marker_wavelength))
                closest_wavelength = wavelengths[closest_idx]
                closest_eqe_value = eqe_values[closest_idx]
                fig.add_trace(go.Scatter(
                    x=[closest_wavelength],  # Wellenlänge für den Marker
                    y=[closest_eqe_value],  # EQE-Wert an dieser Wellenlänge
                    marker=dict(color=trace_color, size=12),  # Use the color from the original trace
                    mode='markers',  # Nur Marker
                    name='Marker',  # Alle Marker haben denselben Namen
                    line_width = line_width, # Thicker Lines for better readibility
                    showlegend=False,  # Marker nicht in der Legende anzeigen
                    meta=metadata[i] if metadata else None,
                ))

            

    # Definition of standard axis layout
    fig.update_layout(
        xaxis_title='Wavelength [nm]',
        yaxis_title='EQE [%]',
        #xaxis_dtick=50,
        #yaxis_dtick=0.1,
        yaxis_range = [0, 100],
        # Show/hide grid based on the 'grid' parameter       
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid,
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid,
    )

    if normalized:
        fig.update_layout(
            yaxis_title="Normalized EQE",
            yaxis_range = [0, 1.19],
    )
        
    if normalize_to_jsc:
        fig.update_layout(
            yaxis_title="To Jsc normalized EQE",
    )
    
    # Create grid button if requested
    if toggle_grid_button:
        fig.update_layout(updatemenus=pio.templates['UMR'].layout.updatemenus)

    # Correct layout
    update_layout_umr(fig)

    # Show Plot
    if showplot:
        fig.show()

    return fig  # Return the Plotly figure object for further customization