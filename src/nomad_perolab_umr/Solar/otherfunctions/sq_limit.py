# This file includes functions for the calculation of the radiative limit

import numpy as np
import scipy.integrate as integrate
import plotly.graph_objects as go
import pandas as pd

from ..constants import e, h, c, k_B
from ..plottemplate import umr_plot_template



def add_rainbow_to_figure(figure, xaxis="eV", y_height=100, opacity=0.3, deep_copy=True):
    """
    Adds a rainbow-colored background to a Plotly figure to visually represent the visible spectrum.

    Parameters:
    -----------
    figure : plotly.graph_objects.Figure
        The input Plotly figure to which the rainbow background will be added.

    xaxis : str, optional
        Defines the x-axis scale: "eV" for photon energy or "nm" for wavelength. Default is "eV".

    y_height : float, optional
        The vertical extent of the rainbow background. Determines the height of the heatmap in y-units.

    opacity : float, optional
        Opacity of the rainbow overlay (0 = fully transparent, 1 = fully opaque). Default is 0.3.

    deep_copy : bool, optional
        If True, creates a deep copy of the figure to preserve the original. Default is True.

    Returns:
    --------
    fig : plotly.graph_objects.Figure
        A Plotly figure with an added rainbow background as a heatmap.
    """

    if deep_copy:
        fig = go.Figure(figure.to_dict())
    else:
        fig = figure

    # Sichtbares Spektrum: 380 - 750 nm (ungefähr)
    wavelengths_nm = np.linspace(380, 750, 1000)
    photon_energy_eV = (h * c) / (wavelengths_nm * 1e-9) / e  # Umrechnung

    # Farbwerte für typisches sichtbares Licht (vereinfachte, aber realistische Zuordnung)
    # Liste: [(nm, hex_color)]
    color_map = [
        (380, "#9400D3"),  # Violett
        (450, "#0000FF"),  # Blau
        (490, "#00FFFF"),  # Cyan
        (510, "#00FF00"),  # Grün
        (570, "#FFFF00"),  # Gelb
        (590, "#FFA500"),  # Orange
        (620, "#FF0000"),  # Rot
        (780, "#7F0000"),  # Tiefrot (optional für sanften Übergang)
    ]

    # Extrahiere X-Achsen-Werte & Farbliste passend zum gewählten Maßstab
    if xaxis == "nm":
        x_vals = np.array([c[0] for c in color_map])
        color_vals = [c[1] for c in color_map]
    elif xaxis == "eV":
        x_vals = np.array([(h * c) / (nm * 1e-9) / e for nm, _ in color_map])
        color_vals = [c[1] for c in color_map]
        x_vals = x_vals[::-1]       # Umkehren wegen steigender Energie bei kürzeren Wellen
        color_vals = color_vals[::-1]
    else:
        raise ValueError("xaxis must be 'nm' or 'eV'")

    # Normiere x_vals für colorscale
    x_min, x_max = min(x_vals), max(x_vals)
    norm_vals = (x_vals - x_min) / (x_max - x_min)

    colorscale = list(zip(norm_vals, color_vals))

    # Simulierte Heatmap mit konstantem Z-Wert (für reines Farbband)
    full_x = np.linspace(x_min, x_max, 1000)
    z = np.outer(np.ones(2), full_x)

    fig.add_trace(go.Heatmap(
        z=z,
        x=full_x,
        y=[0, y_height],
        colorscale=colorscale,
        showscale=False,
        opacity=opacity,
        hoverinfo='skip'
    ))

    return fig


from ..otherfunctions import get_am15g_array
am15g_wavelengths_nm = get_am15g_array('wavelength')
am15g_irradiance_mW_per_cm2_per_nm = get_am15g_array('spectral_irradiance_per_nm')

