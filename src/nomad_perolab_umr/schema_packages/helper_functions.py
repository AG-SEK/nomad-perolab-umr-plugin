#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


### Helper functions

import datetime as dt
import json
import re

import plotly.io as pio
from baseclasses.helper.utilities import (
    create_archive,
    get_entry_id_from_file_name,
    get_reference,
)

from natsort import natsorted

from Solar.plottemplate.umr_plot_template import umr
# Register UMR template
pio.templates["UMR"] = umr



# Function to sort and deduplicate a List in a subsection (e.g. samples, selected_samples)
def sort_and_deduplicate_subsection(subsection, sort_by="name", deduplicate_by="lab_id"):
        
    original_list = subsection # copy of subsection list
    seen = set() # collection of seen lab_ids
    deduplicated_list = [] # empty list to fill

    # Deduplicate   
    for item in original_list:
        if item[deduplicate_by] not in seen:
            seen.add(item[deduplicate_by])
            deduplicated_list.append(item)

    # Sort
    sorted_list = natsorted(deduplicated_list, key=lambda x: x[sort_by])

    return sorted_list

          

# Function to determine the delimiter of a csv file, depending on the first line
def get_delimiter(file_path):
    with open(file_path) as file:
        first_line = file.readline()
    
    # Überprüfe das Trennzeichen in der ersten Zeile
    if ',' in first_line:
        return ','
    elif ';' in first_line:
        return ';'
    else:
        return None  # Wenn weder Komma noch Semikolon gefunden werden
    

def plotly_updateLayout_NOMAD(fig):
    """
    This function explicitly sets some values in the Plotly plots again, because they are not correctly transfered from our template.
    Furthermore a smaller font is used.
    The parameters are so far:
    - showlegend
    - axes (tickfont_size, title_font_size, automargin, ticks)
    Width and Heigth are always displayed differently by NOMAD
    """
    axis = dict(
        tickfont_size=14,
        tickfont_family='Calibri',
        title_font_size=14,
        automargin=True,
        ticks='inside',
        ) 
    fig.update_layout(
        #font_size=14,
        xaxis=axis,
        yaxis=axis,
        yaxis2=axis,
        showlegend=True,
        #font_family = 'Calibri',
        #template="plotly_dark"
    )
    
    # New font size for tables
    for entry in fig['data']:
        if 'cells' in entry:
            entry['cells']['font']['size'] = 14
        if 'header' in entry:
            entry['header']['font']['size'] = 14
            

plot_config = dict(
    #toImageButtonOptions = {
        #'format': 'svg', # one of png, svg, jpeg, webp
        #'filename': 'plot',
        #'height': 500,
        #'width': 700,
        #'scale': 1 # Multiply title/legend/axis/canvas sizes by this factor
    #},
    scrollZoom = False,
    responsive = False,
    displayModeBar = True,
    #staticPlot= True,
    )




# log error method (from Micha)
def log_error(plan_obj, logger, msg):
    if logger:
        logger.error(
            msg, normalizer=plan_obj.__class__.__name__,
            section='system')
    else:
        raise Exception

# log info method
def log_info(plan_obj, logger, msg):
    if logger:
        logger.info(
            msg, normalizer=plan_obj.__class__.__name__,)
            #section='system')
    else:
        raise Exception

# log warning method
def log_warning(plan_obj, logger, msg):
    if logger:
        logger.warning(
            msg, normalizer=plan_obj.__class__.__name__,)
            #section='system')
    else:
        raise Exception

def UMR_search(archive, query, pagination=None):
    from nomad.search import search
    search_result = search(
        owner='all',
        query=query,
        pagination=pagination,
        user_id=archive.metadata.main_author.user_id)
    return search_result


#def search_entry_by_device_name(archive, device_name):
#    query = {
#            #'entry_type:any': ['UMR_InternalSolarCell, UMR_ExternalSolarCell'],
#            'search_quantities': {
#                'id:any': ['data.other_device_names.device_name#UMR_schemas.solar_cell.UMR_ExternalSolarCell','data.other_device_names.device_name#UMR_schemas.solar_cell.UMR_InternalSolarCell'],
#                'str_value': device_name
#                }
#            }
#
#    search_result = UMR_search(archive, query)
#    return search_result


