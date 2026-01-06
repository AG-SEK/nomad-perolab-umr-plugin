"""
In this script we collect small helper functions, which are used in other functions
"""

import plotly.io as pio

from ..plottemplate.umr_plot_template import linepattern


def get_jsc_list_from_jv_data(jv_data, show_information=True):
    """
    Extracts the short-circuit current density (Jsc) values from JV measurement data.

    Parameters:
    - jv_data (list of dict): A list of JV measurement data, where each dictionary contains:
        - 'jv_curve' (list of dict): A list of JV curve data with individual scans.
            Each scan dictionary should include:
            - 'scan' (str): The scan direction (e.g., "Reverse").
            - 'short_circuit_current_density' (float): The Jsc value in mA/cm².
        - 'device' (str): The identifier for the device.
    - show_information (bool, optional): If True, prints the extracted Jsc values.
        Default is True.

    Returns:
    - list of float: A list of extracted Jsc values (in mA/cm²) from the reverse JV scans.

"""
    measured_jsc = []
    for jv_measurement in jv_data:
        reverse_jv_curve = [jv_curve for jv_curve in jv_measurement['jv_curve'] if jv_curve.get("scan") == "Reverse"]
        jsc = reverse_jv_curve[0]['short_circuit_current_density'] # in mA/cm²
        measured_jsc.append(jsc)
        if show_information:
            print(f"Jsc of {jv_measurement['device']}: {jsc} mA/cm²")

    return measured_jsc






def remove_data_from_dataframe_by_lab_ids(df, lab_ids_to_remove):
    """
    Entfernt Zeilen mit bestimmten lab_id-Werten aus dem DataFrame.

    :param df: Pandas DataFrame mit einer Spalte 'lab_id'
    :param lab_ids_to_remove: Liste von lab_id-Werten, die entfernt werden sollen
    :return: Gefiltertes DataFrame ohne die angegebenen lab_id-Werte
    """
    return df[~df["lab_id"].isin(lab_ids_to_remove)]


def find_highest_reverse_efficiency_measurement(jv_measurements):
    """
    Finds the JV measurement with the highest efficiency in reverse scan mode.

    This function iterates over a list of JV measurements, examining each curve
    to identify the highest efficiency obtained during a reverse scan. The function
    returns the measurement with the highest efficiency.

    Parameters:
    jv_measurements (list): A list of dictionaries, where each dictionary represents a JV 
                            measurement containing 'device', 'name', and 'jv_curve' keys.
                            The 'jv_curve' key maps to a list of dictionaries, each having
                            'scan' and 'efficiency' keys.

    Returns:
    dict or None: The dictionary representing the JV measurement with the highest
                  reverse scan efficiency. Returns None if no reverse scan with efficiency
                  higher than 0.1 is found.

    """

    max_efficiency = 0.1 # Arbitrary start max_efficiency
    best_measurement = None
    
    for measurement in jv_measurements:
        for curve in measurement['jv_curve']:
            if curve['scan'] == 'Reverse' and curve['efficiency']> max_efficiency:
                max_efficiency = curve['efficiency']
                best_measurement = measurement

    print(f"The best device is {best_measurement['device']} with {max_efficiency} % efficiency (RV Scan) | measurement: {best_measurement['name']}")

    return best_measurement

def filter_groups_of_batch(batch, group_numbers):
    # Extrahiere die Gruppen aus dem Batch
    groups = batch.get("groups", [])
    
    # Filtere die Gruppen basierend auf den angegebenen group_numbers
    filtered_groups = [group for group in groups if group['group_number'] in group_numbers]
    
    # Erstelle eine Kopie des Batch Dictionaries mit den gefilterten Gruppen
    filtered_batch = {"groups": filtered_groups}
    
    return filtered_batch


def sort_measurements_by_device_list(measurements_data, order_list):
    """
    Sorts a list of measurements based on the name of the device.

    Parameters:
    - measurements_data: list of dict
        The list of dictionaries to be sorted. Each dictionary must have the key "device".
    - order_list: list of str
        The desired order of the values for the "device" key.

    Returns:
    - list of dict
        The sorted list of dictionaries.
    """
    # Map the order to positions (for efficient sorting)
    order_mapping = {name: index for index, name in enumerate(order_list)}
    
    # Sort the list based on the order defined in order_list
    sorted_list = sorted(measurements_data, key=lambda x: order_mapping.get(x["device"], float('inf')))
    
    return sorted_list