def calculate_jsc(bandgap_eV=None, bandgap_nm=None, irradiance_mW_per_cm2_per_nm=am15g_irradiance_mW_per_cm2_per_nm, wavelengths_nm=am15g_wavelengths_nm, showplots=False):
    """
    Calculate the short-circuit current density (Jsc) for a given bandgap under the AM1.5G solar spectrum.

    Parameters:
    -----------
    bandgap_eV : float, optional
        Bandgap energy in electron volts (eV). Provide either this or `bandgap_nm`, not both.

    bandgap_nm : float, optional
        Bandgap wavelength in nanometers (nm). Provide either this or `bandgap_eV`, not both.

    irradiance_mW_per_cm2_per_nm : array_like
        Spectral irradiance in mW/cm²/nm. Default is AM1.5G standard spectrum.

    wavelengths_nm : array_like
        Wavelength array corresponding to the irradiance, in nm.

    showplots : bool, optional
        If True, show plots of photon flux vs photon energy and wavelength.

    Returns:
    --------
    Jsc : float
        Short-circuit current density in mA/cm².
    fig_eV, fig_nm : plotly.graph_objects.Figure (optional)
        The interactive plot figures (only if showplots=True).
    """

    # Calculate missing bandgap value from the other
    if bandgap_nm and not bandgap_eV:
        bandgap_eV = h * c / (bandgap_nm*1e-9) / e
    elif bandgap_eV and not bandgap_nm:
        bandgap_nm = h * c / (bandgap_eV * e) *1e9 
    elif (not bandgap_eV and not bandgap_nm) or (bandgap_eV and bandgap_nm):
        print("Please enter either a bandgap_eV or a bandgap_nm")
        return

    # Convert wavelength to photon energy in Joules and eV
    photon_energy_J = h * c / (wavelengths_nm * 1e-9)
    photon_energy_eV = photon_energy_J / e

   # Convert irradiance from per nm to per eV
    irradiance_mW_per_cm2_per_eV = irradiance_mW_per_cm2_per_nm * wavelengths_nm**2 * 1e-9 / (h * c) * e

    # Calculate photon flux: photons per cm² per second per eV or nm
    photon_flux_per_cm2_per_eV = irradiance_mW_per_cm2_per_eV / 1000 / photon_energy_J  # W to photons
    photon_flux_per_cm2_per_nm = irradiance_mW_per_cm2_per_nm / 1000 / photon_energy_J

    # Only include photons with energy >= bandgap
    mask = photon_energy_eV >= bandgap_eV

    # Integrate photon flux over energy range above bandgap to get Jsc
    Jsc = -1 * e * np.trapezoid(photon_flux_per_cm2_per_eV[mask], photon_energy_eV[mask]) * 1e3  # A to mA

    print(f"The Jsc for a bandgap of {bandgap_eV:.2f} eV ({bandgap_nm:.1f} nm) is {Jsc:.2f} mA/cm²")
 
    if showplots:

        # Calculate total and used photon flux for visualization
        total_photon_number_per_cm2 = (-1) * np.trapezoid(photon_flux_per_cm2_per_eV, photon_energy_eV)
        total_photon_current_mA_per_cm2 = total_photon_number_per_cm2 * e * 1000 # A to mA
        used_photon_number_per_cm2 = (-1) * np.trapezoid(photon_flux_per_cm2_per_eV[mask], photon_energy_eV[mask])
        used_photon_number_percent = (used_photon_number_per_cm2 / total_photon_number_per_cm2) * 100  # Prozentuale Nutzung der Photonen
        used_photon_current_mA_per_cm2 = used_photon_number_per_cm2 * e * 1000 # A to mA

        # Plot: Photon flux vs. photon energy (eV)
        fig_eV = go.Figure()
        # PLot spectrum
        fig_eV.add_trace(go.Scatter(
            x=photon_energy_eV,
            y=photon_flux_per_cm2_per_eV,
            mode='lines',
            name=f'AM1.5G - Total Photon Current: {total_photon_current_mA_per_cm2:.2f} mA/cm²',
            line_color="black",
            line_width=0.3))
        
        # Plot absorbed photons (area)
        fig_eV.add_trace(go.Scatter(
            x=photon_energy_eV[mask],
            y=photon_flux_per_cm2_per_eV[mask],
            fill='tozeroy',
            mode='none',
            name=f'Used Photon Current: {used_photon_current_mA_per_cm2:.2f} mA/cm² ({used_photon_number_percent:.2f} %)'))
        
        # Plot Bandgap (line)
        bandgap_photon_flux = np.interp(bandgap_eV, photon_energy_eV[::-1], photon_flux_per_cm2_per_eV[::-1]) # [::-1] um Liste umzudrehen und aufsteigende Werte für die Photon enery zu erhalten
        fig_eV.add_trace(go.Scatter(x=[bandgap_eV, bandgap_eV], y=[0, bandgap_photon_flux], mode='lines', name=f'Bandgap ({bandgap_eV:.2f} eV)', line_color='red'))

        fig_eV.update_layout(
            title='photon flux vs. photon energy',
            xaxis_title='photon energy (eV)',
            yaxis_title='photon flux [cm<sup>-2</sup>·eV<sup>-1</sup>·s<sup>-1</sup>]',        
            legend_font_size=20,
            yaxis_rangemode = "nonnegative",
            title_font_size = 34,
            yaxis_range = [0, 5e17]
            )
        fig_eV = add_rainbow_to_figure(fig_eV, y_height=5*1e17, xaxis="eV", opacity=0.1)
        fig_eV.show()

        # Plot: Photon flux vs. wavelength (nm)
        mask = wavelengths_nm <= bandgap_nm
        fig_nm = go.Figure()
        fig_nm.add_trace(go.Scatter(
            x=wavelengths_nm,
            y=photon_flux_per_cm2_per_nm,
            mode='lines',
            name=f'AM1.5G - Total Photon Current: {total_photon_current_mA_per_cm2:.2f} mA/cm²',
            line_color="black",
            line_width=0.3))
        
        fig_nm.add_trace(go.Scatter(
            x=wavelengths_nm[mask],
            y=photon_flux_per_cm2_per_nm[mask],
            fill='tozeroy',
            mode='none',
            name=f'Used Photons: {used_photon_current_mA_per_cm2:.2f} mA/cm² ({used_photon_number_percent:.2f} %)'))
        
        bandgap_photon_flux = np.interp(bandgap_nm, wavelengths_nm, photon_flux_per_cm2_per_nm)
        fig_nm.add_trace(go.Scatter(x=[bandgap_nm, bandgap_nm], y=[0, bandgap_photon_flux], mode='lines', name=f'Bandgap ({bandgap_nm:.1f} nm)', line_color='red'))
        
        fig_nm.update_layout(
            title='photon flux vs. wavelength',
            xaxis_title='wavelength [nm]',
            yaxis_title='photon flux [cm<sup>-2</sup>·eV<sup>-1</sup>·s<sup>-1</sup>]',        
            legend_font_size=20,
            title_font_size =34,
            yaxis_rangemode = "nonnegative",
            xaxis_tickangle = 0,
            xaxis_ticklabelstep = 3,
            xaxis_range = [250, 4000],
            yaxis_tickformat = "B",
            #yaxis_showexponent = "all",
            yaxis_range = [0, 6e14]
            )
        fig_nm = add_rainbow_to_figure(fig_nm, y_height=6e14, xaxis="nm", opacity=0.1)
        fig_nm.show()
        return Jsc, fig_eV, fig_nm

    return Jsc









