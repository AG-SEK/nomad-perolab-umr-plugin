"""
In this script we collect functions which are used to create the JV Parameter Boxplots
"""

import pandas as pd
import plotly.graph_objects as go

from ..nomadapifunctions import get_jv_measurements_by_device_list
from ..plottemplate.umr_plot_template import colors
from .helper_functions import get_samples_from_group
from .update_layout import update_layout_umr

# List with JV parameters (as named in NOMAD Oasis)
list_of_parameters = [
        'efficiency',
        'open_circuit_voltage',
        'short_circuit_current_density',
        'fill_factor',
        'power_density_at_maximum_power_point',
        'potential_at_maximum_power_point',
        'current_density_at_maximum_power_point', 
        'series_resistance_ohm',
        'shunt_resistance_ohm',
    ]


def create_boxplot_data(jv_data, batch, list_of_parameters=list_of_parameters, excel_filename="boxplot_data.xlsx", scan_direction=None, fig=None):
    """
    Create a tabular DataFrame for boxplot data from JV measurements.

    Parameters:
    - jv_data (list): List of JV measurement dictionaries, each containing 'device' and 'jv_curve'.
    - batch (dict): Batch information containing groups and associated lab IDs.
    - list_of_parameters (list): List of parameter names to extract from each JV curve (default: None).
    - excel_filename (str): Name of the Excel file if saving is enabled (default: "boxplot_data.xlsx").
    - scan_direction_filter (str or None): Filter für die Scanrichtung (z.B. 'Forward' oder 'Reverse'). Wenn None, werden alle Scanrichtungen berücksichtigt (default: None).
    - fig (plotly.graph_objects.Figure, optional): Existing Plotly figure to which the Boxplot data will be added. If None, a new figure will be created.

    Returns:
    - pd.DataFrame: A DataFrame containing the tabular boxplot data.
    """
    
     # Create a Plotly figure
    if not fig:
        fig = go.Figure()
    
    if list_of_parameters is None:
        list_of_parameters = []  # Default to empty list if no parameters provided

    # Create a mapping from lab_id to group information for efficient lookup
    lab_id_to_group = {}
    for group in batch.get('groups', []):  # Safeguard against missing 'groups' key
        samples = get_samples_from_group(group=group)
        for lab_id in samples:
            lab_id_to_group[lab_id] = {
                'group_number': group['group_number'],
                'group_description': group['group_description']
            }

    # List to store the tabular data
    table_data = []

    # Iterate over each measurement
    for measurement in jv_data:
        lab_id = measurement['device']
        
        # Get the group information for this lab_id
        group_info = lab_id_to_group[lab_id]
        if not group_info:
            continue  # Skip if the lab_id is not in any group

        # Iterate over both curves (e.g., Forward and Reverse)
        for curve in measurement['jv_curve']:
            scan_dir = curve['scan']

            # If scan_direction filter is used
            if scan_direction and scan_dir != scan_direction:
                continue

            # Initialize a row with common information
            row = {
                'lab_id': lab_id,
                'group_number': group_info['group_number'],
                'group_description': group_info['group_description'],
                'scan_direction': scan_dir,
                'measurement_name': measurement['name']
            }

            # Add the parameters to the row
            for param_name in list_of_parameters:
                row[param_name] = curve.get(param_name, None)  # Default to None if parameter not in curve

            # Append the row to the table data
            table_data.append(row)

    # Convert the list of dictionaries to a DataFrame
    boxplot_df = pd.DataFrame(table_data)

    # Save to Excel if the flag is set
    if excel_filename:
        boxplot_df.to_excel(excel_filename, index=False)

    return boxplot_df