def get_file_name(upload_id, entry_id):
    from nomad import files
    with files.UploadFiles.get(upload_id).read_archive(entry_id) as archive:
        lab_id = archive[entry_id]['data']['file_name']
    return lab_id

def get_lab_id(upload_id, entry_id):
    from nomad import files
    with files.UploadFiles.get(upload_id).read_archive(entry_id) as archive:
        lab_id = archive[entry_id]['data']['lab_id']
    return lab_id
                        
def get_method(upload_id, entry_id):
    from nomad import files
    with files.UploadFiles.get(upload_id).read_archive(entry_id) as archive:
        method = archive[entry_id]['data']['method']
    return method

def get_archive(upload_id, entry_id):
    from nomad import files
    with files.UploadFiles.get(upload_id).read_archive(entry_id) as archive_data:
        archive = archive_data[entry_id] #method = archive[entry_id]['data']['method']
    return archive                               

def get_entry(entry, archive, logger, mainfile):
    import json
    with archive.m_context.raw_file(mainfile, 'r') as file:
        data = json.load(file)
    log_warning(entry, logger, f"GetEntry-DATA:{data}")
    entry = entry.from_dict(data['data'])
    log_warning(entry, logger, f"GetEntry-ENTRY:{entry}")
    return entry


def collect_referencing_entries(entry, archive, logger, entry_type):
    # If entry_type is no list make it a list (because of entry_type:any in query)
    if not isinstance(entry_type, list):
        entry_type = [entry_type]
    
    references = []
    # search for all entries referencing this Entry with the entry_type
    query = {
        'entry_references.target_entry_id': archive.metadata.entry_id,
        'entry_type:any': entry_type}
    search_result = UMR_search(archive, query)
    #log_info(entry, logger, f'COLLECT REFERENCING {entry_type} ENTRIES: search result data: {search_result.data} | length: {len(search_result.data)}')
    
    # Extract data from search results
    if search_result.data:
        for res in search_result.data:
            try:
                upload_id, entry_id = res['upload_id'], res['entry_id']
                # Create reference
                reference = get_reference(upload_id, entry_id)
                references.append(reference)
                log_info(entry, logger, f'INFORMATION ABOUT COLLECTED {entry_type} ENTRIES: upload_id: {upload_id} | entry_id: {entry_id}')
            except Exception as e:
                log_error(entry, logger, f"Error during processing (Collecting {entry_type} Entries) --- EXEPTION:{e}")
    else: 
        log_warning(entry, logger, f'No {entry_type} Entries referencing this entry: {entry.lab_id}')

    return references


# Function to collect JV Parameters Sections (used for MPPTracking and StabilityTest Entries)
def collect_parameters(entry, archive, logger, entry_type):

    references = []
    # query = {
    #     #f'data.directory#UMR_schemas.characterization.{entry_type}': entry.directory,  
    #     f'data.datetime#UMR_schemas.characterization.{entry_type}': entry.datetime.isoformat(),  
    #     f'data.device#UMR_schemas.characterization.{entry_type}': entry.device,
    # }

    from nomad.app.v1.models import WithQuery

    query=WithQuery(query={
        'and': [
            {'search_quantities':
                {'id': f'data.datetime#UMR_schemas.characterization.{entry_type}',
                'datetime_value' : entry.datetime}},
            {'search_quantities':
                {'id': f'data.device#UMR_schemas.characterization.{entry_type}',
                 'str_value': entry.device}},
        ]
    }).query


    search_result = UMR_search(archive, query)
    log_info(entry, logger, f'COLLECT PARAMETERS MEASUREMENTS WITH SAME DIRECTOY - {entry_type} ENTRIES: search result: {search_result} | length: {len(search_result.data)}')

    # Extract data from search results
    if len(search_result.data) == 2:
        for res in search_result.data:
            try:
                upload_id, entry_id = res['upload_id'], res['entry_id']
                # Create reference
                reference = get_reference(upload_id, entry_id)
                references.append(reference)
                log_info(entry, logger, f'INFORMATION ABOUT COLLECTED {entry_type} ENTRIES: upload_id: {upload_id} | entry_id: {entry_id}')
            except Exception as e:
                log_error(entry, logger, f"Error during processing (Collecting {entry_type} Entries) --- EXEPTION:{e}")
    else: 
        log_error(entry, logger, f'INFORMATION ABOUT COLLECTING PARAMETER ENTRIES | Not exactly 2 Parameter Sections (Forward & Reverse) were found for: {entry.name}')
        log_info(entry, logger, f'SEARCH RESULT DATA:{search_result.data} | LENGTH:{len(search_result.data)}')
    
    return references