#############################################################################################################################
##### Black Body Radiation (Planck's Law) for spectral irradiance and photon flux for photon energy and wavelength respectively

def bb_spectral_irradiance_mW_per_cm2_per_nm(T, wavelengths_nm):
    """
    Calculate the spectral irradiance (in mW/(cm²·nm)) of a black body at a given temperature
    using Planck's law. The spectral irradiance represents the power emitted per unit area 
    per unit wavelength.

    Parameters:
    -----------
    T : float
        The temperature of the black body in Kelvin (K).
    
    wavelengths_nm : numpy.ndarray
        The wavelengths (in nm) at which to calculate the irradiance.

    Returns:
    --------
    spectral_irradiance_mW_per_cm2_per_nm : numpy.ndarray
        The spectral irradiance in mW/(cm²·nm) at the given wavelengths.
    """

    # Convert wavelengths from nm to meters
    wavelengths_m = wavelengths_nm * 1e-9
    # Apply Planck's law for spectral irradiance in W/(m²·m) (W/m²·m)
    spectral_irradiance_W_per_m2_per_m = (2 * h * c**2) / (wavelengths_m**5) * 1 / (np.exp(h * c / (wavelengths_m * k_B * T)) - 1)
    # Convert from W/(m²·m) to W/(m²·nm) (multiply by 1e-9)
    spectral_irradiance_W_per_m2_per_nm = spectral_irradiance_W_per_m2_per_m * 1e-9
    # Convert from W/(m²·nm) to mW/(cm²·nm) (multiply by 0.1 to convert W to mW and by 1e-4 to convert m² to cm²)
    spectral_irradiance_mW_per_cm2_per_nm = spectral_irradiance_W_per_m2_per_nm * 0.1
    
    return spectral_irradiance_mW_per_cm2_per_nm  # Return the spectral irradiance in mW/(cm²·nm)


