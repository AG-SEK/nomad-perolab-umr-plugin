#### WORK IN PROGRESS - AARON


from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from scipy.optimize import curve_fit

from .helper_functions import get_samples_from_group
from .update_layout import update_layout_umr


def read_luqy_data(mainfile, encoding='ISO-8859-1', device_name=None):
    """
    Parses a LuQY measurement file into a structured dictionary.
    
    Parameters:
        mainfile (str): Path to the file.
        encoding (str): File encoding.
    
    Returns:
        luqy_dict: Parsed data with header and measurement sections.
    """
    data_headers = [
        "Wavelength (nm)",
        "Luminescence flux density (photons/(s cm² nm))",
        "Raw spectrum (counts)"]

    # Create dictionary with header keys (and empty lists to append data)
    luqy_dict = {
        'name': mainfile.split('\\')[-1]
    }
    for key in data_headers:
        luqy_dict[key]=[]

    header_section = True  # Track which section we are in
    first_line = True  # Track first line for datetime

    
    with open(mainfile, encoding=encoding) as file:
        for raw_line in file:
            line = raw_line.strip()
            parts = line.split('\t')
            # Skip empty lines
            if not line:
                continue
            
            # Process first line as datetime
            if first_line:
                if len(parts)==1:
                    try:
                        luqy_dict["datetime"] = datetime.strptime(line, "%m/%d/%Y %I:%M:%S %p")
                    except ValueError:
                        print(f"Error: Invalid datetime format -> {line}")
                    first_line = False
                else:
                    print(f"Error: Invalid Datetime line format -> {line}")
                continue
            
            # Detect transition from header to measurement data
            if "---------" in line:
                header_section = False
                continue

            # Skip Data header line
            if "Wavelength (nm)" in line:
                continue
            
            # Process header section
            if header_section:
                if len(parts) == 2:
                    key, value = parts
                    try:
                        luqy_dict[key] = float(value)
                    except ValueError:
                        luqy_dict[key] = value
                else:
                    
                    print(f"Error: Invalid header line format -> {line}")
                
            # Process measurement data
            elif len(parts) == 3:
                try:
                    wavelength, lum_flux, raw_spectrum = map(float, parts)
                    luqy_dict["Wavelength (nm)"].append(wavelength)
                    luqy_dict["Luminescence flux density (photons/(s cm² nm))"].append(lum_flux)
                    luqy_dict["Raw spectrum (counts)"].append(raw_spectrum)
                except ValueError:
                    print(f"Error: Invalid measurement data format -> {line}")
            else:
                print(f"Error: Invalid measurement line length -> {line}")
    
    # Convert lists to numpy arrays
    for key in data_headers:
        luqy_dict[key] = np.array(luqy_dict[key], dtype=float)
    
    if device_name:
        luqy_dict['device']= device_name
    
    return luqy_dict





##############################################################################################
##############################################################################################

colors = pio.templates["UMR"].layout.colorway
colors = colors + colors + colors # Liste Colors zu klein!!!


def gaussian(x, a, x0, sigma):
    """
    Gaussian function, representing a single Gaussian peak.

    Parameters:
    x (array): The input values (typically wavelength values).
    a (float): Amplitude (height) of the Gaussian peak.
    x0 (float): The center of the peak (mean of the distribution).
    sigma (float): Standard deviation (width) of the Gaussian peak.

    Returns:
    array: The computed Gaussian values for each input `x`.
    """
    # Calculate and return the Gaussian function values
    return a * np.exp(-((x - x0) ** 2) / (2 * sigma ** 2))


def double_gaussian(x, a1, x01, sigma1, a2, x02, sigma2):
    """
    Double Gaussian function, representing the sum of two Gaussian peaks.

    Parameters:
    x (array): The input values (typically wavelength values).
    a1 (float): Amplitude (height) of the first Gaussian peak.
    x01 (float): The center of the first peak (mean of the distribution).
    sigma1 (float): Standard deviation (width) of the first Gaussian peak.
    a2 (float): Amplitude (height) of the second Gaussian peak.
    x02 (float): The center of the second peak (mean of the distribution).
    sigma2 (float): Standard deviation (width) of the second Gaussian peak.

    Returns:
    array: The computed values representing the sum of the two Gaussian peaks for each input `x`.
    """
    # Return the sum of the two Gaussian functions
    return gaussian(x, a1, x01, sigma1) + gaussian(x, a2, x02, sigma2)