# Function to collect JV Measurements (used for MPPTracking and StabilityTest Entries)
def collect_jv_curves(entry, archive, logger, entry_type):

    references = []

    #query = {f'data.directory#UMR_schemas.characterization.{entry_type}': entry.directory}
    query = {
        'search_quantities':
            {'id': f'data.directory#UMR_schemas.characterization.{entry_type}',
            'str_value': entry.directory}
        }
        

    from nomad.app.v1.models.models import MetadataPagination
    pagination = MetadataPagination(page_size=10)
    
    while len(references) < 2000: # maximum number of curves searched for
        search_result = UMR_search(archive, query, pagination)
        #log_info(entry, logger, f'COLLECT JV MEASUREMENTS WITH SAME DIRECTOY - {entry_type} ENTRIES: search result data: {search_result.data} | length: {len(search_result.data)}')
        #log_info(entry, logger, f'COLLECT JV MEASUREMENTS WITH SAME DIRECTOY - {entry_type} ENTRIES: pagination: {search_result.pagination} | length: {len(search_result.data)}')

        # Extract data from search results
        if len(search_result.data) >= 1:
            for res in search_result.data:
                try:
                    upload_id, entry_id = res['upload_id'], res['entry_id']
                    # Create reference
                    reference = get_reference(upload_id, entry_id)
                    references.append(reference)
                    log_info(entry, logger, f'INFORMATION ABOUT COLLECTED {entry_type} ENTRIES: upload_id: {upload_id} | entry_id: {entry_id}')
                except Exception as e:
                    log_error(entry, logger, f"Error during processing (Collecting {entry_type} Entries) --- EXEPTION:{e}")
            next_value = search_result.pagination.next_page_after_value
            if not next_value:
                break
            pagination.page_after_value = next_value
        else: 
            log_warning(entry, logger, f'INFORMATION ABOUT COLLECTED JV MEASUREMENTS | No {entry_type} Section was found for: {entry.name}')
            break
        
    return references

#def collect_measurement(entry, archive, logger, entry_type):
    



def check_best_measurements(entry, archive, logger, measurements):
    # Check how many best_measurement entries exist
    best_measurement_objects = [measurement for measurement in measurements if measurement.best_measurement]
    number_of_best_measurements = len(best_measurement_objects)
    if number_of_best_measurements == 1:
        log_info(entry, logger, f"ONE BEST MEASUREMENT SELECTED FOR: {measurements}.")
    elif number_of_best_measurements > 1:
        log_error(entry, logger, f"More than 1 best_measurement. Please check {measurements}. Only 1 best_measurement is allowed.")
    elif number_of_best_measurements == 0:
        log_warning(entry, logger, f"No best_measurement was found for: {measurements}.")

    return number_of_best_measurements # to set best measurement in normalize function directly if number is 0

def set_single_measurement_as_best_measurement(entry, archive, logger, measurements):
    if len(measurements) == 1:
        single_entry=measurements[0]
        single_entry.best_measurement=True
        single_entry_mainfile = single_entry.m_root().metadata.mainfile
        create_archive(single_entry, archive, single_entry_mainfile, overwrite=True)
        log_warning(entry, logger, f"The measurement {single_entry.name} -  was set to best_measurement because it is the only one.")




