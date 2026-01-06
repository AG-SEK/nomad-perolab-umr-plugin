'''
In this script we collect functions which are used for the full batch analysis.


This are functions which are applied on an already existing figure. (e.g. from plot_jv)
The functions then change the color of the different traces and group them in legendgroups
Furthermore buttons are displayed to toggle between different substrates or groups

'''

import plotly.io as pio

from .helper_functions import (
    find_group_by_lab_id,
    find_group_number,
    get_group_description,
    get_plotted_cell_descriptions,
    get_plotted_substrates,
    map_colors_to_items,
    map_linepattern_to_items,
)


def plot_batch(initial_fig, batch, group_by='group', showplot=True, show_all_button=False):
    """
    Plot batch data with the option to group by groups or substrates.

    Parameters:
    - fig (plotly.graph_objs.Figure): Plotly figure object to update.
    - groups (list): List of dictionaries representing groups, each containing 'number' and 'description' keys.
    - group_by (str): Specifies whether to group traces by 'group' or 'substrate'. Defaults to 'group'.
    - showplot (bool): If True, displays the plot after updating. Defaults to True.

    Returns:
    - fig (plotly.graph_objs.Figure): Updated Plotly figure object.

    Notes:
    - The function updates the colors and legend groups of traces in the provided figure based on the grouping method.
    - It also adds a button to show all traces and adjusts the legend position for better layout.
    """
    # Copy figure
    fig = initial_fig

    # Map colors to substrates
    substrates = get_plotted_substrates(fig)
    substrate_color_dict = map_colors_to_items(substrates)

    # Map colors to groups
    list_group_numbers = [group['group_number'] for group in batch['groups']]
    group_color_dict = map_colors_to_items(list_group_numbers)

    # Change color of traces based on substrate and form legendgroup
    for trace in fig.data:
        # Extract substrate, cell name and group
        device = trace.meta['device']
        substrate = device.split('_')[2]  # Extract substrate number (5-digits)
        group= find_group_by_lab_id(batch, device)
        group_number = group['group_number']

        # Change trace
        if group_by == 'substrate':
            trace.line.color = substrate_color_dict[substrate]
            trace.marker.color = substrate_color_dict[substrate]
            trace.legendgroup = substrate
            trace.legendgrouptitle.text = substrate
            trace.legendgrouptitle.font.size = 16
        elif group_by == 'group':
            trace.line.color = group_color_dict[group_number]
            trace.marker.color = group_color_dict[group_number]
            trace.legendgroup = group_number
            trace.legendgrouptitle.text = group['group_description']
            trace.legendgrouptitle.font.size = 16
            # Using legendgroups enables us to show and hide all curves of each substrate simultaneously

    if show_all_button:
        ## Button to show all traces
        
        # New Button to show all plots
        new_button = dict(
            label="Show All",
            method="update",
            args=[{'visible': [True] * len(fig.data)}]  # Make all traces visible
        )

        # Check if updatemenus is already existing
        if not fig.layout.updatemenus:
            fig.layout.updatemenus=pio.templates['UMR'].layout.updatemenus  # toggle button for grid
            fig.layout.updatemenus[0].buttons = [new_button]
        else:
            # Append new Button to existing updatemenus
            current_buttons = fig.layout.updatemenus[0].buttons
            fig.layout.updatemenus[0].buttons = list(current_buttons) + [new_button]

    # Update Layout (Legend)
    fig.update_layout(
        legend_xanchor='left',
        legend_x=1.02,
        legend_font_size=14,
        width=920,  # increase width because legend outside of plot
    )

    if showplot:
        fig.show()

    return fig