def fit_gaussian(wavelengths, luminescence, double=False):
    """
    Fit a Gaussian (single or double) to the given luminescence data.

    Parameters:
    wavelengths (array): Array of wavelength values (independent variable).
    luminescence (array): Array of luminescence values (dependent variable).
    double (bool): If True, fits a double Gaussian; if False, fits a single Gaussian. Default is False.

    Returns:
    tuple: 
        - fit_func (function): A lambda function that represents the fitted Gaussian(s).
        - peak_positions (tuple): The positions (wavelengths) of the peaks.
        - popt (array): The optimized parameters for the Gaussian fit.
    """
    
    # Find the index of the maximum luminescence value
    peak_index = np.argmax(luminescence)
    
    # Determine the wavelength and value at the peak
    peak_wavelength = wavelengths[peak_index]
    peak_value = luminescence[peak_index]

    if len(wavelengths) < 4 or len(luminescence) < 4:
        print("Not enough Datapoints for gaussian fit. Please check fit range.")
        return None, None, None
    
    if double:
        # Initial guesses for the parameters of a double Gaussian
        p0 = [peak_value, peak_wavelength, 10, peak_value / 2, peak_wavelength + 20, 10]
        
        try:
            # Perform the curve fitting for the double Gaussian
            popt, _ = curve_fit(double_gaussian, wavelengths, luminescence, p0=p0)
            
            # Define the fitted double Gaussian function using the optimized parameters
            def fit_func(x):
                return double_gaussian(x, *popt)
            
            # Return the fitted function, the positions of the two peaks, and the parameters
            return fit_func, (popt[1], popt[4]), popt
        except (RuntimeError, TypeError):
            # If the double Gaussian fitting fails, print a message and fall back to a single Gaussian
            print("Double Gaussian fit failed, falling back to single Gaussian.")
            try:
                popt, _ = curve_fit(gaussian, wavelengths, luminescence, p0=[peak_value, peak_wavelength, 10])
                def fit_func(x):
                    return gaussian(x, *popt)
                return fit_func, (popt[1],), popt
            except (RuntimeError, TypeError):
                print("Single Gaussian fit also failed.")
                return None, None, None

            #fit_func, peak_positions, popt = fit_gaussian(wavelengths, luminescence, double=False)
            #return fit_func, peak_positions, popt
            #return fit_gaussian(wavelengths, luminescence, double=False)
    else:
        # Initial guesses for the parameters of a single Gaussian
        p0 = [peak_value, peak_wavelength, 10]
        
        try:
            # Perform the curve fitting for the single Gaussian
            popt, _ = curve_fit(gaussian, wavelengths, luminescence, p0=p0)
            
            # Define the fitted single Gaussian function using the optimized parameters
            def fit_func(x):
                return gaussian(x, *popt)
            
            # Return the fitted function, the position of the peak, and the parameters
            return fit_func, (popt[1],), popt
        except RuntimeError:
            # If the single Gaussian fitting fails, print an error message and return None
            print("Gaussian fit failed.")
            return None, None, None


def find_fit_range(wavelengths, luminescence, threshold=0.00001, center_wavelength=None):
    """
    Automatically determines the fitting range where the luminescence drops close to zero.
    
    The function identifies the region around a given center wavelength where the luminescence 
    is above a specified threshold and returns the corresponding wavelength range.

    Parameters:
    wavelengths (array-like): The array of wavelengths to search through.
    luminescence (array-like): The array of luminescence values corresponding to each wavelength.
    threshold (float): The minimum value of luminescence considered to be significant (default is 0.00001).
    center_wavelength (float): The central wavelength around which the fitting range is to be determined (default is 800 nm).

    Returns:
    tuple: A tuple containing the left and right bounds of the fitting range, in wavelength units.
    """

    # Find wavelength of peak
    if not center_wavelength:
        peak_index = np.argmax(luminescence)
        center_wavelength = wavelengths[peak_index]

    # Start searching for the left boundary from the center wavelength
    left_index = peak_index
    while left_index > 0 and luminescence[left_index] > threshold:
        left_index -= 1
    
    # Start searching for the right boundary from the center wavelength
    right_index = peak_index
    while right_index < len(wavelengths) - 1 and luminescence[right_index] > threshold:
        right_index += 1
    
    print(f"The peak is at wavelength {center_wavelength} nm")
    print(f"The fit range was automatically set to {wavelengths[left_index]} nm to {wavelengths[right_index]} nm ")
    # Return the wavelengths corresponding to the left and right boundaries of the fit range
    return wavelengths[left_index], wavelengths[right_index]