def bb_spectral_irradiance_mW_per_cm2_per_eV(T, energies_eV):
    """
    Calculate the spectral irradiance (in mW/(cm²·eV)) of a black body at a given temperature
    using Planck's law. The spectral irradiance represents the power emitted per unit area 
    per unit energy.

    Parameters:
    -----------
    T : float
        The temperature of the black body in Kelvin (K).
    
    energies_eV : numpy.ndarray
        The energies (in eV) at which to calculate the irradiance.

    Returns:
    --------
    spectral_irradiance_mW_per_cm2_per_eV : numpy.ndarray
        The spectral irradiance in mW/(cm²·eV) at the given energies.
    """

    # Convert energies from eV to Joules (1 eV = 1.60218e-19 J)
    energies_J = energies_eV * e
    # Apply Planck's law for spectral irradiance in W/(m²·J) (W/m²·J)
    spectral_irradiance_W_per_m2_per_J = (2 * energies_J**3) / (h**3 * c**2) * 1 / (np.exp(energies_J / (k_B * T)) - 1)
    # Convert from W/(m²·J) to W/(m²·eV) (multiply by e, the conversion from J to eV)
    spectral_irradiance_W_per_m2_per_eV = spectral_irradiance_W_per_m2_per_J * e
    # Convert from W/(m²·eV) to mW/(cm²·eV) (multiply by 0.1 to convert W to mW and by 1e-4 to convert m² to cm²)
    spectral_irradiance_mW_per_cm2_per_eV = spectral_irradiance_W_per_m2_per_eV * 0.1
    
    return spectral_irradiance_mW_per_cm2_per_eV  # Return the spectral irradiance in mW/(cm²·eV)


def bb_photon_flux_per_cm2_per_nm(T, wavelengths_nm):
    """
    Calculate the photon flux (in photons/(s·cm²·nm)) of a black body at a given temperature
    using Planck's law. Photon flux represents the number of photons emitted per unit area
    per unit wavelength.

    Parameters:
    -----------
    T : float
        The temperature of the black body in Kelvin (K).
    
    wavelengths_nm : numpy.ndarray
        The wavelengths (in nm) at which to calculate the photon flux.

    Returns:
    --------
    photon_flux_per_cm2_per_nm : numpy.ndarray
        The photon flux in photons/(s·cm²·nm) at the given wavelengths.
    """

    # Convert wavelengths from nm to meters
    wavelengths_m = wavelengths_nm * 1e-9
    # Apply Planck's law for photon flux in photons/(m²·m·s) (photons/m²·m·s)
    photon_flux_per_m2_per_m = (2 * c) / (wavelengths_m**4) * 1 / (np.exp(h * c / (wavelengths_m * k_B * T)) - 1)
    # Convert from photons/(m²·m·s) to photons/(m²·nm·s) (multiply by 1e-9)
    photon_flux_per_m2_per_nm = photon_flux_per_m2_per_m * 1e-9
    # Convert from photons/(m²·nm·s) to photons/(s·cm²·nm) (multiply by 1e-4 to convert m² to cm²)
    photon_flux_per_cm2_per_nm = photon_flux_per_m2_per_nm * 1e-4
    
    return photon_flux_per_cm2_per_nm  # Return the photon flux in photons/(s·cm²·nm)


