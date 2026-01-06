
from datetime import datetime

import plotly.graph_objects as go  # for go.Scatter Plot
import plotly.io as pio

from .update_layout import update_layout_umr

################## SIMPLE JV CURVE PLOT (Forward and Reverse) ##################

def plot_jv(jv_curves = None, full_jv_data = None, names='scan', grid=False, toggle_grid_button=False, fig=None, rangemode='normal', table=False, toggle_table_button=False, toggle_scan_buttons= False, linemode='lines+markers', showplot=True, scan_direction='both'):
    """
    Plots current density-voltage (J-V) curves for photovoltaic cells using Plotly.
    If you want to plot forward and reverse curves, make sure that the reverse curve is the first curve in the list and the reverse curve the second one.

    Parameters:
    - jv_curves (list of , optional): List of dictionaries representing J-V curves.
        Each dictionary should have the keys:
        - 'voltage': List of voltage values for the J-V curve.
        - 'current_density': List of corresponding current density values.
        - 'scan': String representing the name of the scan (Forward or Reverse).
    - full_jv_data (list of dict, optional): List of dictionaries containing full JV data from NOMAD Oasis. (for trace metadata)
    - names (list or string): List of names of data (cell names) or string value. if not given Reverse and Forward are used
    - grid (bool, optional): Flag to control the visibility of the grid in the plot.
        Default is False.
    - toggle_grid_button (bool, optional): Flag to control the visibility of the Toggle Grid Button in the plot.
        Default is False.
    - fig (plotly.graph_objects.Figure, optional): Existing Plotly figure to which
        the JV curves will be added. If None, a new figure will be created.
    - rangemode (str, optional): Range mode for the axes. Options: 'normal', 'tozero' (range extends to 0), 'nonnegative' (range is non-negative -> 1st quadrant only).
        Default is 'normal'.
    - table (bool, optional): Flag to control the visibility of the JV parameters table in the plot.
        Default is False.
    - toggle_table_button (bool, optional): Flag to control the visibility of the Toggle Table Button in the plot.
        Default is False.
    - showplot (bool): If True, the plot will be displayed. Defaults to True.
    - linemode (str, optional): Mode to display the lines in the scatter plot. Default is 'lines+markers'.
        Possible values are 'lines', 'markers', 'lines+markers', etc.
    - scan_direction (str, optional): Flag to control which scan directions are plottet. Either use 'both', 'Forward' or 'Reverse'. Default is 'both'.

    Returns:
    - fig (plotly.graph_objects.Figure): Plotly figure object.

    """
   
    # Generate jv_curves list from full_jv_data and create correspondning metadata list
    if full_jv_data:
        jv_curves = []
        metadata = []
        for jv_data in full_jv_data:
            for jv_curve in jv_data['jv_curve']:
                if scan_direction == jv_curve['scan'] or scan_direction == 'both':
                    jv_curves.append(jv_curve)
                    metadata.append(dict(
                        datetime = datetime.fromisoformat(jv_data["datetime"]),
                        device = jv_data["device"],
                        scan = jv_curve['scan'],
                        scan_order = jv_data['scan_order'],
                    ))

    else:
        metadata = []*len(jv_curves)


    # Create a Plotly figure
    if not fig:
        fig = go.Figure()

    try:

        # Define names of curves if not given
        list_names=[]

        if isinstance(names, list):
            list_names = names

        elif names == 'scan':
            for curve in jv_curves:
                list_names.append(curve["scan"]),          # name of curve in legend
        elif names == 'lab_id':
            if not full_jv_data:
                print("Please give full_jv_data to display lab_id as name")
                return
            for i, curve in enumerate(jv_curves):
                list_names.append(metadata[i]["device"]),   
        elif names == 'lab_id+scan':
            if not full_jv_data:
                print("Please give full_jv_data to display lab_id as name")
                return
            for i, curve in enumerate(jv_curves):
                list_names.append(f'{metadata[i]["device"]} {curve["scan"]}')  

        # Add traces for each I-V curve
        for i, curve in enumerate(jv_curves):
            fig.add_scatter(
                x=curve["voltage"],          # x-values
                y=curve["current_density"],  # y-values
                name=list_names[i],          # name of curve in legend
                mode=linemode,
                meta = metadata[i],
                hovertext=metadata[i]["device"],
            )
            
    except KeyError as e:
        # Falls der Schlüssel nicht gefunden wird
        print(f"There is a Key ERROR: {e} -  Most probably you want to enter data in full_jv_data")
        return

    # Definition of standard axis layout
    fig.update_layout(
        xaxis_title='Voltage [V]',
        yaxis_title='Current Density [mA/cm²]',
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
        yaxis_range = [-5, 25],
    )

    # If you use toggle_table button, also toggle_grid_button will be displayed, to create first updatemenu
    if toggle_table_button:
        toggle_grid_button=True

    # Creates grid button
    if toggle_grid_button:
        fig.update_layout(updatemenus=pio.templates['UMR'].layout.updatemenus)  # toggle button for grid


    # Toggle table button
    if toggle_table_button:
        # Show Table
        table = True

        new_button = dict(
            label = 'Toggle Table',
            method = 'restyle',
            args=[{'columnwidth': [0, 0, 0]}],  # Initialzustand, alles sichtbar
            args2=[{'columnwidth': [2, 1, 1]}]  # Toggle-Zustand für die Tabelle DOES NOT FULLY WORK
        )

        # Get current updatemenus list
        current_updatemenus = fig.layout.updatemenus
        # Append new Button to existing updatemenus
        current_updatemenus[0].buttons = list(current_updatemenus[0].buttons) + [new_button]


    # Add Buttons to switch between forward and reverse scan
    if toggle_scan_buttons:
        for scan in ["Forward", "Reverse"]:
            new_button = dict(
                label=scan,
                method="update",
                args=[{'visible': [True if trace.meta['scan'] == scan else False for trace in fig.data]}]
            )
            
            # Check if updatemenus exists and is not empty
            if fig.layout.updatemenus and len(fig.layout.updatemenus) > 0:
                # Get current updatemenus list
                current_updatemenus = fig.layout.updatemenus
                current_updatemenus[0].buttons = list(current_updatemenus[0].buttons) + [new_button]
            else:
                # Initialize updatemenus if it doesn't exist
                fig.update_layout(updatemenus=[{
                    'buttons': [new_button]
                }])

    # Add JV parameters table if required
    if table:   
        # Definition of colors
        colors = pio.templates['UMR'].layout.colorway  # use colors from umr-Ttemplate
        rowEvenColor = 'white'
        rowOddColor = 'rgb(229,229,229)'

        # Round parameters
        curves = jv_curves
        for curve in curves:
            curve['fill_factor'] = f"{round(float(curve['fill_factor']), 2):.2f}"  # Always show two decimal numbers
            curve['open_circuit_voltage'] = round(float(curve['open_circuit_voltage']*1000))
            curve['short_circuit_current_density'] = round(float(curve['short_circuit_current_density']), 1)

        
        fig.add_table(
            header=dict(values=['', '<b>RV</b>', '<b>FW</b>'], font=dict(size=28, color=['black', colors[0], colors[1]])), # former font size 18
            cells=dict(values=[
                ['<b>V<sub>oc</sub></b> [mV]', '<b>J<sub>sc</sub></b> [mA/cm²]', '<b>FF</b> [%]', '<b>PCE</b> [%]'],
                [f"{curves[0][param]}" for param in ['open_circuit_voltage', 'short_circuit_current_density', 'fill_factor', 'efficiency']], 
                [f"{curves[1][param]}" for param in ['open_circuit_voltage', 'short_circuit_current_density', 'fill_factor', 'efficiency']],
            ],
                font=dict(size=28, color=['black', colors[0], colors[1]]), # former font size 18
                fill_color = [[rowOddColor,rowEvenColor,rowOddColor, rowEvenColor,rowOddColor, rowEvenColor]*5]),
            domain={'x': [0.05, 0.55], 'y': [0.05, 0.55]},  # Adjust domain to move table to left bottom # former x=[0.05, 0.5], y=[0.1, 0.5]
            columnwidth=[2.5, 1, 1],  # Adjust column width formeer 1.8, 1, 1
        )

    
    # Correct layout
    update_layout_umr(fig)

    if showplot:
        fig.show()
        
    return fig     # Return the Plotly figure object for further customization