# Function to collect JV Parameters Sections (used for MPPTracking and StabilityTest Entries)
def collect_extra_data(entry, archive, logger):

    # Es werden noch alle Extra Dateien angezeigt Todo
    references = []
   
    #mainfile_extra = entry.m_root().metadata.mainfile.replace("IV", "Extra")
    #log_warning(entry, logger, f"COLLECT EXTRA: {entry.datetime.isoformat()} | {entry.device}")

    #query= {
    #    'data.device#UMR_schemas.characterization.connection_test.UMR_ConnectionTestExtraData': entry.device,
    #    'data.datetime#UMR_schemas.characterization.connection_test.UMR_ConnectionTestExtraData': entry.datetime
    #}
   

    from nomad.app.v1.models import WithQuery

    # query=WithQuery(query={
    #     'and': [
    #         {'data.datetime#UMR_schemas.characterization.connection_test.UMR_ConnectionTestExtraData': entry.datetime},
    #         {'data.device#UMR_schemas.characterization.connection_test.UMR_ConnectionTestExtraData': entry.device},
    #     ]
    # }).query

    query=WithQuery(query={
        'and': [
            {'search_quantities':{
                'id': 'data.datetime#UMR_schemas.characterization.connection_test.UMR_ConnectionTestExtraData',
                'datetime_value': entry.datetime}},
            {'search_quantities':{
                'id': 'data.device#UMR_schemas.characterization.connection_test.UMR_ConnectionTestExtraData',
                'str_value': entry.device}},
        ]
    }).query

    search_result = UMR_search(archive, query)
    log_info(entry, logger, f'COLLECT EXTRA DATA (CONNECTION TEST) MEASUREMENTS WITH SAME DIRECTOY -  ENTRIES: search result: {search_result} | length: {len(search_result.data)}')

    # Extract data from search results
    if len(search_result.data) == 1:
        for res in search_result.data:
            try:
                upload_id, entry_id = res['upload_id'], res['entry_id']
                # Create reference
                reference = get_reference(upload_id, entry_id)
                references.append(reference)
                log_info(entry, logger, f'INFORMATION ABOUT COLLECTED EXTRA DATA (CONNECTION TEST) ENTRIES: upload_id: {upload_id} | entry_id: {entry_id}')
            except Exception as e:
                log_error(entry, logger, f"Error during processing (Collecting EXTRA DATA (CONNECTION TEST) Entries) --- EXEPTION:{e}")
    else: 
        log_error(entry, logger, f'INFORMATION ABOUT COLLECTING EXTRA DATA (CONNECTION TEST) ENTRIES | Not exactly 1 Extra Data Sections was found for: {entry.name}')
        log_info(entry, logger, f'SEARCH RESULT DATA:{search_result.data} | LENGTH:{len(search_result.data)}')
    
    return references


def get_entry_by_mainfile(entry, archive, mainfile):
    """
    Loads and returns an entry object from the archive using the given mainfile path.
    """

    # Open the archive file corresponding to the mainfile
    with archive.m_context.raw_file(mainfile, 'r') as file:
        data = json.load(file)

    # Populate the entry object with the loaded data
    entry = entry.from_dict(data['data'])

    return entry
 

def add_process_and_layer_to_sample(ELN_entry, archive, logger, sample_ref, process_entry):
    """
    Adds a process and associated layer(s) to a sample entry in the electronic lab notebook (ELN) archive.

    Parameters:
    -----------
    ELN_entry : object
        An ELN entry object containing metadata for the process, layers, and sample references.
    archive : dict
        The full NOMAD archive where the sample and process entries are stored.
    logger : logging.Logger
        Logger object for logging actions, warnings, or errors during the update process.
    sample_ref : object
        A entity reference object, including a reference to the sample that should be updated with the new process and layers.
    process_entry : object
        The process entry to be added to the sample, populated with metadata from ELN_entry.

    Returns:
    --------
    sample_entry : object
        The updated sample entry after attaching the process and layer(s).

    Notes:
    ------
    - The function modifies both the process and sample entry objects.
    - If `ELN_entry.use_current_datetime` is True, the current datetime is set.
    - The sample is saved back into the archive using `create_archive()`.
    """    
    
    # Use current datetime if the ELN entry is configured to do so
    if ELN_entry.use_current_datetime is True:
        ELN_entry.datetime = dt.datetime.now()
        
    # Populate the process entry using the metadata from the ELN entry
    process_entry.m_update_from_dict(ELN_entry.m_to_dict())  
    # Clear any existing samples in the process to avoid unintended duplicates
    process_entry.samples = []

    # Retrieve the sample entry by resolving the reference to its mainfile
    mainfile = sample_ref.reference.m_root().metadata.mainfile
    sample_entry = get_entry_by_mainfile(ELN_entry, archive, mainfile)

    # Merge descriptions from the sample reference and the ELN entry
    if sample_ref.description:
        if ELN_entry.description:
            process_entry.description = ELN_entry.description + "\n" + sample_ref.description
        else:
            process_entry.description = sample_ref.description
    
    # Append the process to the sample's list of processes
    sample_entry.processes.append(process_entry)
            
    # If the ELN entry contains layer information, add each layer to the sample
    if hasattr(ELN_entry, 'layer'):
        for layer in ELN_entry.layer:    # ELN_entry.layer is a list!
            # Deep copy the resolved layer to avoid linking to the original object
            sample_entry.layers.append(layer.m_resolved().m_copy(deep=True))

    # Add the sample reference to the ELN entry's samples list
    #ELN_entry.samples.append(sample_ref.m_resolved().m_copy(deep=True)) # without m_copy it would be a CompositeSystem Reference not a UMR_EntityReference!

    # Use m_copy(deep=False) for shallow copy to avoid issues with parent class SubSections
    resolved_sample = sample_ref.m_resolved()
    sample_copy = resolved_sample.m_copy(deep=False)
    ELN_entry.samples.append(sample_copy)

    # PERFORMANCE: Don't save here - will be batched later to reduce I/O
    # The caller is responsible for saving all updated samples at once
    # create_archive(sample_entry, archive, mainfile, overwrite=True)

    return sample_entry, mainfile