def bb_photon_flux_per_cm2_per_eV(T, energies_eV):
    """
    Calculate the photon flux (in photons/(s·cm²·eV)) of a black body at a given temperature
    using Planck's law. Photon flux represents the number of photons emitted per unit area
    per unit energy.

    Parameters:
    -----------
    T : float
        The temperature of the black body in Kelvin (K).
    
    energies_eV : numpy.ndarray
        The energies (in eV) at which to calculate the photon flux.

    Returns:
    --------
    photon_flux_per_cm2_per_eV : numpy.ndarray
        The photon flux in photons/(s·cm²·eV) at the given energies.
    """

    # Convert energies from eV to Joules (1 eV = 1.60218e-19 J)
    energies_J = energies_eV * e
    # Apply Planck's law for photon flux in photons/(m²·J·s) (photons/m²·J·s)
    photon_flux_per_m2_per_J = (2 * energies_J**2) / (h**3 * c**2) * 1 / (np.exp(energies_J / (k_B * T)) - 1)
    # Convert from photons/(m²·J·s) to photons/(m²·eV·s) (multiply by e, the conversion from J to eV)
    photon_flux_per_m2_per_eV = photon_flux_per_m2_per_J * e
    # Convert from photons/(m²·eV·s) to photons/(s·cm²·eV) (multiply by 1e-4 to convert m² to cm²)
    photon_flux_per_cm2_per_eV = photon_flux_per_m2_per_eV * 1e-4
    
    return photon_flux_per_cm2_per_eV  # Return the photon flux in photons/(s·cm²·eV)




def calculate_j0(T, bandgap_eV=None, bandgap_nm=None, wavelengths_nm = None, showplots=False, ):
    """
    Calculate the dark saturation current density (J0) using black body photon flux 
    integrated up to the bandgap wavelength.

    Parameters:
    ----------
    T : float
        Temperature of the black body (in Kelvin).    

    bandgap_eV : float, optional
        Bandgap energy in electron volts (eV). Provide either this or `bandgap_nm`, not both.

    bandgap_nm : float, optional
        Bandgap wavelength in nanometers (nm). Provide either this or `bandgap_eV`, not both.

    wavelengths_nm : array-like, optional
        Array of wavelengths in nanometers to use for integration. If None, a default 
        range up to bandgap wavelength + 100 nm is generated.

    showplots : bool, optional
        If True, a plot of the black-body photon spectrum and integration range will be shown.

    Returns:
    -------
    j0 : float
        Dark saturation current density in mA/cm².

    fig_nm : plotly.graph_objects.Figure (optional)
        The interactive plot figure (only if showplots=True).
    """

   # Calculate missing bandgap value from the other
    if bandgap_nm and not bandgap_eV:
        bandgap_eV = h * c / (bandgap_nm*1e-9) / e
    elif bandgap_eV and not bandgap_nm:
        bandgap_nm = h * c / (bandgap_eV * e) *1e9 
    elif (not bandgap_eV and not bandgap_nm) or (bandgap_eV and bandgap_nm):
        print("Please enter either a bandgap_eV or a bandgap_nm")
        return

    # Convert bandgap energy to corresponding wavelength in nm (E = hc/λ)
    #bandgap_nm = h * c / (bandgap_eV * e) * 1e9
    upper_limit = bandgap_nm + 100

    # If no wavelength array is provided, generate one
    if wavelengths_nm is None:
        wavelengths_nm = np.linspace(1, upper_limit, int(upper_limit))

    # Create a mask for all wavelengths ≤ bandgap wavelength (only photons above bandgap contribute)
    mask_nm = wavelengths_nm <= bandgap_nm


    
    # Calculate spectral photon flux (per cm² per nm) using Planck's law
    # Multiply by π to account for hemispherical emission
    photon_flux_per_cm2_per_nm = bb_photon_flux_per_cm2_per_nm(T, wavelengths_nm) * np.pi

    # Integrate photon flux up to the bandgap wavelength
    flux_above_Eg_nm = np.trapezoid(photon_flux_per_cm2_per_nm[mask_nm], wavelengths_nm[mask_nm])

    # Calculate J0 in mA/cm² using elementary charge and conversion
    j0 = flux_above_Eg_nm * e * 1000 #/ .EQE_EL  # in mA/cm²
    

    # Kumulierte Integration des Flusses
    #flux_above_Eg_nm = cumulative_trapezoid(photon_flux_per_cm2_per_nm[mask_nm], wavelengths_nm[mask_nm])
    
    
    print(f"Black Body Radiation at {T} K leads to j0 = {j0} mA/cm²")

    if showplots:
        # Identify the peak in the photon flux spectrum
        peak_index = np.argmax(photon_flux_per_cm2_per_nm)
        peak_x = wavelengths_nm[peak_index]
        peak_y = photon_flux_per_cm2_per_nm[peak_index]

        # Plot the black-body photon flux spectrum
        fig_nm = go.Figure()

        fig_nm.add_trace(go.Scatter(
            x=wavelengths_nm,
            y=photon_flux_per_cm2_per_nm,
            mode='lines',
            name=f'Black-body spectrum at {T} K'))

        fig_nm.update_layout(
            title='Black-Body Spectrum',
            title_font_size=30,
            xaxis_title='Wavelength [nm]',
            yaxis_title='Photon Flux [photons/cm²/nm]',
            xaxis_rangemode="nonnegative",
            yaxis_rangemode="nonnegative",
            yaxis_type='log',
            yaxis_dtick = 50,
            yaxis_tickmode = "linear",
            xaxis_ticklabelstep = 4
        )

        # Shade integration area
        fig_nm.add_trace(go.Scatter(
            x=wavelengths_nm[mask_nm],
            y=photon_flux_per_cm2_per_nm[mask_nm],
            mode='none',
            fill='tozeroy',
            name='Integration'))

        # Mark the bandgap position
        fig_nm.add_trace(go.Scatter(
            x=[bandgap_nm, bandgap_nm],
            y=[0, peak_y],
            mode='lines',
            name='Bandgap',
            line_color='black',
            showlegend=True))

        # fig_nm.add_annotation(
        #     x=bandgap_nm - 10,
        #     y=peak_y-10^100,
        #     text="Bandgap",
        #     showarrow=True,
        #     arrowhead=2,
        #     arrowcolor="black",
        #     ax=-40,
        #     ay=60,
        #     font=dict(size=20, color="black"),
        #     align="center",
        # )

        fig_nm.show()

        return j0, fig_nm

    return j0