def plot_boxplot_jv(boxplot_df, parameter="efficiency", scan_direction="Reverse", trace_colors=None, xaxis_title=None, group_descriptions=None, fig=None, showplot=True, show_group_names=True, group_order=None):
    """
    Creates a customized boxplot using Plotly's graph objects with multiple customization options for various parameters.

    Args:
        boxplot_df (pd.DataFrame): The DataFrame containing data to be plotted. Should include 'group_number', 'scan_direction', and 'lab_id'.
        parameter (str): The parameter to plot on the y-axis. Available options: 'efficiency', 'open_circuit_voltage', 'short_circuit_current_density', 'fill_factor', 'potential_at_maximum_power_point', 'current_density_at_maximum_power_point', 'power_density_at_maximum_power_point', 'series_resistance_ohm', 'shunt_resistance_ohm'.
        scan_direction (str): Direction of scan to display. Options: 'Forward', 'Reverse', 'both'. Determines whether to plot only one direction or both.
        trace_colors (dict, optional): Dictionary mapping scan direction ('Forward', 'Reverse') to color values. If not provided, defaults will be used.
        xaxis_title (str, optional): Title for the x-axis. If not provided, defaults will be used.
        group_descriptions (dict, optional): Dictionary to rename x-axis group labels. If provided, overrides default group names.
        title (str, optional): The title of the plot. If not provided, a default title based on the parameter will be used.
        fig (plotly.graph_objects.Figure, optional): Existing figure to update. If None, a new figure will be created.
        showplot (bool, optional): Whether to display the plot. Defaults to True.
        show_group_names (bool, optional): Whether to show group names on the x-axis. Defaults to True.
        group_order (list, optional): Custom order for the group traces. If None, groups will follow the order in the DataFrame.

    Returns:
        plotly.graph_objects.Figure: The generated Plotly figure object.
    """
    
    # Map parameter to corresponding y-axis title and plot title
    # here are the standard yaxis titles and titles defined
    parameter_map = {
        'efficiency': ('PCE [%]', 'PCE'),
        'open_circuit_voltage': ('V<sub>OC</sub> [V]', 'V<sub>OC</sub>'),
        'short_circuit_current_density': ('J<sub>SC</sub> [mA/cm²]', 'J<sub>SC</sub>'),
        'fill_factor': ('Fill Factor', 'FF'),
        'potential_at_maximum_power_point': ('V<sub>MPP</sub> [V]', 'V<sub>MPP</sub>'),
        'current_density_at_maximum_power_point': ('J<sub>MPP</sub> [mA/cm²]', 'J<sub>MPP</sub>'),
        'power_density_at_maximum_power_point': ('P<sub>MPP</sub> [mW/cm²]', 'P<sub>MPP</sub>'),
        'series_resistance_ohm': ('R<sub>series</sub> [Ω]', 'R<sub>series</sub>'),
        'shunt_resistance_ohm': ('R<sub>shunt</sub> [Ω]', 'R<sub>shunt</sub>')
    }

    if parameter not in parameter_map:
        raise ValueError(f"Invalid parameter '{parameter}'. Must be one of {', '.join(parameter_map.keys())}.")
    
    yaxis_title, title = parameter_map[parameter]

    # Get batch ID:
    first_device_id = boxplot_df['lab_id'][0]
    batch_id = f"{first_device_id.split('_')[0]}_{first_device_id.split('_')[1]}"

    # Validate scan direction
    if scan_direction not in ["Forward", "Reverse", "Both", "both"]:
        raise ValueError("scan_direction must be 'Forward', 'Reverse', or 'Both'.")
    

    # Extract unique group numbers from the DataFrame
    if group_order is None:
        group_order = sorted(boxplot_df["group_number"].unique())

    # Create a new figure if one is not provided
    if not fig:
        fig = go.Figure()

    # Plot data based on the scan direction
    # This is the part, when the scans are plotted as seperate traces (to give them different colors)
    if scan_direction.lower() == "both":
      
        # Initialize default colors if not provided
        if trace_colors is None:
            trace_colors = {
                "Reverse": list(colors.values())[0],
                "Forward": list(colors.values())[1]
            }

        # Plot for both 'Forward' and 'Reverse' scan directions
        for direction in ["Reverse", "Forward"]:
            filtered_df = boxplot_df[boxplot_df["scan_direction"] == direction]
            fig.add_trace(
                go.Box(
                    y=filtered_df[parameter],
                    x=filtered_df["group_number"],
                    name=direction,
                    marker_color=trace_colors[direction],
                    boxmean=True,  # Optionally show the mean as well
                    hovertext=filtered_df['lab_id'],  # Hover text
                )
            )
        fig.update_layout(boxmode='group')  # Group boxes by x-axis values
        fig.update_layout(title = f"{batch_id} - Both Scans")



    # This is the part, when the groups are plotted as seperate traces (to give them different colors)
    else:
        # Initialize default colors if not provided
        if trace_colors is None:
            trace_colors = {}
            for i, number in enumerate(group_order):
                trace_colors[number] = list(colors.values())[i]

        # Plot for either 'Forward' or 'Reverse' scan direction
        filtered_df = boxplot_df[boxplot_df["scan_direction"] == scan_direction]
        for group_number in group_order:
            group_data = filtered_df[filtered_df["group_number"] == group_number]
            fig.add_trace(
                go.Box(
                    y=group_data[parameter],
                    x=group_data["group_number"],
                    name=str(group_number),
                    marker_color=trace_colors.get(group_number, "gray"),
                    boxmean=True,
                    hovertext=group_data["lab_id"],
                    alignmentgroup=str(group_number),
                    showlegend=False
                )
            )
            fig.update_layout(title = f"{batch_id} - {scan_direction} Scan")

    # Update trace settings (e.g., size, color, jitter)
    fig.update_traces(
        marker_size=10,
        fillcolor='rgba(0,0,0,0)',  # Transparent box fill
        boxpoints='all',  # Show all data points
        boxmean='sd',  # Show mean and standard deviation
        pointpos=0,  # Position of points relative to box
        jitter=0.5,  # Add jitter for better separation between points
    )

    # Update layout with axis titles, font size, etc.
    fig.update_layout(
        title_font_size=38,  # Plot title font size
        yaxis_title=yaxis_title,
        yaxis_zeroline=False,  # No horizontal zero line
        xaxis_tickangle=0,  # Horizontal x-axis labels
        xaxis_ticklabelstep=1,
        xaxis_title=xaxis_title,
        xaxis_type="category",  # Categorical (not numerical) axis to be able to change the order
        yaxis_rangemode="tozero"
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

    # Show the plot if required
    if showplot:
        fig.show()

    return fig











############################ OLD AND OUTDATED ######################################








############################### GET DATA ###############################

def get_jv_data_for_boxplot(groups, list_of_parameters=list_of_parameters, jv_data_list=None, best_measurement=True):

    ### Added query to access only specific measurements

    """
    Retrieves JV measurement data for a list of device groups as needed for make_boxplot() function.

    Parameters:
    - groups (list): List of dictionaries, each containing a group number and a list of samples.
    - list_of_parameters (list): Optional. List of parameter names to extract from JV curve measurements. Defaults to ['voltage', 'current'].

    Returns:
    boxplot_data: List of dictionaries containing group number and corresponding data formatted for make_boxplot() function.

    Notes:
    - This function fetches JV measurement data for each group in the provided list using an API call.
    - The resulting data structure is suitable for generating a box plot of JV characteristics across different groups.
    
    # Example boxplot_data
    boxplot_data = [
        {
            'group_number': 1,
            'data': [
                {'lab_id': 'sample1', 'Reverse': {'Efficiency': 80, 'V_OC': 0.6}},
                {'lab_id': 'sample2', 'Forward': {'Efficiency': 75, 'V_OC': 0.5}},
            ]
        },
        {
            'group_number': 2,
            'data': [
                {'lab_id': 'sample3', 'Reverse': {'Efficiency': 70, 'V_OC': 0.55}},
                {'lab_id': 'sample4', 'Forward': {'Efficiency': 72, 'V_OC': 0.52}},
            ]
        },
    ]
    
    """


    # List to store the data groupwise
    boxplot_data = [] 

    # Iterate over each group
    for i, group in enumerate(groups):
        # Create a new entry in the boxplot_data list for the current group
        boxplot_data.append({
            'group_number': group['number'],  # Store the group number
            'data': []                        # Initialize an empty list to store data for this group
        })

        
        # Retrieve JV measurement data for the current group using an API call

        # Check if jv data is manually given in a list with entries for each group
        if jv_data_list:
            jv_data = jv_data_list[i]
        # Otherwise get best jv measurement for device
        else:
            print(f"API call for group {group['number']}:")
            if group['samples']:
                jv_data = get_jv_measurements_by_device_list(group['samples'], best_measurement=best_measurement)
            else:
                print(f"No samples given for group {group['number']} - {group['description']}")
                continue


        # Iterate over each sample data entry in the retrieved JV data
        for sample_data in jv_data:
            
            # Create dictionary to store the sample data, starting with the device lab ID
            data = dict(lab_id=sample_data['device'])
            print(f"{sample_data['device']}")

            # Iterate over both curves (RV and FW) for the current sample
            for curve in sample_data['jv_curve']:
                # Extract and store only the parameters of interest from the curve
                data[curve['scan']] = {key: value for key, value in curve.items() if key in list_of_parameters}

            # Append the formatted sample data to the current group's data list
            boxplot_data[i]['data'].append(data)
        
    # Return the formatted boxplot data for all groups
    return boxplot_data


############################### PLOT DATA ###############################

def make_boxplot(boxplot_data, groups, parameter='efficiency', scan='Reverse', group_descriptions=None, showplot=True, option='basic', fig=None, alignmentgroup=None):
    """
    Creates a box plot for JV measurement data based on given boxplot_data.

    Parameters:
    - boxplot_data (list): List of dictionaries containing formatted JV measurement data for boxplots.
    - groups (list, optional): List of dictionaries containing group information. Default is None.
    - parameter (str): Parameter to plot. Options include 'efficiency', 'open_circuit_voltage', 'short_circuit_current_density', 
                      'fill_factor', 'potential_at_maximum_power_point', 'current_density_at_maximum_power_point',
                      'power_density_at_maximum_power_point', 'series_resistance_ohm', 'shunt_resistance_ohm'. Default is 'efficiency'.
    - scan (str): Type of scan to use. Options are 'Reverse' or 'Forward'. Default is 'Reverse'.
    - group_descriptions (list, optional): List of descriptions for each group. Default is None.
    - showplot (bool): If True, the plot will be displayed. Defaults to True.
    - option (str): Type of boxplot to create. Options include 'basic' (single scan) or 'scans' (both scans). Default is 'basic'.

    Returns:
    - plotly.graph_objects.Figure: The resulting boxplot figure.

    Notes:
    - This function creates a box plot to visualize JV measurement data across different groups.
    - Depending on the 'option' parameter, it can plot either a single scan or both Forward and Reverse scans.
    - The plot is interactive, allowing users to hover over boxes for detailed information.
    """
    

    # Determine y-axis title and plot title based on parameter
    if parameter == 'efficiency':
        yaxis_title = 'PCE [%]'
        title = 'PCE'  # η, Eff.
    elif parameter == 'open_circuit_voltage':
        yaxis_title = 'V<sub>OC</sub> [V]'
        title = 'V<sub>OC</sub>'
    elif parameter == 'short_circuit_current_density':
        yaxis_title = 'J<sub>SC</sub> [mA/cm²]'
        title = 'J<sub>SC</sub>'
    elif parameter == 'fill_factor':
        yaxis_title = 'Fill Factor'
        title = 'FF'
    elif parameter == 'potential_at_maximum_power_point':
        yaxis_title = 'V<sub>MPP</sub> [V]'
        title = 'V<sub>MPP</sub>'
    elif parameter == 'current_density_at_maximum_power_point': 
        yaxis_title = 'J<sub>MPP</sub> [mA/cm²]'
        title = 'J<sub>MPP</sub>'
    elif parameter == 'power_density_at_maximum_power_point':
        yaxis_title = 'P<sub>MPP</sub> [mW/cm²]'
        title = 'P<sub>MPP</sub>'
    elif parameter == 'series_resistance_ohm':
        yaxis_title = 'R<sub>series</sub> [Ω]'
        title = 'R<sub>series</sub>'
    elif parameter == 'shunt_resistance_ohm':
        yaxis_title = 'R<sub>shunt</sub> [Ω]'
        title = 'R<sub>shunt</sub>'


    # Create Figure
    if not fig:
        fig = go.Figure()


    ### Basic Plot
    if option=='basic':
        
        # We plot the groups as traces
        for group_data in boxplot_data:
            y_data = []  # y_data for boxplot
            devices = [] # needed for hovertext
    
            # Obtain description if groups are given
            if groups:
                for group in groups:
                    if group['number'] == group_data['group_number']:
                        current_group = group
                group_description = current_group['description']
            else:
                group_description = group_data['group_number']

            # Iterate through devices
            for sample_data in group_data['data']:
                y_data.append(sample_data[scan][parameter]) # append data

                # Some additional variables for title, hovertext, etc.
                device = sample_data['lab_id']
                devices.append(device)          
                batch_id = f"{device.split('_')[0]}_{device.split('_')[1]}"

            # Add trace (add box)
            fig.add_trace(go.Box(
                y=y_data,                 # Data
                name=group_description,   # Group/Category
                hovertext=devices,        # Hover text
                alignmentgroup=alignmentgroup,

            ))

        fig.update_layout(
            title=f'<b>{batch_id} - {scan.lower()} scan - {title}</b>',
            showlegend=False)



    ### Both Scans Plot ###
    if option=='scans':
        
        # Prepare Boxplot data for Plotly
        # We plot 2 basic traces (Forward and Reverse)
        for scan in ['Forward', 'Reverse']:
            y_data = []    # y_data for boxplot
            devices = [] # needed for hovertext
            x_groups = []  # x groups  for boxplot grouping (x)

            # We iterate through groups and add them as x values in trace
            for group_data in boxplot_data:
                
                # Obtain description if groups are given
                if groups:
                    for group in groups:
                        if group['number'] == group_data['group_number']:
                            current_group = group
                    group_description = current_group['description']
    
                # Iterate through devices
                for sample_data in group_data['data']:
                    # Append Y data
                    y_data.append(sample_data[scan][parameter])

                    # Grouping
                    if groups:
                        x_groups.append(group_description)
                    else:
                        x_groups.append(group_data['group_number'])

                    # Some additional variables for title, hovertext, etc.                
                    device = sample_data['lab_id']
                    devices.append(device)          
                    batch_id = f"{device.split('_')[0]}_{device.split('_')[1]}"


            # Add trace (add box)
            fig.add_trace(go.Box(
                x=x_groups,
                y=y_data,                 # Data
                name=scan,                # Group/Category
                hovertext=devices,        # Hover text,
            ))

        fig.update_layout(
            title=f'<b>{batch_id} - both scans - {title}</b>',
            #title=f'both scans - {title}</b>',
            showlegend=True,
            boxmode='group', # group together boxes of the different traces for each value of x
        )

    ###### FOR ALL OPTIONS AGAIN ######

    # Update Trace Settings (for all traces)
    fig.update_traces(
        marker_size=10,
        fillcolor='rgba(0,0,0,0)',# Transparent box fill
        boxpoints='all',          # Show all points
        boxmean='sd',             # True for Show mean # 'sd' if standard deviation should be displayd
        pointpos=0,               # Relative position of points with respect to box
        jitter=0.5,               # Adds some jitter for better separation between points
    )



    # Update plot layout
    fig.update_layout(
        title_font_size=38, # 28
        yaxis_title=yaxis_title,
        xaxis_tickangle=0,        # Horizontal text
        xaxis_ticklabelstep=1,
        yaxis_zeroline=False,     # No horizontal zero line
    )


    # Update x-axis tick labels if group_descriptions is provided
    if group_descriptions:
        fig.update_layout(
            xaxis_tickmode='array',
            xaxis_tickvals=list(range(0, len(group_descriptions))),
            xaxis_ticktext=group_descriptions,
        )

    # Correct layout
    update_layout_umr(fig)

    # Show the plot
    if showplot:
        fig.show()

    return fig