def plot_groups(initial_fig, batch, menu='buttons', showplot=True, group_number=None):
    """
    Plot grouped data with interactive buttons or dropdown menu for selecting groups.

    Parameters:
    - fig (plotly.graph_objs.Figure): Plotly figure object to update.
    - groups (list): List of dictionaries representing groups, each containing 'number' and 'description' keys.
    - menu (str): Type of interactive menu to display for selecting groups. Options are 'buttons' or 'dropdown'. Defaults to 'buttons'.
    - showplot (bool): If True, displays the plot after updating. Defaults to True.
    - group_number (int or None): If provided, shows only the traces belonging to the specified group number initially. Defaults to None.

    Returns:
    - fig (plotly.graph_objs.Figure): Updated Plotly figure object.

    Notes:
    - This function updates the colors and line patterns of traces in the provided figure based on the groups.
    - It allows interaction with the plot using either buttons or a dropdown menu to select and display specific groups.
    - Additionally, it supports showing traces of a specific group initially if group_number is specified.
    """

    # Copy figure
    fig = initial_fig
    # List with traces
    list_traces = []
    # Map colors to substrates
    substrates = get_plotted_substrates(fig)
    substrate_color_dict = map_colors_to_items(substrates)
    # Map line patterns to cells
    cells = get_plotted_cell_descriptions(fig)
    cell_linepattern_dict = map_linepattern_to_items(cells)

    # Change color and linepattern of traces based on substrate and cell
    for trace in fig.data:
        # Extract substrate and cell name
        device = trace.meta['device']
        substrate = device.split('_')[2]  # Extract substrate number (5-digits)
        group= find_group_by_lab_id(batch, device)
        group_no = group['group_number']
        cell = device.split('_')[-1]
        # Add group number to metadata
        trace.meta['group_number'] = group_no
        # Change trace
        trace.line.color = substrate_color_dict[substrate]
        trace.marker.color = substrate_color_dict[substrate]
        trace.line.dash = cell_linepattern_dict[cell]
        # Default: Make only the first group visible
        trace.visible = True if group_no == batch['groups'][0]['group_number'] else False 
        list_traces.append(device)

    # Add Button for each group
    if not group_number:
        buttons = []
        for group in batch['groups']:
            list_group_samples = [sample_ref['lab_id'] for sample_ref in group['samples']]
            if not any(item in list_traces for item in list_group_samples):
                print(f"Skip group {group['group_number']} - {group['group_description']}. No solar cells for this group in the Plot.")
            else:
                buttons.append(dict(
                    label=group['group_description'],
                    method='update',
                    args=[{'visible': [True if trace.meta['group_number'] == group['group_number'] else False for trace in fig.data]}],
                ))
            
                ### Dropdown Menu ###
                if menu == 'dropdown':
                    # Dropdown Menu
                    new_updatemenu = dict(
                        type='dropdown',
                        y=1.15,
                        xanchor='left',
                        buttons=buttons,
                        font_size=16,
                    )
                    # Add new updatemenu to figure
                    updatemenus = list(fig.layout.updatemenus)  # Get current list of updatemenus
                    updatemenus.append(new_updatemenu)  # Append new updatemenu
                    fig.update_layout(updatemenus=updatemenus)
                
                ### Buttons Menu ###
                elif menu == 'buttons':
                    # Buttons List Menu
                    new_updatemenu = dict(
                        type="buttons",
                        y=1.15,
                        xanchor='left',
                        buttons=buttons,
                        font_size=16,
                        direction='left',
                    )
                    # Add new updatemenu to figure
                    updatemenus = list(fig.layout.updatemenus)
                    updatemenus.append(new_updatemenu)
                    fig.update_layout(
                        width=850,
                        updatemenus=updatemenus,
                    )

    # Update Layout (Legend)
    fig.update_layout(
        legend_xanchor='left',
        legend_x=1.02,
        legend_font_size=14,
        width=920,  # increase width because legend outside of plot
    )


    # Show specific substrate at beginning
    if group_number:
        for trace in fig.data:
            group_no = trace.meta['group_number']
            trace.visible = True if group_no == group_number else False
        fig.layout.updatemenus = [] # Delete all Buttons
        description = get_group_description(batch, group_number)
        fig.update_layout(title=description)
   

    if showplot:
        fig.show()

    return fig