def convert_nm_to_ev(wavelength_nm):
    """
    Converts wavelength in nanometers to energy in electron volts (eV).

    Parameters:
    wavelength_nm (float): The wavelength in nanometers to convert.

    Returns:
    float: The equivalent energy in electron volts (eV).
    """
    # Import necessary constants from Solar.constants (h: Planck's constant, c: speed of light, e: elementary charge)
    from ..constants import c, e, h
    
    # Apply the formula to convert wavelength (in nm) to energy (in eV)
    return (h * c) / (wavelength_nm * 1e-9 * e) 


def plot_and_fit_luqy(luqy_list, showplot=True, names=None, perform_gaussian_fit=True, double_gauss=False, fit_range="automatic", threshold=0.00001, center_wavelength=None, x_axis_ev=False, show_fit=True, show_fit_in_legend=False, show_ivoc_and_luqy=True, fig= None,  grid=False, normalized=False, trace_color=None):
    

    """
    Creates a Plotly figure displaying luminescence quantum yield (LuQY) data and optionally 
    performs a Gaussian or double Gaussian fit.

    Parameters:
    -----------
    luqy_list : list of dict
        A list of dictionaries containing spectral data. Each dictionary should include at least 
        the keys "Wavelength (nm)" and "Luminescence flux density (photons/(s cm² nm))".
    showplot : bool, optional
        If `True`, the plot is displayed immediately. Default: `True`.
    names : list of str, optional
        A list of names for the individual spectra. If `None`, default names such as "PL 1", "PL 2" are used.
    show_maximum : bool, optional
        If `True`, the maximum luminescence is marked with a dashed line. Default: `False`.
    double_gauss : bool, optional
        If `True`, a double Gaussian function is fitted to the data. Otherwise, a single Gaussian fit is applied. Default: `False`.
    fit_range : str or list, optional
        Defines the range for the Gaussian fit:
        - `"automatic"` (default): The range is determined automatically.
        - `"full"`: The entire dataset is used for fitting.
        - `[min, max]`: Manually specify the fit range in nanometers.
    threshold : float, optional
        Threshold for automatically determining the fit range. Default: `0.00001`.
    center_wavelength : float, optional
        The wavelength around which the automatic fit range is centered. Default: `800 nm`.
    x_axis_ev : bool, optional
        If `True`, the x-axis is displayed in electron volts (eV) instead of nanometers (nm). Default: `False`.
    show_fit : bool, optional
        If `True`, the Gaussian fit is plotted. Default: `True`.
    show_fit_in_legend : bool, optional
        If `True`, legends for the fitted curves are displayed. Default: `False`.
    show_parameters : bool, optional
        If `True`, iVoc and LuQY values are displayed as annotations in the plot. Default: `True`.

    Returns:
    --------
    fig : plotly.graph_objects.Figure
        The generated Plotly figure.
    all_params : list of list or None
        A list containing the fit parameters for each spectrum. The content depends on whether a single 
        or double Gaussian fit was chosen:
        - **Single Gaussian fit (`double_gauss=False`)**:
          `params = [a, x0, sigma]`, where:
            - `a`     : Amplitude of the Gaussian curve.
            - `x0`    : Center of the Gaussian peak.
            - `sigma` : Standard deviation of the Gaussian curve.
        - **Double Gaussian fit (`double_gauss=True`)**:
          `params = [a1, x01, sigma1, a2, x02, sigma2]`, where:
            - `a1, x01, sigma1` : Parameters of the first Gaussian curve.
            - `a2, x02, sigma2` : Parameters of the second Gaussian curve.
        If no fit was successful, `all_params` contains `None` at the respective position.

    Example:
    --------
    ```python
    # Example usage of the function
    fig, params = plot_luqy(luqy_list, double_gauss=True, show_fit=True)
    ```
    """
     
    
    if not fig:
        fig = go.Figure()
        
    # Define List for return values    
    all_params = []
    peak_wavelengths = []
    
    for i, luqy_dict in enumerate(luqy_list):
    
        # Extract data
        iVoc = luqy_dict.get("iVoc (V)", "N/A")
        LuQY = luqy_dict.get("LuQY (%)", "N/A")
        wavelengths = np.array(luqy_dict["Wavelength (nm)"])
        luminescence = np.array(luqy_dict["Luminescence flux density (photons/(s cm² nm))"])

        # Optional: Normalize luminescence
        if normalized:
            luminescence = luminescence / np.max(luminescence)  # Normierung auf 1
            yaxis_title='Normalized PL Intensity'
        else:
            yaxis_title='PL Intensity [photons/(s cm² nm)]'

    
        # Umwandlung in eV falls erforderlich
        if x_axis_ev:
            wavelengths_plot = convert_nm_to_ev(wavelengths)
            xaxis_minor_dtick=0.05
            xaxis_dtick=0.1
            x_label = 'Photon Energy [eV]'
        else:
            wavelengths_plot = wavelengths
            xaxis_minor_dtick=25
            xaxis_dtick=50
            x_label = 'Wavelength [nm]'
                
        # Define names for the curves
        if isinstance(names, list):
            list_names = names   
        else:
            list_names = [f"PL {i+1}" for i in range(len(luqy_dict))]


        # Daten plotten
        if not trace_color:
            trace_color = colors[i]

        fig.add_trace(go.Scatter(x=wavelengths_plot, y=luminescence, mode='lines', name=list_names[i], line_color=trace_color))
        
    
        # Determine fit range based on user input
        if isinstance(fit_range, list) and len(fit_range) == 2:
            fit_min, fit_max = fit_range
        elif fit_range == "full":
            fit_min, fit_max = min(wavelengths), max(wavelengths)
        else:  # Default to "automatic"
            fit_min, fit_max = find_fit_range(wavelengths, luminescence,  threshold=threshold, center_wavelength=center_wavelength)

        # Apply wavelength range filter
        mask = (wavelengths >= fit_min) & (wavelengths <= fit_max)
        wavelengths_fit = wavelengths[mask]
        luminescence_fit = luminescence[mask]


        # Gaussian-Fit
        if perform_gaussian_fit:
            fit_func, fitted_peaks, params = fit_gaussian(wavelengths_fit, luminescence_fit, double=double_gauss)

            if not fit_func and not params:
                print("Error: Gaussian Fit Failed")
                return
            
            # Determine peak wavelengths
            if len(params)==6:
                a1, x01, sigma1, a2, x02, sigma2 = params
                peak_wavelength= x01 if a1 > a2 else x02
                second_peak_wavelength = x01 if a1 < a2 else x02
                peak_ratio = a1 / a2 if a1 > a2 else a2 / a1

            elif len(params)==3:
                a, x0, sigma = params
                peak_wavelength = x0
                second_peak_wavelength = None
                peak_ratio = None  # Only one peak, so no ratio

            if show_fit and fit_func:
                fit_wavelengths = np.linspace(min(wavelengths_fit), max(wavelengths_fit), 500)
                fit_luminescence = fit_func(fit_wavelengths)
                
                if x_axis_ev:
                    fit_wavelengths_plot = convert_nm_to_ev(fit_wavelengths)
                else:
                    fit_wavelengths_plot = fit_wavelengths

                    fig.add_trace(go.Scatter(x=fit_wavelengths_plot, y=fit_luminescence, mode='lines', name='Gaussian Fit', line=dict(dash='dot'), showlegend=show_fit_in_legend))
                
                if double_gauss and params is not None:
                    g1 = gaussian(fit_wavelengths, params[0], params[1], params[2])
                    g2 = gaussian(fit_wavelengths, params[3], params[4], params[5])
                    fig.add_trace(go.Scatter(x=fit_wavelengths_plot, y=g1, mode='lines', name='Gaussian 1', line=dict(dash='dot'), showlegend=show_fit_in_legend))
                    fig.add_trace(go.Scatter(x=fit_wavelengths_plot, y=g2, mode='lines', name='Gaussian 2', line=dict(dash='dot'), showlegend=show_fit_in_legend))
                
                for peak in fitted_peaks:
                    peak_plot = convert_nm_to_ev(peak) if x_axis_ev else peak
                    if x_axis_ev:
                        annotation_text=f'{peak_plot:.2f}'
                    else:
                        annotation_text=f'{peak_plot:.0f}'


                    fig.add_trace(go.Scatter(x=[peak_plot, peak_plot], y=[0, fit_func(peak)], mode='lines', name='Fitted Peak', line=dict(dash='dash', color=trace_color), showlegend=show_fit_in_legend))
                    fig.add_annotation(x=peak_plot, y=0, yanchor="top", text=annotation_text, font_size=15, showarrow=False, font_color=trace_color)

    
        # Annotate iVoc and LuQY in top-left corner
        if show_ivoc_and_luqy:   
            fig.add_annotation(x=0.05, y=0.95,
                            text=f'iVoc: {iVoc} V <br>LuQY: {LuQY}%',
                            showarrow=False,
                            xref='paper', yref='paper',
                            align='left',
                            font_size=20)
       

        # Append Return values to Lists
        peak_wavelengths.append(peak_wavelength)
        all_params.append(params)

    # Update Layout of Plot
    fig.update_layout(
        xaxis_title=x_label,
        # Major Ticks
        xaxis_dtick=xaxis_dtick,
        xaxis_tickmode='linear',
        # Minor Ticks
        xaxis_minor_dtick=xaxis_minor_dtick, # Depends if eV or nm
        xaxis_minor_tickmode='linear',
        yaxis_title=yaxis_title, # Depends if normalized or not normalized (see above)
        yaxis_rangemode="tozero",
        yaxis_exponentformat="power",
        yaxis_tickfont_size=28,
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
    )

    # Correct layout
    update_layout_umr(fig)
        
    if showplot:
        fig.show()

    return fig, peak_wavelengths, second_peak_wavelength, peak_ratio, all_params