def find_group_by_lab_id(batch, lab_id):
    """
    Find the group dictionary associated with a given lab_id.

    Args:
        batch (dict): The main batch dictionary containing all data.
        lab_id (str): The lab_id to search for.

    Returns:
        dict or None: The group dictionary if found, else None.
    """
    for group in batch.get('groups', []):
        # Check if the lab_id is in the samples of the group
        for sample in group.get('samples', []):
            if sample.get('lab_id') == lab_id:
                return group

        # Check if the lab_id is in the substrates of the group
        for substrate in group.get('substrates', []):
            if substrate.get('lab_id') == lab_id:
                return group

    return None



def get_samples_from_batch(batch, solar_cells=True, basic_samples=False):
    """
    Extracts sample lab_ids from the given batch, optionally filtering based on sample type.

    Parameters:
    - batch (dict): A dictionary representing a batch as saved in NOMAD Oasis. 
                    It must contain a 'samples' key, which is a list of sample dictionaries, 
                    each having a 'lab_id' field.
    - solar_cells (bool): A flag indicating whether to include samples that do not end with '_X'. 
                          These are considered solar cell samples. Defaults to True.
    - basic_samples (bool): A flag indicating whether to include samples whose lab_ids end with '_X'. 
                            Defaults to False.

    Returns:
    list of str: A list of lab_ids for the samples in the batch. 
                 - If `solar_cells` is True, samples without '_X' suffix are included.
                 - If `basic_samples` is True, samples with '_X' suffix are included.
                 - If both flags are True, both types of samples are included.
    """
    
    samples = []  # List to store sample lab_ids

    # Iterate over each sample in the batch
    for item in batch['samples']:
        lab_id = item['lab_id']

        # Handling of basic samples
        if lab_id.endswith('_X') and basic_samples:
            samples.append(lab_id)

        # handling of solar cell samples
        if not lab_id.endswith('_X') and solar_cells:
            samples.append(lab_id)

    return samples



def get_samples_from_group(group=None, batch=None, group_number=None, solar_cells=True, basic_samples=False):
  
    # Log Errors
    if (group and group_number) or (group and batch):
        print("If you enter a group directly, do no enter a group_number and a batch")
        return
    if (batch and not group_number) or (group_number and not batch):
        print("If you enter a group_number or a batch, please also give the batch or the group_number respectively")
        return

    # Determine grup based on give group_nuber
    if batch and group_number:
        for g in batch['groups']:
            if g['group_number'] == group_number:
                group = g

    samples = []  # List to store sample lab_ids

    # Iterate over each sample in the batch
    for item in group['samples']:
        lab_id = item['lab_id']

        # Handling of basic samples
        if lab_id.endswith('_X') and basic_samples:
            samples.append(lab_id)

        # handling of solar cell samples
        if not lab_id.endswith('_X') and solar_cells:
            samples.append(lab_id)

    return samples

######### Function to map colors to a list of items e.g. groups, substrates #########

colors = pio.templates["UMR"].layout.colorway * 3 # Set UMR standard colors 3x after each other for many substrates

def map_colors_to_items(items_list, colors_list=colors):
    """
    Map colors to items in a list.

    Parameters:
    - items_list (list): List of items to map colors to.
    - colors_list (list): List of colors to map to the items. Defaults to `colors`.

    Returns:
    - item_color_dict (dict): Dictionary mapping items to colors.
    """

    item_color_dict = {}
    for i, item in enumerate(items_list):
        item_color_dict[item] = colors_list[i]

    return item_color_dict
 

######### Function to map linepatterns to a list of items e.g. cells #########


def map_linepattern_to_items(items_list, linepatterns_list=linepattern):
    """
    Map line patterns to items in a list.

    Parameters:
    - items_list (list): List of items to map line patterns to.
    - linepatterns_list (list): List of line patterns to map to the items. Defaults to `linepattern`.

    Returns:
    - item_linepattern_dict (dict): Dictionary mapping items to line patterns.
    """

    item_linepattern_dict = {}
    for i, item in enumerate(items_list):
        item_linepattern_dict[item] = linepatterns_list[i]

    return item_linepattern_dict



######### Function to get the description of a group for a specified group number #########

def get_group_description(batch, group_number):
    """
    Retrieves the description of a group with the specified group number.

    Parameters:
    - groups (list of dict): The list of group dictionaries. 
    - number (int/str): The group number to search for.

    Returns:
    str: The description of the group with the specified number
    
    """
    # Iterate through the groups and check the group number
    for group in batch['groups']:
        if group['group_number'] == group_number:
            # If group number found return description
            return group['group_description']





######### Function to extract the different cell descriptions (e.g. A,B,C,D) from a batch #########