def calculate_voc(Jsc, J0, n=1, T=300):
    """
    Calculate the open-circuit voltage (Voc) of a solar cell using the diode equation.

    Parameters:
    ----------
    Jsc : float
        Short-circuit current density (in A/cm²).
    J0 : float
        Dark saturation current density (in A/cm²).
    n : float, optional
        Ideality factor (typically 1 ≤ n ≤ 2). Default is 1.
    T : float, optional
        Temperature in Kelvin. Default is 300 K.

    Returns:
    -------
    Voc : float
        Open-circuit voltage in volts (V).
    """
    # Calculate Voc using the Shockley diode equation
    Voc = (n * k_B * T / e) * np.log((Jsc / J0) + 1)

    return Voc



def simulate_jv_curve(Jsc, J0, n=1, T=300, showplots=False, incident_irradiance = 100):
    """
    Simulate the JV (current-voltage) curve of a solar cell using the Shockley diode equation.

    Parameters:
    ----------
    Jsc : float
        Short-circuit current density in A/cm².
    J0 : float
        Dark saturation current density in A/cm².
    n : float, optional
        Ideality factor (typically 1 ≤ n ≤ 2). Default is 1.
    T : float, optional
        Temperature in Kelvin. Default is 300 K.
    showplots : bool, optional
        If True, a plot of the JV curve, power curve, and MPP is shown.

    Returns:
    -------
    J : np.ndarray
        Simulated current density (A/cm²) as a function of voltage.
    V : np.ndarray
        Voltage values (V).
    fig : plotly.graph_objects.Figure (optional)
        The interactive plot figure (only if showplots=True).
    """

    # Calculate open-circuit voltage Voc
    Voc = calculate_voc(Jsc, J0, T=T)

    # Simulate voltage array from 0 to Voc + small buffer
    V = np.linspace(0, Voc + 0.01, 500)

    # Calculate current density using the diode equation
    J = Jsc - J0 * (np.exp((e * V) / (n * k_B * T)) - 1)

    # Calculate power and find Maximum Power Point (MPP)
    P = V * J
    mpp_index = np.argmax(P)
    V_mpp = V[mpp_index]
    J_mpp = J[mpp_index]
    P_mpp = P[mpp_index]

    # Calculate Fill Factor (FF)
    FF = (V_mpp * J_mpp) / (Voc * Jsc)

    # Calculate Power Conversion Efficiency (PCE)
    PCE = (P_mpp / incident_irradiance) * 100  # in percent

    if showplots:
        # Plot with Plotly
        fig = go.Figure()

        # JV curve
        fig.add_trace(go.Scatter(x=V, y=J, mode='lines', name='Current Density J [mA/cm²]'))

        # Power curve
        fig.add_trace(go.Scatter(x=V, y=P, mode='lines', name='Power Density P [mW/cm²]', yaxis='y2'))

        # Highlight MPP
        fig.add_trace(go.Scatter(
            x=[V_mpp], y=[J_mpp],
            mode='markers',
            name='MPP',
            marker=dict(symbol="star", color='red', size=10)
        ))

        # Layout and axes
        fig.update_layout(
            title="Simulated JV-Curve with Maximum Power Point (MPP)",
            xaxis_title="Voltage [V]",
            yaxis_title="Current Density [mA/cm²]",
            xaxis_range=[0, Voc + 0.05],
            yaxis_range= [0, 75],
            showlegend=True,
            title_font_size = 34,
            yaxis2=dict(
                title="Power Density [mW/cm²]",
                overlaying='y',
                side='right',
                range= [0, 75]
            ),
            legend_font_size = 20
        )

        # Annotate FF and PCE
        fig.add_annotation(
            xref ="paper",
            yref="paper",
            x=0.05,
            y=0.95,
            text=f"PCE = {PCE:.2f} %<br>Jsc = {Jsc:.2f} mA/cm² <br>V<sub>oc</sub> {Voc:.3f} V <br>FF = {FF:.2f} <br>",
            showarrow=False,
            font=dict(size=20),
            align="left"
        )

        # Draw rectangle from origin to MPP
        fig.add_shape(
            type="rect",
            x0=0, y0=0,
            x1=V_mpp, y1=J_mpp,
            line=dict(color="grey", width=1),
            fillcolor="rgba(150, 150, 255, 0.5)",
        )

        fig.show()

        return J, V, fig
    
    return J, V





