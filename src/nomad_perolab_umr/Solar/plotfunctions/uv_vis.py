# ## Tauc Plot from UV-vis measurement

# Lea Obermüller
# 04.03.2024

# The Tauc method is based on the assumption that the energy-dependent absorption coefficient α can be expressed by the following equation:
# 
# $(αhν)^{1/\gamma} = B(hν - E_g)$
# 
# where h is the Planck constant,ν is the photon’s frequency,Eg is the band gap energy, and B is a constant. The γ factor depends on the nature of the electron transition and is equal to 1/2 or 2 for the direct and indirect transition band gaps. 
# 
# The region showing a steep, linear increase of light absorption with increasing energy is characteristic of semiconductor materials. The x-axis intersection point of the linear fit of the Tauc plot gives an estimate of the band gap energy.
#
# https://doi.org/10.1021/acs.jpclett.8b02892
# 

# how to use 

"""

names = ["Stack up to perovskite", "Perovskite on glass"]
file_path = []
file_path.append(r'/Volumes/Solar/5_ScientificResults/01_Batches/UMR_002_LO/02_RawData/04_UV-Vis/Transmission/UMR_002_00021.Sample.Raw.csv')
file_path.append(r'/Volumes/Solar/5_ScientificResults/01_Batches/UMR_002_LO/02_RawData/04_UV-Vis/Transmission/UMR_002_Perov_on_Glass.Sample.Raw.csv')


fig_Ab, fig_tauc, E_G = tauc_plot(file_path, names, bandgap = "direct", grid=True, toggle_grid_button = True)

"""


# Import

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from scipy.constants import c, e, h
from scipy.stats import linregress

################## LOAD STANDARD PLOT FUNCTIONS ##################
#import Solar.plottemplate # UMR Template is automatically set as default
from ..plottemplate.umr_plot_template import colors, markers
from ..plottemplate.umr_plot_template import linepattern as pattern
from . import update_layout_umr