################################


def create_boxplot_data_luqy(luqy_data, batch, excel_filename=None, double_gauss=True, show_fit=True, show_ivoc_and_luqy=True, showfit=True):
    """
    Erstellt einen DataFrame für Boxplot-Daten aus luqy_data.

    Parameters:
    - luqy_data (list): Liste von Dictionaries mit Messdaten, die 'lab_id' und 'iVoc (V)' enthalten.
    - batch (dict): Batch-Informationen mit Gruppen und zugehörigen Lab-IDs.
    - excel_filename (str): Name der Excel-Datei, falls gespeichert werden soll (default: "boxplot_data.xlsx").

    Returns:
    - pd.DataFrame: DataFrame mit den Boxplot-Daten.
    """
    # Mapping von lab_id zu Gruppeninformationen
    lab_id_to_group = {}
    for group in batch.get("groups", []):
        samples = get_samples_from_group(group=group, basic_samples=True)
        for lab_id in samples:
            lab_id_to_group[lab_id] = {
                "group_number": group["group_number"],
                "group_description": group["group_description"]
            }

    # Liste für die Daten
    table_data = []
    
    for measurement in luqy_data:
        lab_id = measurement["device"]
        group_info = lab_id_to_group.get(lab_id)
        if not group_info:
            continue  # Überspringen, wenn keine Gruppenzuordnung vorhanden

        fig, peak_wavelengths, second_peak_wavelength, peak_ratio, all_params = plot_and_fit_luqy([measurement], showplot=showfit, double_gauss=double_gauss, show_fit=True, show_ivoc_and_luqy=True, names=[lab_id])
        peak_wavelength = peak_wavelengths[0]
        params = all_params[0]

        row = {
            "lab_id": lab_id,
            "group_number": group_info["group_number"],
            "group_description": group_info["group_description"],
            'measurement_name': measurement['name'],
            "internal_open_circuit_voltage (V)": measurement.get("iVoc (V)", None),
            "luminescent_quantum_yield (%)": measurement.get("LuQY (%)", None),
            'peak_wavelength (nm)': peak_wavelength,
            'second_peak_wavelength (nm)': second_peak_wavelength if double_gauss else None,
            'peak_ratio': peak_ratio,
            'amplitude a1': params[0],
            'peak_wavelength x01':params[1],
            'standard_deviation sigma1': params[2],
            'amplitude a2': params[3] if double_gauss else None,
            'peak_wavelength x02': params[4] if double_gauss else None,
            'standard_deviation sigma2': params[5] if double_gauss else None,
        }
        table_data.append(row)

    # DataFrame erstellen
    boxplot_df = pd.DataFrame(table_data)
    
    # In Excel speichern, falls gewünscht
    if excel_filename:
        boxplot_df.to_excel(excel_filename, index=False)

    return boxplot_df