def calculate_fom(Jsc, J0, n=1, T=300, incident_irradiance=100):
    """
    Calculate Maximum Power Point (MPP) and key solar cell parameters (Figure of merit) from Jsc and J0 parameters.

    Parameters:
    ----------
    Jsc : float
        Short-circuit current density in mA/cm².
    J0 : float
        Dark saturation current density in mA/cm².
    n : float, optional
        Ideality factor of the diode (default: 1).
    T : float, optional
        Temperature in Kelvin (default: 300 K).
    incident_irradiance : float, optional
        Incident power in mW/cm² (default: 100 mW/cm²).

    Returns:
    -------
    fom_dict : dict
        Dictionary with figures of merit (PCE, FF, MPP, Jsc, Voc, J0).
    """

    # Simulate JV curve
    J, V = simulate_jv_curve(Jsc, J0, n=n, T=T, incident_irradiance=incident_irradiance)

    # Calculate power at each voltage point
    P = V * J  # Power in mW/cm² (assuming J is in mA/cm² and V in V)

    # Find index of Maximum Power Point (MPP)
    mpp_index = np.argmax(P)
    V_mpp = V[mpp_index]
    J_mpp = J[mpp_index]
    P_mpp = P[mpp_index]

    # Calculate Voc
    Voc = calculate_voc(Jsc, J0, n=n, T=T)

    # Calculate Fill Factor
    FF = (V_mpp * J_mpp) / (Voc * Jsc)

    # Calculate Power Conversion Efficiency (PCE)
    PCE = (P_mpp / incident_irradiance) * 100 # in %

    # Collect figures of merit
    fom_dict = {
        "PCE [%]": PCE,
        "FF [1]": FF,
        "P_mpp [mW/cm2]": P_mpp,
        "V_mpp [V]": V_mpp,
        "J_mpp [mA/cm2]": J_mpp,
        "Jsc [mA/cm2]": Jsc,
        "Voc [V]": Voc,
        "J0 [mA/cm2]": J0,
    }

    print(f"Open-Circuit Voltage: {Voc:.3f} V²")
    print(f"Maximum Power Density at the MPP: {P_mpp:.3f} mW/cm²")
    print(f"Fill Factor (FF): {FF:.3f}")
    print(f"Power Conversion Efficiency (PCE): {PCE:.2f} %")

    return fom_dict