def plot_substrates(initial_fig, menu='buttons', showplot=True, substrate_number=None):
    """
    Plot substrates data with interactive buttons or dropdown menu for selecting substrates.

    Parameters:
    - fig (plotly.graph_objs.Figure): Plotly figure object to update.
    - menu (str): Type of interactive menu to display for selecting substrates. Options are 'buttons' or 'dropdown'. Defaults to 'buttons'.
    - showplot (bool): If True, displays the plot after updating. Defaults to True.
    - substrate_number (str or None): If provided, shows only the traces belonging to the specified substrate number initially. Defaults to None.

    Returns:
    - fig (plotly.graph_objs.Figure): Updated Plotly figure object.

    Notes:
    - This function updates the colors and line patterns of traces in the provided figure based on substrates and cells.
    - It allows interaction with the plot using either buttons or a dropdown menu to select and display specific substrates.
    - Additionally, it supports showing traces of a specific substrate initially if substrate_number is specified.
    """

    # Copy figure
    fig = initial_fig

    # Map colors to substrates
    substrates = get_plotted_substrates(fig)
    substrate_color_dict = map_colors_to_items(substrates)

    # Map line patterns to cells
    cells = get_plotted_cell_descriptions(fig)
    cell_linepattern_dict = map_linepattern_to_items(cells)

    # Change color of traces based on substrate and cell
    for trace in fig.data:
        device = trace.meta['device']
        substrate = device.split('_')[2]  # Extract substrate number (5-digits)
        cell = device.split('_')[3]
        trace.line.color = substrate_color_dict[substrate]
        trace.line.dash = cell_linepattern_dict[cell]
        trace.visible = True if substrate == substrates[0] else False


    # Add Button for each substrate
    buttons = []
    for substrate in substrates:
        buttons.append(dict(
            label=substrate,
            method='update',
            args=[{'visible': [True if trace.meta['device'].split('_')[2] == substrate else False for trace in fig.data]}],
        ))

    ### Dropdown Menu ###
    if menu == 'dropdown':
        # Dropdown Menu
        new_updatemenu=dict(
            type='dropdown',
            y=1.15,
            xanchor='left',
            buttons=buttons,
            font_size=16,
        )
        # Add new updatemenu to figure
        updatemenus = list(fig.layout.updatemenus)  # Get current list of updatemenus
        updatemenus.append(new_updatemenu)  # Append new updatemenu
        fig.update_layout(updatemenus=updatemenus)
    
    ### Buttons Menu ###
    elif menu == 'buttons':
        # Buttons Menu
        new_updatemenu=dict(
            type="buttons",
            x=1.02,
            xanchor='left',
            buttons=buttons,
            font_size=16,
        )
        # Add new updatemenu to figure
        updatemenus = list(fig.layout.updatemenus)
        updatemenus.append(new_updatemenu)
        fig.update_layout(
            width=850,
            updatemenus=updatemenus,
        )


    # Show specific substrate at beginning
    if substrate_number:
        for trace in fig.data:
            device = trace.meta['device']
            substrate = device.split('_')[2]  # Extract substrate number (5-digits)
            trace.visible = True if substrate == substrate_number else False
        fig.layout.updatemenus = []
        fig.update_layout(title=substrate_number)

   
    # Update Layout (Legend)
    fig.update_layout(legend_font_size=16)


    if showplot:
        fig.show()

    return fig







############################################################
############################################################
############################################################
# OUTDATED FUNCTIONS - DO NOT USE ANYMORE -> ONLY FOR LEGACY USE


