"""
In this script we collect functiosn which are used to determine the best devices and plot them quickly
"""


from . import find_highest_reverse_efficiency_measurement, plot_batch, get_samples_from_group, find_highest_reverse_efficiency_measurement, plot_jv, plot_eqe, sort_measurements_by_device_list
from ..nomadapifunctions import get_eqe_measurements_by_device_list, get_jv_measurements_by_device_list


def find_and_plot_best_cells(
        boxplot_df,
        batch,
        show_jv=True,
        show_eqe=True,
        names="group_names",
        group_descriptions=None,
        eqe_normalized=False,
        best_measurement_eqe=True,
        best_measurement_jv=True,
    ):
    
    

    print("----- FIND BEST SOLAR CELL DEVICES -----")
 
    # Initialize variables
    jv_measurements = []  # Best JV measurements for each group
    best_cells = []  # Best devices for each group
    group_names = []  # Names or descriptions of groups

    # Iterate through each group in the batch
    for group in batch.get('groups', []):
        print("--------------------------------")
        print(f"Group: {group['name']}")

        # Get group description or use a placeholder if not available
        group_names.append(group['group_description'])
        
        # Filter DataFrame for the current group and Reverse scan direction
        group_df = boxplot_df[(boxplot_df['group_number'] == group['group_number']) & (boxplot_df['scan_direction'] == "Reverse")]
 
        if not group_df.empty:
            # Get the best JV measurement for each device in the group
            best_measurement = group_df.loc[group_df['efficiency'].idxmax()]
            print(f"The best device is {best_measurement['lab_id']} with {best_measurement['efficiency']} % efficiency (RV Scan) | measurement: {best_measurement['measurement_name']}")

            
            # Append to best cells list
            best_cells.append(best_measurement['lab_id'])
        else:
            print("No samples in this group")
            continue

    # Override group names if custom descriptions are provided
    if group_descriptions:
        group_names=group_descriptions
    
    # Set plot names based on the selected naming convention
    if names == "group_names":
        names = group_names
    elif names == "lab_id":
        names = best_cells
    print(best_cells)
    
    # Plot JV measurements if requested
    fig_jv = None
    # Get JV measurements
    print("----- Get JV Measurements -----")
    jv_measurements = get_jv_measurements_by_device_list(best_cells, best_measurement=best_measurement_jv)
    jv_measurements = sort_measurements_by_device_list(jv_measurements, best_cells)
    # Plot JV
    if show_jv:
        fig_jv = plot_jv(full_jv_data=jv_measurements, scan_direction="Reverse", names=names, showplot=False)
        fig_jv.update_traces(marker_size=10)
        fig_jv.show()
  
    # Plot EQE measurements if requested
    fig_eqe = None
    # Get EQE measurements
    print("----- Get EQE Measurements -----")
    eqe_measurements = get_eqe_measurements_by_device_list(best_cells, best_measurement=best_measurement_eqe)
    eqe_measurements = sort_measurements_by_device_list(eqe_measurements, best_cells)
    # Plot EQE
    if show_eqe:
        fig_eqe = plot_eqe(full_eqe_data=eqe_measurements, normalized=eqe_normalized, names=names, linemode="lines+markers", showplot=False)
        fig_eqe.update_traces(marker_size=10)
        fig_eqe.show()    


    return best_cells, group_names, jv_measurements, fig_jv, eqe_measurements, fig_eqe









#### OUTDATED - LEGACY ####

def find_and_plot_best_cells_old(
        batch,
        ignore_cells_list=None,
        show_jv=True,
        show_eqe=True,
        names="group_names",
        group_descriptions=None,
        eqe_normalized=False,
        best_measurement_eqe=True,
        best_measurement_jv=True,
    ):
    
    """
    Identify and plot the best-performing solar cell devices from a batch of groups.

    Parameters:
    - batch (dict): A dictionary containing solar cell groups with relevant data.
    - ignore_cells_list (list, optional): List of cells to exclude from analysis. Defaults to None.
    - show_jv (bool, optional): If True, plot JV measurements for the best devices. Defaults to True.
    - show_eqe (bool, optional): If True, plot EQE measurements for the best devices. Defaults to True.
    - names (str, optional): Specify the naming convention for plots. 
        Options: "group_names" (default) or "lab_id".
    - group_descriptions (list, optional): Custom descriptions for groups. If provided, overrides group names. Defaults to None.
    - eqe_normalized (bool, optional): If True, normalize EQE plots. Defaults to False.

    Returns:
    - tuple: Contains:
        - best_cells (list): Devices corresponding to the best JV measurements for each group.
        - best_jv_measurements (list): Best JV measurement for each group.
        - fig_jv (plotly.graph_objects.Figure or None): JV plot, or None if `show_jv` is False.
        - eqe_measurements (list): EQE measurements of the best devices.
        - fig_eqe (plotly.graph_objects.Figure or None): EQE plot, or None if `show_eqe` is False.
    """

    print("----- FIND BEST SOLAR CELL DEVICES -----")
 
    # Initialize variables
    best_jv_measurements = []  # Best JV measurements for each group
    best_cells = []  # Best devices for each group
    group_names = []  # Names or descriptions of groups

    # Iterate through each group in the batch
    for group in batch.get('groups', []):
        print("--------------------------------")
        print(f"Group: {group['name']}")

        # Get group description or use a placeholder if not available
        group_names.append(group['group_description'])

        # Get samples and filter out ignored cells
        group_samples = get_samples_from_group(group)
        filtered_group_samples = [
            cell for cell in group_samples 
            if ignore_cells_list is None or cell not in ignore_cells_list
        ]

        if filtered_group_samples: 
            # Get the best JV measurement for each device in the group
            measurements = get_jv_measurements_by_device_list(filtered_group_samples, best_measurement=best_measurement_jv, show_devices=False)
            
            # Find the highest reverse efficiency measurement in the group
            best_measurement = find_highest_reverse_efficiency_measurement(measurements)
            
            # Append to respective lists
            best_jv_measurements.append(best_measurement)
            best_cells.append(best_measurement['device'])
        else:
            print("No samples in this group")
            continue

    # Override group names if custom descriptions are provided
    if group_descriptions:
        group_names=group_descriptions
    
    # Set plot names based on the selected naming convention
    if names == "group_names":
        names = group_names
    elif names == "lab_id":
        names = best_cells

    # Plot JV measurements if requested
    fig_jv = None
    if show_jv:
        fig_jv = plot_jv(full_jv_data=best_jv_measurements, scan_direction="Reverse", names=names, showplot=False)
        fig_jv.update_traces(marker_size=10)
        fig_jv.show()
  
    # Plot EQE measurements if requested
    fig_eqe = None
    # Get EQE measurements
    print("----- Get EQE Measurements -----")
    eqe_measurements = get_eqe_measurements_by_device_list(best_cells, best_measurement=best_measurement_eqe)
    eqe_measurements = sort_measurements_by_device_list(eqe_measurements, best_cells)
    
    if show_eqe:
        # Plot EQE
        fig_eqe = plot_eqe(full_eqe_data=eqe_measurements, normalized=eqe_normalized, names=names, linemode="lines+markers", showplot=False)
        fig_eqe.update_traces(marker_size=10)
        fig_eqe.show()    


    return best_cells, best_jv_measurements, fig_jv, eqe_measurements, fig_eqe