def calculate_fom_from_jv_curve(J, V, n=1, T=300, incident_irradiance=100):
    """
    Calculate Maximum Power Point (MPP) and key solar cell parameters (Figure of Merrits) from a given JV curve.

    Parameters:
    ----------
    J : np.ndarray
        Current density values in mA/cm² (must be positive for power calculation).
    V : np.ndarray
        Corresponding voltage values in V.
    n : float, optional
        Ideality factor of the diode (default: 1).
    T : float, optional
        Temperature in Kelvin (default: 300 K).
    incident_irradiance : float, optional
        Incident power in mW/cm² (default: 100 mW/cm²).

    Returns:
    -------
    fom_dict : dict
        Dictionary with figures of merit (PCE, FF, MPP, Jsc, Voc, J0).
    """

    # Calculate power at each voltage point
    P = V * J  # Power in mW/cm² (assuming J is in mA/cm² and V in V)

    # Find index of Maximum Power Point (MPP)
    mpp_index = np.argmax(P)
    V_mpp = V[mpp_index]
    J_mpp = J[mpp_index]
    P_mpp = P[mpp_index]

    from scipy.interpolate import interp1d

    # Interpolate Voc if not provided (J → V at J=0)
    try:
        interp_VJ = interp1d(J, V, kind='linear', fill_value='extrapolate')
        Voc = float(interp_VJ(0))
        print(f"Determined Voc via interpolation: {Voc:.3f} V")
    except Exception as excep:
        print(f"Could not interpolate Voc: {excep}")
        Voc = np.nan

    # Interpolate Jsc if not provided (V → J at V=0)
    try:
        interp_JV = interp1d(V, J, kind='linear', fill_value='extrapolate')
        Jsc = float(interp_JV(0))
        print(f"Determined Jsc via interpolation: {Jsc:.3f} mA/cm²")
    except Exception as excep:
        print(f"Could not interpolate Jsc: {excep}")
        Jsc = np.nan

    # Estimate J0 if not provided
    try:
        J0 = Jsc / (np.exp((e * Voc) / (n * k_B * T)) - 1)
        print(f"Estimated J0 using diode equation: {J0:.3e} mA/cm²")
    except Exception as excep:
        print(f"Could not calculate J0: {excep}")
        J0 = np.nan

    # Calculate Fill Factor
    FF = (V_mpp * J_mpp) / (Voc * Jsc)

    # Calculate Power Conversion Efficiency (PCE)
    PCE = (P_mpp / incident_irradiance) * 100 # in %

    # Collect figures of merit
    fom_dict = {
        "PCE [%]": PCE,
        "FF [1]": FF,
        "P_mpp [mW/cm2]": P_mpp,
        "V_mpp [V]": V_mpp,
        "J_mpp [mA/cm2]": J_mpp,
        "Jsc [mA/cm2]": Jsc,
        "Voc [V]": Voc,
        "J0 [mA/cm2]": J0,
    }

    print(f"Maximum Power Density at the MPP: {P_mpp:.3f} mW/cm²")
    print(f"Fill Factor (FF): {FF:.3f}")
    print(f"Power Conversion Efficiency (PCE): {PCE:.2f} %")

    return fom_dict