def get_groups(batch, only_solar_cells=True):
    """
    OUTDATED FUNCTION: ONLY USE IF REALLY NECCESARY

    Extracts groups from the given batch dictionary and returns them as a list of dictionaries.

    This function processes a batch dictionary to extract group information, including group number, description,
    samples (solar cell IDs), and substrates. Each group is represented as a dictionary in the returned list.

    Parameters:
    - batch (dict): A dictionary representing a batch of data containing groups (e.g., as returned by get_batch_by_id).
    - only_solar_cells (bool): Flag indicating whether to include only solar cell samples. Defaults to True.

    Returns:
    list of dict: A list of dictionaries, each representing a group with the following keys:
        - 'number' (int/str): The identifier of the group.
        - 'description' (str): The description of the group.
        - 'samples' (list of str): A list of IDs representing solar cell samples.
        - 'substrates' (list of str): A list of IDs representing substrates associated with the group.
    """

    groups = [] # empty groups list

    for group in batch['groups']:

        # Create smample list
        if only_solar_cells==True:
            # Put only real solar cells in samples list
            samples = [item['lab_id'] for item in group['samples'] if item['lab_id'].split('_')[-1] != 'X']
        else:
            # Put all samples (including basic samples wit "X" in samples list
            samples=[item['lab_id'] for item in group['samples']]

        # Create group dictionary for each group in the batch
        group_dict = dict(
            number=group['group_number'],
            description=group['group_description'],
            samples=samples,
            substrates = [item['lab_id'].split('_')[-1] for item in group['substrates']] # All substrate numbers (only last part of e.g. SNX_00020)
        )
        # Append group dictionary to list
        groups.append(group_dict)

    return groups


def filter_groups(groups, group_numbers):
    """
    OUTDATED FUNCTION: ONLY USE IF REALLY NECCESARY

    Filters the list of groups to only include those with specified group numbers.

    This function takes a list of group dictionaries and a list of group numbers, 
    returning a new list that only includes the groups whose 'number' key matches 
    one of the specified group numbers.

    Parameters:
    - groups (list of dict): The original list of group dictionaries. (see get_groups)
    - group_numbers (list of int/str): The group numbers to retain in the filtered list.

    Returns:
    list of dict: A filtered list of dictionaries that only contains the groups 
                  with the specified group numbers.

    """
    # Filter groups (Take only groups with given group numbers)
    filtered_groups = [group for group in groups if group['number'] in group_numbers]

    return filtered_groups


def remove_sample_from_groups(lab_ids_to_remove, groups):
    """
    OUTDATED FUNCTION: ONLY USE IF REALLY NECCESARY

    Removes a sample with the given lab_id from the provided list of groups.
   
    This function searches through each group in the list and removes the sample 
    with the specified lab_id if it is found. It also prints a message indicating 
    whether the sample was removed and from which group, or if it was not found.

    Parameters:
    - lab_ids_to_remove (list of str): A list of lab_ids to delete from each group.
    - groups (list): A list of dictionaries, where each dictionary represents a group. (see get_groups)

    """
    
    # Check if list or single id is given and create list
    if not isinstance(lab_ids_to_remove, list):
        lab_ids_to_remove = [lab_ids_to_remove]


    for lab_id in lab_ids_to_remove:
        removed = False

        for group in groups:
            # Get samples for each Group
            samples = group.get('samples', [])
 
           
            # Iterate through samples to find the one with lab_id_to_delete
            if lab_id in samples:
                samples.remove(lab_id)
                print(f"Sample '{lab_id}' was removed from group {group['number']}")
                removed = True
        
        if not removed:
            print(f"Sample '{lab_id}' was not found in the groups")

    return groups



