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

from baseclasses.helper.utilities import get_reference, create_archive, get_entry_id_from_file_name



# Function to determine the delimiter of a csv file, depending on the first line
def get_delimiter(file_path):
    with open(file_path, 'r') as file:
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
    with files.UploadFiles.get(upload_id).read_archive(entry_id) as archive:
        archive = archive[entry_id] #method = archive[entry_id]['data']['method']
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
    with archive.m_context.raw_file(mainfile, 'r') as file:
        data = json.load(file)
    entry = entry.from_dict(data['data'])
    return entry


def add_process_and_layer_to_sample(ELN_entry, archive, logger, sample_ref, process_entry):
    '''function to add the process and layer to the sample'''    
    
    # Use current Datetime in new entry
    if ELN_entry.use_current_datetime == True:
        ELN_entry.datetime = dt.datetime.now()
        
    # Update Process from ELN Process entry
    process_entry.m_update_from_dict(ELN_entry.m_to_dict())
    # Remove Samples
    process_entry.samples = []

    #Get sample entry
    mainfile = sample_ref.reference.m_root().metadata.mainfile
    sample_entry =  get_entry_by_mainfile(ELN_entry, archive, mainfile)

    # Add description from Sample Reference to process dscription
    if sample_ref.description:
        if ELN_entry.description:
            process_entry.description = ELN_entry.description + "\n" + sample_ref.description
        else:
            process_entry.description = sample_ref.description
    
    # Add process to sample
    sample_entry.processes.append(process_entry)

    # Add layer to sample entry
    if hasattr(ELN_entry, 'layer'):
        for layer in ELN_entry.layer:         # ELN_entry.layer is a list!
            sample_entry.layers.append(layer.m_resolved().m_copy(deep=True))

    # Add sample to sample list (in ELN process entry)
    ELN_entry.samples.append(sample_ref.m_resolved().m_copy(deep=True)) # without m_copy it would be a CompositeSystem Reference not a UMR_EntityReference!

    #ELN_entry.selected_samples.remove(sample_ref)

    # Update Sample
    create_archive(sample_entry, archive, mainfile, overwrite=True)

    return sample_entry



def create_solar_cell_from_basic_sample(ELN_entry, archive, logger, sample_entry, solar_cell_name, solar_cell_entry):
    '''function to create the solar cells on a substrate baeed on the already existing basic sample of the substrate'''
    solar_cell_lab_id = f"{sample_entry.lab_id[:-1]}{solar_cell_name}" # TODO Fehler abfangen
    solar_cell_name=f"solar_cell_{solar_cell_lab_id}"
    solar_cell_file_name = f'Batch/SolarCells/{solar_cell_name}.archive.json'
    
    # Create and update Solar Cell based on Basic Sample Entry
    solar_cell_entry.m_update_from_dict(sample_entry.m_to_dict())
    solar_cell_entry.name = f"Solar Cell {solar_cell_lab_id}"
    solar_cell_entry.lab_id = solar_cell_lab_id
    solar_cell_entry.datetime = ELN_entry.datetime

    create_archive(solar_cell_entry, archive, solar_cell_file_name)
    
    solar_cell_entry_id = get_entry_id_from_file_name(solar_cell_file_name, archive)
    return solar_cell_entry_id, solar_cell_entry  # return value as variable for next function


def create_solar_cell_references(ELN_entry, archive, logger, sample_ref, solar_cell_reference):

    # Add solar cell to sample list (in ELN process entry)
    log_warning(ELN_entry, logger, f"REFE {solar_cell_reference}" )
    ELN_entry.samples.append(solar_cell_reference) #.m_resolved().m_copy(deep=True)) # without m_copy it would be a CompositeSystem Reference not a UMR_EntityReference!
    # TODO


    # Add Sample reference to batch
    # Load batch entry
    mainfile = sample_ref.reference.batch.m_root().metadata.mainfile
    batch = get_entry_by_mainfile(ELN_entry, archive, mainfile)
    # Append sample
    batch.samples.append(solar_cell_reference)

    # Add sample reference to group in batch
    # Load group entry 
    group_number = sample_ref.reference.group_number
    batch.groups[group_number-1].samples.append(solar_cell_reference)

    # Update batch entry
    create_archive(batch, archive, mainfile, overwrite=True)

    # Add sample reference to substrate
    # Load substrate entry
    mainfile = sample_ref.reference.substrate.m_root().metadata.mainfile
    substrate = get_entry_by_mainfile(ELN_entry, archive, mainfile)
    # Append sample
    substrate.samples.append(solar_cell_reference)
    # Update substrate entry
    create_archive(substrate, archive, mainfile, overwrite=True)



def create_directory(ELN_entry, archive, logger, directory_name):
    '''
    Fuction to create a directory. Used in Batch Plan Process to create Batch, Processes, SUbstrates, SolarCells,... folders
    '''

    from nomad.files import UploadFiles

    # Get the upload using the upload_id from the archive
    upload = UploadFiles.get(archive.metadata.upload_id)

    # Check if the directory already exists
    if not upload.raw_path_exists(directory_name):
        # Create directory
        upload.raw_create_directory(directory_name)
        log_warning(ELN_entry, logger, f"Created Directory '{directory_name}' in '{archive.metadata.upload_name}'.")
    else:
        # Folder exists, skip creation
        log_warning(ELN_entry, logger, f"Directory '{directory_name}' already exists in '{archive.metadata.upload_name}'.")





# Make a boolean out of a string (false, FALSE, true, TRUE)
def text_to_bool(text):
    if text == "Yes":
        return True
    if text == "No":
        return False
    # Manage true, True, TRUE
    else:
        return text.upper() == 'TRUE'