def create_solar_cell_from_basic_sample(ELN_entry, archive, logger, sample_entry, solar_cell_name, solar_cell_entry):
    """
    Creates a new solar cell entry in the archive based on an existing basic sample.

    Parameters:
    -----------
    ELN_entry : object
        The ELN entry providing context such as timestamp and possibly linked metadata.
    archive : dict
        The NOMAD archive where entries are stored and managed.
    logger : logging.Logger
        Logger object (currently unused) for tracking events, warnings, or errors.
    sample_entry : object
        The existing basic sample entry (e.g., substrate) from which the solar cell is derived.
    solar_cell_name : str
        A name or identifier suffix to distinguish the new solar cell.
    solar_cell_entry : object
        The new solar cell entry object that will be initialized and stored.

    Returns:
    --------
    tuple
        (solar_cell_entry_id, solar_cell_entry)
        - `solar_cell_entry_id` is the archive identifier of the newly created solar cell entry.
        - `solar_cell_entry` is the object instance of the created solar cell.

    Notes:
    ------
    - Copies metadata from the basic sample into the solar cell entry.
    - Constructs a unique lab ID and file path for storing the new solar cell entry.
    - Saves the new entry to the archive using `create_archive`.
    - Does not currently handle errors if `sample_entry.lab_id` is not in expected format.

    """   
    
    # Generate a new lab ID by modifying the sample_entry's lab_id
    solar_cell_lab_id = f"{sample_entry.lab_id[:-1]}{solar_cell_name}"
     # TODO Fehler abfangen (Hier wird einfach der letzte Buchstabe der Basic Sample weggenommen und ersetzt)

    # Construct a new name and file path for the solar cell
    solar_cell_name=f"solar_cell_{solar_cell_lab_id}"
    solar_cell_file_name = f'Batch/SolarCells/{solar_cell_name}.archive.json'
    
    # Initialize the solar cell entry using metadata from the basic sample
    solar_cell_entry.m_update_from_dict(sample_entry.m_to_dict())
    solar_cell_entry.name = f"Solar Cell {solar_cell_lab_id}"
    solar_cell_entry.lab_id = solar_cell_lab_id
    solar_cell_entry.datetime = ELN_entry.datetime # Use timestamp from ELN

    # Add architecture
    if ELN_entry.solar_cell_settings.architecture:
        solar_cell_entry.architecture = ELN_entry.solar_cell_settings.architecture # Use timestamp from ELN
    else:
        log_warning(ELN_entry, logger, f"No architecture given i the solar cell settings for this Process: {ELN_entry}")

    
    # Save the solar cell entry to the archive under the generated file name
    create_archive(solar_cell_entry, archive, solar_cell_file_name)

    # Get the ID of the newly created entry from the archive file name
    solar_cell_entry_id = get_entry_id_from_file_name(solar_cell_file_name, archive)

    return solar_cell_entry_id, solar_cell_entry  # return value as input for next method needed