def plot_groups_old(fig, groups, menu='buttons', showplot=True, group_number=None):
    """
   OUTDATED FUNCTION: ONLY USE IF REALLY NECCESARY
    """

    # Map colors to substrates
    substrates = get_plotted_substrates(fig)
    substrate_color_dict = map_colors_to_items(substrates)
    # Map line patterns to cells
    cells = get_plotted_cell_descriptions(fig)
    cell_linepattern_dict = map_linepattern_to_items(cells)

    # Change color and linepattern of traces based on substrate and cell
    for trace in fig.data:
        # Extract substrate and cell name
        device = trace.meta['device']
        substrate = device.split('_')[2]  # Extract substrate number (5-digits)
        group = find_group_number(groups, device)
        cell = device.split('_')[-1]
        # Add group number to metadata
        trace.meta['group_number'] = group
        # Change trace
        trace.line.color = substrate_color_dict[substrate]
        trace.marker.color = substrate_color_dict[substrate]
        trace.line.dash = cell_linepattern_dict[cell]
        # Default: Make only the first group visible
        trace.visible = True if group == groups[0]['number'] else False 

    # Add Button for each group
    buttons = []
    for group in groups:
        buttons.append(dict(
            label=group['description'],
            method='update',
            args=[{'visible': [True if trace.meta['group_number'] == group['number'] else False for trace in fig.data]}],
        ))
    
    ### Dropdown Menu ###
    if menu == 'dropdown':
        # Dropdown Menu
        new_updatemenu = dict(
            type='dropdown',
            y=1.15,
            xanchor='left',
            buttons=buttons,
            font_size=16,
        )
        # Add new updatemenu to figure
        updatemenus = list(fig.layout.updatemenus)  # Get current list of updatemenus
        updatemenus.append(new_updatemenu)  # Append new updatemenu
        fig.update_layout(updatemenus=updatemenus)
    
    ### Buttons Menu ###
    elif menu == 'buttons':
        # Buttons List Menu
        new_updatemenu = dict(
            type="buttons",
            y=1.15,
            xanchor='left',
            buttons=buttons,
            font_size=16,
            direction='left',
        )
        # Add new updatemenu to figure
        updatemenus = list(fig.layout.updatemenus)
        updatemenus.append(new_updatemenu)
        fig.update_layout(
            width=850,
            updatemenus=updatemenus,
        )

    # Update Layout (Legend)
    fig.update_layout(
        legend_xanchor='left',
        legend_x=1.02,
        legend_font_size=14,
        width=920,  # increase width because legend outside of plot
    )


    # Show specific substrate at beginning
    if group_number:
        for trace in fig.data:
            group = trace.meta['group_number']
            trace.visible = True if group == group_number else False
        fig.layout.updatemenus = [] # Delete all Buttons
        for group in groups:
            if group['number'] == group_number:
                # If group number found return description
                description = group['description']

        fig.update_layout(title=description)
   

    if showplot:
        fig.show()

    return fig






def plot_batch_old(fig, groups, group_by='group', showplot=True, show_all_button=False):
    """
   OUTDATED FUNCTION: ONLY USE IF REALLY NECCESARY
    """

    # Map colors to substrates
    substrates = get_plotted_substrates(fig)
    substrate_color_dict = map_colors_to_items(substrates)

    # Map colors to groups
    list_group_numbers = [group['number'] for group in groups]
    group_color_dict = map_colors_to_items(list_group_numbers)

    # Change color of traces based on substrate and form legendgroup
    for trace in fig.data:
        # Extract substrate, cell name and group
        device = trace.meta['device']
        substrate = device.split('_')[2]  # Extract substrate number (5-digits)
        group_number = find_group_number(groups, device)

        # Change trace
        if group_by == 'substrate':
            trace.line.color = substrate_color_dict[substrate]
            trace.marker.color = substrate_color_dict[substrate]
            trace.legendgroup = substrate
            trace.legendgrouptitle.text = substrate
            trace.legendgrouptitle.font.size = 16
        elif group_by == 'group':
            trace.line.color = group_color_dict[group_number]
            trace.marker.color = group_color_dict[group_number]
            trace.legendgroup = group_number
            trace.legendgrouptitle.text = groups[group_number-1]['description']
            trace.legendgrouptitle.font.size = 16
            # Using legendgroups enables us to show and hide all curves of each substrate simultaneously

    if show_all_button:
        ## Button to show all traces
        
        # New Button to show all plots
        new_button = dict(
            label="Show All",
            method="update",
            args=[{'visible': [True] * len(fig.data)}]  # Make all traces visible
        )

        # Check if updatemenus is already existing
        if not fig.layout.updatemenus:
            fig.layout.updatemenus=pio.templates['UMR'].layout.updatemenus  # toggle button for grid
            fig.layout.updatemenus[0].buttons = [new_button]
        else:
            # Append new Button to existing updatemenus
            current_buttons = fig.layout.updatemenus[0].buttons
            fig.layout.updatemenus[0].buttons = list(current_buttons) + [new_button]

    # Update Layout (Legend)
    fig.update_layout(
        legend_xanchor='left',
        legend_x=1.02,
        legend_font_size=14,
        width=920,  # increase width because legend outside of plot
    )

    if showplot:
        fig.show()

    return fig  