def plot_boxplot_luqy(boxplot_df, parameter="internal_open_circuit_voltage (V)", group_descriptions=None, fig=None, showplot=True, xaxis_title="Groups", show_group_names=True, group_order=None, hoverlabel="lab_id", trace_color=None, showlegend=False):
    """
    Erstellt ein Boxplot für iVoc-Werte, gruppiert nach Gruppen.
    
    Parameters:
    - boxplot_df (pd.DataFrame): DataFrame mit den Daten für das Boxplot.
    
    Returns:
    - plotly.graph_objects.Figure: Das generierte Plotly-Boxplot.
    """
    if not fig:
        fig = go.Figure()
    
    # Map parameter to corresponding y-axis title and plot title
    # here are the standard yaxis titles and titles defined
    parameter_map = {
        'internal_open_circuit_voltage (V)': ('iV<sub>OC</sub> [V]', 'internal V<sub>OC</sub> (LuQY)'),
        "luminescent_quantum_yield (%)": ("LuQY [%]", "LuQY"),
        'peak_wavelength (nm)': ("PL peak wavelength  [nm]", "PL peak (Gaussian Fit)"),
        'second_peak_wavelength (nm)': ("PL peak wavelength  [nm]", "2nd PL peak (Gaussian Fit)"),
        'peak_ratio': ("PL peak ratio", "PL peak ratio"),
        'amplitude a1': ("amplitude [(photons/(s cm² nm))]", "PL peak (Gaussian Fit)"),
        'peak_wavelength x01': ("PL peak wavelength  [nm]", "PL peak (Gaussian Fit)"),
        'standard_deviation sigma1': ("standard deviation [nm]", "PL peak (Gaussian Fit)"),
        'amplitude a2': ("amplitude [(photons/(s cm² nm))]", "2nd PL peak (Gaussian Fit)"),
        'peak_wavelength x02': ("PL peak wavelength  [nm]", "2nd PL peak (Gaussian Fit)"),
        'standard_deviation sigma2': ("standard deviation [nm]", "2nd PL peak (Gaussian Fit)")
    }


    if parameter not in parameter_map:
        raise ValueError(f"Invalid parameter '{parameter}'. Must be one of {', '.join(parameter_map.keys())}.")
    
    yaxis_title, title = parameter_map[parameter]

    # Get batch ID:
    #first_device_id = boxplot_df['lab_id'][0]
    # batch_id = f"{first_device_id.split('_')[0]}_{first_device_id.split('_')[1]}"  # Unused variable

    # Extract unique group numbers from the DataFrame
    if group_order is None:
        group_order = sorted(boxplot_df["group_number"].unique())


    for group_number in group_order:
        group_data = boxplot_df[boxplot_df["group_number"] == group_number]
        
        fig.add_trace(
            go.Box(
                y=group_data[parameter],
                x=group_data["group_number"],
                name=str(group_number),
                boxmean=True,
                hovertext=group_data[hoverlabel],
                showlegend=showlegend,
                marker_color=trace_color
            )
        )
    

      # Update trace settings (e.g., size, color, jitter)
    fig.update_traces(
        marker_size=10,
        fillcolor='rgba(0,0,0,0)',  # Transparent box fill
        boxpoints='all',  # Show all data points
        boxmean='sd',  # Show mean and standard deviation
        pointpos=0,  # Position of points relative to box
        jitter=0.5,  # Add jitter for better separation between points
    )

    #if yaxis_title in ["PL peak wavelength  [nm]", ""]:
    #    yaxis_rangemode="normal"
    #else:
    #    yaxis_rangemode="tozero"
    yaxis_rangemode="normal"

    fig.update_layout(
        title=title,
        title_font_size=38, 
        yaxis_title=yaxis_title,
        xaxis_title=xaxis_title,
        xaxis_type="category",
        yaxis_rangemode=yaxis_rangemode
    )
    

    # Order x axis category
    if group_order:
        fig.update_layout(
            xaxis_categoryorder='array',
            xaxis_categoryarray=group_order
    )

    # Show group names on the x-axis
    if show_group_names:
        group_names = []
        for group_number in group_order:
            description_value = boxplot_df.loc[boxplot_df['group_number'] == group_number, 'group_description'].iloc[0]
            group_names.append(description_value)
        
        fig.update_layout(
            xaxis_tickmode='array',
            xaxis_tickvals=group_order,
            xaxis_ticktext=group_names,
        )

    # Update x-axis tick labels if group descriptions are provided
    if group_descriptions:
        fig.update_layout(
            xaxis_tickmode='array',
            xaxis_tickvals=group_order,
            xaxis_ticktext=group_descriptions,
        )

   # Correct layout
    update_layout_umr(fig)

    if showplot:
        fig.show()

    return fig