def create_solar_cell_references(ELN_entry, archive, logger, sample_ref, list_solar_cell_references):
    """
    Adds solar cell references to the batch and substrate associated with a given sample reference.
    
    Parameters:
    -----------
    ELN_entry : object
        The ELN entry object that may provide context or metadata for the operation.
    archive : dict
        The NOMAD archive where all entries are stored.
    logger : logging.Logger
        Logger for tracking progress, warnings, or errors.
    sample_ref : object
        A entity reference object with a reference to the sample from which the batch and the substrates are derived.
    list_solar_cell_references : list
        A list of references to the solar cell entries to be added to the batch and substrate.

    Returns:
    --------
    None

    Notes:
    ------
    - This function updates both the batch and substrate to include references to newly created solar cells.
    - Errors in resolving batch or substrate references are logged and skipped.
    """
    # Add solar cell references to sample list (in ELN process entry)
    ELN_entry.samples.extend(list_solar_cell_references) #.m_resolved().m_copy(deep=True)) # without m_copy it would be a CompositeSystem Reference not a UMR_EntityReference!


    # PERFORMANCE: Return batch/substrate info for batched saving later
    # Don't save here - collect all updates first
    try:
        batch_resolved = sample_ref.reference.batch.m_resolved()
        batch_mainfile = batch_resolved.m_root().metadata.mainfile
        batch = get_entry_by_mainfile(ELN_entry, archive, batch_mainfile)
        
        # Append all solar cell references to the batch's samples list
        batch.samples.extend(list_solar_cell_references)
        
        # Add the solar cell references to the appropriate group in the batch
        group_number = sample_ref.reference.group_number
        if group_number and (1 <= group_number <= len(batch.groups)):
            batch.groups[group_number-1].samples.extend(list_solar_cell_references)
        elif group_number:
            log_error(ELN_entry, logger, f"Invalid group number '{group_number}' for batch.")
    except Exception as e:
        log_error(ELN_entry, logger, f"Could not update batch: {e}")
        batch = None
        batch_mainfile = None

    # Get substrate info
    try:
        substrate_resolved = sample_ref.reference.substrate.m_resolved()
        substrate_mainfile = substrate_resolved.m_root().metadata.mainfile
        substrate = get_entry_by_mainfile(ELN_entry, archive, substrate_mainfile)
        
        # Append all solar cell references to the substrate's samples list
        substrate.samples.extend(list_solar_cell_references)
    except Exception as e:
        log_error(ELN_entry, logger, f"Could not update substrate: {e}")
        substrate = None
        substrate_mainfile = None
    
    # Return entries for batched saving
    return batch, batch_mainfile, substrate, substrate_mainfile



def create_directory(ELN_entry, archive, logger, directory_name):
    '''
    Creates a directory in the archive upload. Used during batch planning to organize folders like Batch, Processes, Substrates, SolarCells, etc.
    '''

    from nomad.files import UploadFiles

    # Get the upload context using the upload ID from the archive metadata
    upload = UploadFiles.get(archive.metadata.upload_id)

    # Check if the directory already exists
    if not upload.raw_path_exists(directory_name):
        # Create the directory if it doesn't exist
        upload.raw_create_directory(directory_name)
        log_info(ELN_entry, logger, f"Created Directory '{directory_name}' in '{archive.metadata.upload_name}'.")
    else:
        # Directory already exists; log and skip creation
        log_info(ELN_entry, logger, f"Directory '{directory_name}' already exists in '{archive.metadata.upload_name}'.")





# Make a boolean out of a string (false, FALSE, true, TRUE)
def text_to_bool(text):
    if text == "Yes":
        return True
    if text == "No":
        return False
    # Manage true, True, TRUE
    else:
        return text.upper() == 'TRUE'
    

def sanitize_filename(name: str, replacement: str = "_") -> str:
    """
    Entfernt alle Zeichen aus einem Dateinamen, die problematisch sein könnten.
    
    Erlaubt sind:
    - Groß- und Kleinbuchstaben (A–Z, a–z)
    - Ziffern (0–9)
    - Unterstrich (_), Punkt (.) und Bindestrich (-)

    Andere Zeichen werden durch den `replacement`-Wert ersetzt (Standard: "_").
    """
    pattern = r'[^a-zA-Z0-9_.-]'  # Zeichenklasse: alles außer den erlaubten Zeichen
    cleaned = re.sub(pattern, replacement, name)
    return cleaned