def extract_cell_descriptions(batch):
    '''
    Extracts cell descriptions from a batch of solar cell samples.

    Parameters:
    - batch (dict): A dictionary representing a batch containing:
                  - 'samples' (list of str): A list of sample IDs.

    Returns:
    list of str: A list of unique cell descriptions extracted from the sample IDs.
    '''
    # Extract list of solar cell lab ids from full batch
    samples = batch['samples']
    solar_cells = [sample['lab_id'] for sample in samples if sample['lab_id'].split('_')[-1] != 'X']

    cell_descriptions = set() # Set to collect solar cell descriptions

    for solar_cell in solar_cells:
        # Split the solar cell lab ID by underscores and take the last part -> cell description
        cell_description = solar_cell.split('_')[-1]
        # Add the cell description to the set (automatically handles duplicates)
        cell_descriptions.add(cell_description)
    
    # Convert the set back to a list and return list
    return list(cell_descriptions)


######### Function to obtain all substrate numbers which are plotted in the given figure #########

def get_plotted_substrates(fig):
    '''
    Extracts substrate numbers of solar cells from the traces of a given figure.

    Parameters:
    - fig (object): A figure object containing plotted data. Each trace in fig.data 
                  should have metadata with a 'device' key.
    Returns:
    list of str: A sorted list of unique substrate numbers extracted from the figure.
    '''

    substrate_numbers = set() # Set to collect substrate numbers

    # Extract the substrate number from every trace (metadata)
    for trace in fig.data:
        device = trace.meta['device']
        substrate = device.split('_')[2]  # Extract substrate number (3rd part of the split string)
        substrate_numbers.add(substrate)  # Add to the set (automatically handles duplicates)
    
    # Return sorted list  
    return sorted(substrate_numbers)


#########  Function to extract the different cell descriptions (e.g. A,B,C,D) from the plot #########

def get_plotted_cell_descriptions(fig):
    '''
    Extracts cell descriptions from the traces of a given figure.

    Parameters:
    - fig (object): A figure object containing plotted data. Each trace in fig.data 
                  should have metadata with a 'device' key.
    Returns:
    list of str: A list of unique cell descriptions extracted from the figure.
    '''

    cell_descriptions = set() # Set to collect cell descriptions

    # Extract the cell description (e.g. A, B, C, D) from every trace (metadata)
    for trace in fig.data:
        device = trace.meta['device']
        cell_description = device.split('_')[-1] # Extract cell description (Last part of the split string)
        cell_descriptions.add(cell_description)  # Add to the set (automatically handles duplicates)
    
    # Return sorted list  
    return sorted(cell_descriptions)




### NOT YET REALLY USED, BUT MIGHT BE ACTUALLY NICE


def reorder_traces_by_names(fig, new_order_names):
    """
    Ändert die Reihenfolge der Traces in einer Plotly-Figur basierend auf einer Liste von Namen
    und behält Traces mit dem Namen 'Marker' oder anderen nicht spezifizierten Traces am Ende.

    Parameters:
    - fig: plotly.graph_objects.Figure
        Die ursprüngliche Plotly-Figur.
    - new_order_names: list of str
        Die neue Reihenfolge der Traces, angegeben als Liste von Namen.

    Returns:
    - plotly.graph_objects.Figure
        Die aktualisierte Figur mit der neuen Reihenfolge der Traces.
    """
    # Mapping der Namen auf die Traces
    name_to_trace = {trace.name: trace for trace in fig.data}
    
    # Neue Reihenfolge der Traces basierend auf den Namen
    reordered_data = [name_to_trace[name] for name in new_order_names if name in name_to_trace]
    
    # Hinzufügen aller nicht spezifizierten Traces (z. B. Marker-Traces)
    unspecified_traces = [trace for trace in fig.data if trace.name not in new_order_names]
    reordered_data.extend(unspecified_traces)
    
    # Erstellen einer neuen Figur mit der neuen Trace-Reihenfolge
    fig.data=reordered_data

    return fig




############################################################
# OUTDATED FUNCTIONS - DO NOT USE ANYMORE -> ONLY FOR LEGACY USE





def find_group_number(groups, lab_id):
    '''
    OUTDATED FUNCTION: ONLY USE IF REALLY NECCESARY

    Finds the group number for a given lab_id within a list of groups.

    Parameters:
    - groups (list of dict): A list of dictionaries where each dictionary represents a group. (obtained from get_groups) 
    - lab_id (int/str): The lab_id to search for within the groups.

    Returns:
    int/str: The number of the group that contains the given lab_id, or None if the lab_id is not found in any group.
    '''

    # Check for every group if lab_id is in samples list
    for group in groups:
        if lab_id in group['samples']:
            # If lab_id was found return group number
            return group['number']
    return None