def tauc_plot(file_path_T, file_path_R, names, bandgap, grid=False, toggle_grid_button=False, rangemode='normal'):
    """
    Creates a tauc plot from 
    a transmission spectrum recorded with uv-vis spectrometer

    Parameters:
    - file_path (list): List of file paths to transmission spectra data. 
    File must include transmittance (in %) and wavelength (in nm). 
    - names (list): substrate names
    - bandgap: direct or indirect
    - grid (True or False): show grid or not
    - toggle_grid_button (Ture or False): show toggle grid button or not 

    Returns: 
    - fig (plotly.graph_objects.Figure): Plotly figure object.
    - E_G: bandgap energy 
    """
    
    gamma = None
    while gamma is None:
        if bandgap.lower() == "direct":
            gamma = 1/2
            title = '(Energy x Absorbance)² [a.u.]'
        elif bandgap.lower() == "indirect":
            gamma = 2
            title = '√(Energy x Absorbance) [a.u.]'
        else: 
            print(f"ERROR: Value specified for bandgap <{bandgap}> is not valid.") 
            bandgap = input("Please specify if the bandgap is <direct> or <indirect>: ")
    
    E_G = []
    
    "---- Initialyze Plots ----"

    # Create a Plotly figure for absorptance
    fig_A = go.Figure()
    
    # Create a Plotly figure for absorbance
    fig_Ab = go.Figure()

    # Create a Plotly figure for tauc plot
    fig_tauc = go.Figure()
    
    # Reflectance plot
    fig_R = go.Figure()
    
    # Transmittance plot
    fig_T = go.Figure()
    
    
    "-------------------Calculate relevant data-----------------------------"
    i = 0
    data = {}
    
    for path_T, path_R in zip(file_path_T, file_path_R):
        
        # read file into pandas dataframe 
        data_T = pd.read_csv(path_T) # transmittance
        data_R = pd.read_csv(path_R) # reflectance

        # create new data frame with absorptance A = 100-T-R
        data_A = pd.DataFrame({'nm': data_T['nm'], "%A": 100-data_T[" %T"]-data_R[" %R"]})
        data_A = data_A.loc[(data_A[data_A['nm']>=850].index.max()):] # remove all data for wavelength above 850nm (probleme with uv vis)
        

        # emty dataframe for corrected data 
        data_corr = pd.DataFrame(columns = ["Energy", "Wavelength", "Absorbance", "Absorptance", "Reflectance", "Transmittance", "Tauc Data"])
       
        # caclulate absorbance and absorptance
        data_corr["Absorptance"] = (data_A["%A"])/100
        data_corr["Absorbance"] = -np.log(data_T[" %T"]/100)
        
        data_corr["Wavelength"] = data_A["nm"]
        data_corr["Reflectance"] = data_R[" %R"]/100
        data_corr["Transmittance"] = data_T[" %T"]/100

        # convert wavelength to energy 
        data_corr["Energy"] = c*h/(data_A["nm"]*e)*10**9

        # calculate tauc data 
        data_corr["Tauc Data"] =(data_corr["Absorbance"] * data_corr["Energy"])**(1/gamma)# (np.log(1-data_corr["Absorptance"]) * data_corr["Energy"])**(1/gamma)

        data[names[i]] = data_corr # save corrected data to a dictionary for later use 
        i = i+1
    
    
    "------------ Plot Absorptance, Reflectance and Transmittance ----------------"
    
    for dev, d in data.items():
        
        # plot absorptance 
        fig_A.add_scatter(x=d["Wavelength"][::10], y=d["Absorptance"][::10]*100, name = f"{dev} A")
        fig_A.add_scatter(x=d["Wavelength"][::10], y=d["Reflectance"][::10]*100, name = f"{dev} R")

        
         # plot absorptance 
        fig_Ab.add_scatter(x=d["Wavelength"], y=d["Absorbance"], name = dev)
        

        # plot reflectance
        fig_R.add_scatter(x=d["Wavelength"], y=d["Reflectance"]*100, name = dev)
        
        # plot transmittance 
        fig_T.add_scatter(x=d["Wavelength"], y=d["Transmittance"]*100, name = dev)
        
        # plot all on one plot for each device
        fig_C = go.Figure()
        fig_C.add_scatter(x=d["Wavelength"], y=d["Absorptance"]*100, name = 'Absorptance', mode = 'lines', line=dict(width=3, dash='dash'))
        fig_C.add_scatter(x=d["Wavelength"], y=d["Reflectance"]*100, name = 'Reflectance', mode = 'lines', line=dict(width=3, dash='dot'))
        fig_C.add_scatter(x=d["Wavelength"], y=d["Transmittance"]*100, name = 'Transmittance', mode = 'lines', line=dict(width=3))

        fig_C.update_layout(
            title = dev,
            yaxis_title = '[%]',
            xaxis_title = 'Wavelength [nm]',
            xaxis_dtick=0.1,
            yaxis_dtick=2.5,
            # Show/hide grid based on the 'grid' parameter
            xaxis_showgrid=grid,
            xaxis_minor_showgrid=grid, 
            yaxis_showgrid=grid,
            yaxis_minor_showgrid=grid, 
            # show only positive range if rangemode is "nonnegative"
            xaxis_rangemode=rangemode, 
            yaxis_rangemode=rangemode,
            yaxis_zeroline = False,
            yaxis_range = [-10,100], 
        )

        if toggle_grid_button:
            fig_C.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid

        update_layout_umr(fig_C)
        fig_C.show()
        # fig_C.write_image(f"UVvis_{dev}.png", scale = 2)
        
    # update plot settings
    
    fig_A.update_layout(
        xaxis_title = 'Wavelength [nm]',
        yaxis_title = '[%]',
        xaxis_dtick=0.1,
        yaxis_dtick=2.5,
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
        # show only positive range if rangemode is "nonnegative"
        xaxis_rangemode=rangemode, 
        yaxis_rangemode=rangemode,
        #legend_y = 0.2,
        #legend_x = 0.55,
        yaxis_zeroline = False,
        yaxis_range = [0,100],
        yaxis_title_font = dict(size = 33),
        xaxis_title_font = dict(size = 33),
    )

    if toggle_grid_button:
        fig_A.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid

    update_layout_umr(fig_A)
    fig_A.show()
    # fig_A.write_image("Absorptance.png", scale = 2)
    
    fig_Ab.update_layout(
        xaxis_title = 'Wavelength [nm]',
        yaxis_title = 'Absorbance',
        #xaxis_dtick=0.1,
        #yaxis_dtick=2.5,
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
        # show only positive range if rangemode is "nonnegative"
        xaxis_rangemode=rangemode, 
        yaxis_rangemode=rangemode,
        yaxis_title_font = dict(size = 33),
        xaxis_title_font = dict(size = 33),
        #legend = dict(
         #   y = 0.2,
         #   x = 0.55),
        #yaxis_zeroline = False,
        #yaxis_range = [0,1]
    )

    if toggle_grid_button:
        fig_Ab.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid

    update_layout_umr(fig_Ab)
    fig_Ab.show()
    # fig_Ab.write_image("Absorbance.png", scale = 2)
    
    fig_R.update_layout(
        xaxis_title = 'Wavelength [nm]',
        yaxis_title = 'Reflectance [%]',
        xaxis_dtick=0.1,
        yaxis_dtick=2.5,
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
        # show only positive range if rangemode is "nonnegative"
        xaxis_rangemode=rangemode, 
        yaxis_rangemode=rangemode,
        yaxis_title_font = dict(size = 33),
        xaxis_title_font = dict(size = 33),
        yaxis_zeroline = False,
        #legend = dict(
        #    y = 0.2,
        #    x = 0.55),
        uirevision = 'true', 
        yaxis_range = [0,100]
    )

    if toggle_grid_button:
        fig_R.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid

    update_layout_umr(fig_R)
    pio.show(fig_R)
    # fig_R.write_image("Reflectance.png", scale = 2)
    
    fig_T.update_layout(
        xaxis_title = 'Wavelength [nm]',
        yaxis_title = 'Transmittance [%]',
        xaxis_dtick=0.1,
        yaxis_dtick=2.5,
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
        # show only positive range if rangemode is "nonnegative"
        xaxis_rangemode=rangemode, 
        yaxis_rangemode=rangemode,
        yaxis_title_font = dict(size = 33),
        xaxis_title_font = dict(size = 33),
        yaxis_zeroline = False,
        #legend = dict(
         #   y = 0.99,
          #  x = 0.55),
        yaxis_range = [-10,100]
    )

    if toggle_grid_button:
        fig_T.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid

    update_layout_umr(fig_T)
    fig_T.show()
    # fig_T.write_image("Transmittance.png", scale = 2)
    
    "---------------- Plot Tauc ------------------"
    i = 0 # for line pattern 
    
    for (dev, col, m) in zip(data, colors, markers):
        
        d = data[dev] 
        
        # tauc plot
        fig_tauc.add_scatter(x=d["Energy"], y=d["Tauc Data"], name = dev, mode = "lines+markers", line_color = colors[col], marker = dict(symbol = m))
        #fig_tauc.update_layout(xaxis_range = [1.4, 1.8], yaxis_range = [-1, 10])
        fig_tauc.show()
        
        # linear part
        
        print(f"Cell <{dev}>")
        min_E = float(input("Please enter the minimum energy for the linear fit (in eV): "))
        max_E = float(input("Please enter the maximum energy for the linear fit (in eV): "))
        mask1 = (d["Energy"] >= min_E) & (d["Energy"] <= max_E)

        # Perform linear regression on the filtered data
        slope1, intercept1, _, _, _ = linregress(d["Energy"][mask1], d["Tauc Data"][mask1])
        x_intercept1 = -intercept1 / slope1
        
        print(slope1, intercept1)

        energy_range1 = np.linspace(min(d["Energy"][mask1].min(), 
                                    x_intercept1), 
                                    max(d["Energy"][mask1].max(), 
                                    x_intercept1), 100)

        # Calculate the linear fit lines for the specified range
        fit_line1 = slope1 * energy_range1 + intercept1

        # plot linear fit lines
        fig_tauc.add_scatter(x=energy_range1, 
                             y=fit_line1, 
                             mode = "lines", 
                             name = 'Linear Fit', 
                             showlegend = False, 
                             line_color = colors['black'], 
                             line_dash = pattern[i])
        fig_tauc.add_scatter(
                                x=[x_intercept1],
                                y=[0],
                                mode='markers+text',  # Damit der Text angezeigt wird
                                name='X-Intercept',
                                text=[f"{x_intercept1:.2f}"],  # Formatierung auf 2 Nachkommastellen
                                textposition='bottom right',
                                textfont=dict(size=30),
                                marker_color=colors['black'],
                                marker=dict(symbol='circle', size=10),
                                showlegend=False
)


        E_G.append(x_intercept1) # save band gap energy 
        i = i+1

        
        
    # set tauc plot settings 

    fig_tauc.update_layout(
        xaxis_title = 'Energy [eV]',
        yaxis_title = title,
        xaxis_dtick=0.05,
        yaxis_dtick=2.5,
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
        # show only positive range if rangemode is "nonnegative"
        xaxis_rangemode=rangemode, 
        yaxis_rangemode=rangemode,
        #legend_x = 0.5,
        yaxis = dict(tickmode = 'array', tickvals = [0], ticktext = ['0']),
        yaxis_title_font = dict(size = 30),
        xaxis_title_font = dict(size = 30),
        xaxis_tickfont = dict(size = 30),
        showlegend = False
    )
    
    if toggle_grid_button:
        fig_tauc.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid

    # Correct layout
    update_layout_umr(fig_tauc)
    fig_tauc.show()
    
    # fig_tauc.write_image(f"Tauc_{dev}.png", scale = 2)
    
    
    "-------- Print and save band gap energy ------------"
    for E, name in zip(E_G, names):
        print(f"Band gap energy of cell <{name}> is {E} eV")


    return(fig_A, fig_tauc, E_G)





    
    
    
    
    

