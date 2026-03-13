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


# Imports Python general
import os
import numpy as np
import pandas as pd

# Imports HZB
from baseclasses.helper.utilities import (
    create_archive,
    get_entry_id_from_file_name,
    get_reference,
    get_encoding
)

from nomad.datamodel.data import EntryData

# Imports Nomad
from nomad.datamodel.metainfo.eln import Entity
from nomad.metainfo import MEnum, Quantity, SchemaPackage, Section, SubSection
from nomad.units import ureg

from .batch import UMR_ExternalBatch
from .categories import *
from .helper_functions import *
from .solar_cell import UMR_BasicSample, UMR_ExternalSolarCell
from .substrate import UMR_ExternalSubstrate, UMR_Substrate

# Imports UMR
from .suggestions_lists import *
from .umr_reference_classes import UMR_EntityReference

m_package = SchemaPackage(aliases=['UMR_schemas.create_external_batch '])

################################ Create External Batch ################################

class UMR_ExternalSubstrateSettings(UMR_Substrate):
    # Displays only substrate_area, conducting_material_thickness, structuring, surface_resistivity and transmission
    m_def = Section(
        label='Advanced Properties - External Substrate',
        a_eln=dict(
            hide=['conducting_material', 'substrate', 'solar_cell_area', 'pixel_area',
                'name', 'batch', 'datetime', 'number_of_pixels', 'group', 'lab_id', 'supplier', 'width', 'length', 'substrate_thickness', 'substrate_material', 'conducting_layer', 'samples'],
            properties=dict(
                order=['substrate_area', 'conducting_layer_thickness', 'structuring', 'surface_resistivity', 'transmission', 'description'])))
    
    def normalize(self, archive, logger):
        return
        # Do not call normalize functions of parent classes!


class UMR_ExternalSolarCellSettings(UMR_BasicSample):
    # Displays only area and layers
    m_def = Section(
        label='Advanced Properties - External Solar Cell',
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition',
                'name', 'batch', 'datetime', 'group_number', 'lab_id', 'substrate', 'device_names', 'architecture', 'encapsulation', 'width', 'length', 'sample_id',
                'measurements', 'other_device_names'],
            properties=dict(
                order=['area','description','layers'])))
    
    def normalize(self, archive, logger):
        return
        # Do not call normalize functions of parent classes!


class UMR_CreateExternalBatch(Entity, EntryData):
    m_def = Section(
        categories=[UMRCreateCategory],
        label='Create External Batch',
        a_eln=dict(
            hide=['lab_id', "csv_file", "create_batch_from_csv_file", "name"],
            properties=dict(
                editable=dict(exclude=["batch_id"]),
                order=[
                    "batch_id",
                    "fill_general_info",
                                                            'datetime','supplier','batch_name_supplier','our_batch_number', 'responsible_person', "description",
                    #'csv_file', 'create_batch_from_csv_file',
                    "enter_substrates",
                    'number_of_substrates','substrate_ids', 'substrate_length','substrate_width','substrate_thickness', 'substrate_material', 'conducting_layer',
                    "enter_cells",
                    'number_of_solar_cells_on_substrate', 'solar_cell_names', 'solar_cell_length','solar_cell_width', 'architecture', 'encapsulation', 'create_batch',
                    'batch_was_created',
                    ])))
        

    
    ### CHECKLIST

    fill_general_info = Quantity(
        type=bool,
        label="1. Enter general information.",
        description="Fill the ELN fields 'datetime', 'supplier', 'batch name (supplier)', 'responsible person' and 'our batch number' with the general information about the Batch. Feel free to add additiona information in the 'description' field. Save the entry afterwards, the 'batch_id' is then generated automatically.",
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
    enter_substrates = Quantity(
        type=bool,
        label="2. Enter substrate information",
        description="Enter the number of substrates and all substrate ids. Additionally enter the dimensions of the substrate (lenght, width, height as well as the substrate material and conducting layer. If you want to add more detailed information about the substrate use the 'advanced substrate settings' section.)",
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
    enter_cells = Quantity(
        type=bool,
        label="3. Enter solar cell information",
        description="Enter the number of solar cells on each substrate and all solar cell names. Additionally enter the dimensions of the cells (lenght, width) as well as the cell architecture and if given encapsulation. If you want to add more detailed information about the cells use the 'advanced solar cells settings' section.)",
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    

    # Quantities
    batch_id = Quantity(
        type = str,
        description = "Automatically generated based on batch number and supplier . You cannot edit the ID.",
        a_eln=dict(component='StringEditQuantity'))

    supplier = Quantity(
        type=MEnum(suggestions_supplier),
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_supplier)))
    
    batch_name_supplier = Quantity(   
        type=str,
        a_eln=dict(component='StringEditQuantity',
            label='Batch name (Supplier)'))
    
    our_batch_number =  Quantity(  # our numbering
        type=int,
        a_eln=dict(component='NumberEditQuantity'))
    
    responsible_person = Quantity(
        type = MEnum(suggestions_persons),
        description = 'Person responsible for this batch. Choose from the Dropdown List. If your name does not appear, please inform the Oasis administrator.',
        a_eln = dict(
            label="responsible person", # For type MEnum a label has to be given i the a_eln section,oterhwise it is not displayed -> bug???
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_persons)))

    number_of_substrates = Quantity(  # our numbering
        type=int,
        a_eln=dict(component='NumberEditQuantity'))
    
    substrate_ids = Quantity(   
        type=str,
        description="Only the number engraved on the substrate",
        shape=['number_of_substrates'],
        a_eln=dict(component='StringEditQuantity'))
    
    substrate_width = Quantity(
        type=np.float64,
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    substrate_length = Quantity(
        type=np.float64,
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    substrate_thickness = Quantity( 
        type=np.float64,
        unit='mm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm')) 
      
    substrate_material = Quantity( 
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_substrate_material)))
    
    conducting_layer = Quantity(
        type=str,
         description='Choose the name of the conducting layer from the dropdown list or type in a new one.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_conducting_material)))
    
    number_of_solar_cells_on_substrate= Quantity(
        type=int,
        a_eln=dict(component='NumberEditQuantity'))
    
    solar_cell_names = Quantity(   
        type=str,
        desription='Names of the solar cells, like 1,2,3,4 or A,B,C,D',
        shape=['number_of_solar_cells_on_substrate'],
        a_eln=dict(component='StringEditQuantity'))
    
    solar_cell_length = Quantity(
        type=np.float64,
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    solar_cell_width = Quantity(
        type=np.float64,
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    architecture = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_architecture)))
    
    encapsulation = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_encapsulation)))
    
    create_batch = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ActionEditQuantity'))
    
    batch_was_created = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    

    # SubSections
    advanced_substrate_settings = SubSection(section_def=UMR_ExternalSubstrateSettings)
    advanced_solar_cell_settings = SubSection(section_def = UMR_ExternalSolarCellSettings)
    created_entities = SubSection(section_def = UMR_EntityReference, repeats=True)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        # Empty created entiteis subsection if batch not created
        if self.created_entities and not self.batch_was_created:
            self.created_entities = []

        # Create batch_id
        if self.supplier and self.our_batch_number:
            batch_abbreviation = supplier_abbreviations.get(self.supplier)  
            batch_id = f"{batch_abbreviation}_{str(self.our_batch_number).zfill(3)}"
            self.batch_id=batch_id


        # Check current status of Batch Plan and automatically check checkboxes
        if not (self.supplier and self.our_batch_number):
            log_warning(self, logger, "Please enter the 'supplier and the 'batch_number' in the Batch Plan")
        else:
            self.fill_general_info = True

            if isinstance(self, UMR_CreateExternalBatch) and not isinstance(self, UMR_CreateExternalBatchViaCSV):
                if not (self.number_of_substrates and self.substrate_ids):
                    log_warning(self, logger, "Please enter Substrate information")
                else:
                    self.enter_substrates = True
                    
                    if not (self.number_of_solar_cells_on_substrate and self.solar_cell_names):
                        log_warning(self, logger, "Please enter Solar Cell information")
                    else:
                        self.enter_cells = True

        #################################### CREATE BATCH VIA GUI ####################################
            
        if self.create_batch:
            self.create_batch = False
            
            # Log possible errors / VALIDATION
            if self.batch_was_created:
                log_error(self, logger, "The Batch has already been created. This cannot been undone without deleting the Batch folder and creating an new empty one. If you did that uncheck the batch_was_created checkbox.")
                return
            if not (self.supplier and self.our_batch_number and self.number_of_substrates and self.number_of_solar_cells_on_substrate):
                log_error(self, logger, "The solar cells cannot be generated because at least one field of either 'supplier', 'batch_number', 'number_of_substrates', number_of_solar_cells_on_substrate' or 'substrate_ids', has not been filled in.")
                return
            if len(self.substrate_ids) != self.number_of_substrates:
                log_error(self, logger, "The number of entered substrate IDs does not match the specified number of substrates.")
                return
            if len(self.solar_cell_names) != self.number_of_solar_cells_on_substrate:
                log_error(self, logger, "The number of entered solar cell names does not match the specified number of solar cells on each substrate.")
                return 
            if supplier_abbreviations.get(self.supplier) is None:
                log_error(self, logger, f"The suppplier '{self.supplier}' has no abbreviation yet. Please inform the Oasis Administrator.")
                return
            
            # Clear the list with created entities
            self.created_entities = []

            # Create directory structure
            for dir_path in ["Batch", "Batch/Substrates", "Batch/Samples", "Batch/SolarCells"]:
                create_directory(self, archive, logger, dir_path)
           
            # Prepare batch identifiers
            batch_abbreviation = supplier_abbreviations[self.supplier]  
            batch_lab_id = f"{batch_abbreviation}_{str(self.our_batch_number).zfill(3)}"
            batch_name = f"batch_{batch_lab_id}"
            batch_file_name = f"Batch/{batch_name}.archive.json"
            

            # CREATE BATCH
            batch = UMR_ExternalBatch(
                name = f"Batch {batch_lab_id}",
                datetime = self.datetime,
                lab_id = batch_lab_id,
                supplier = self.supplier,
                batch_number = self.our_batch_number,
                external_batch_name_supplier = self.batch_name_supplier,
                description = self.description,
                samples = [],
                substrates = [],
            )

            # Get batch entry ID (will be created at the end)
            batch_entry_id = get_entry_id_from_file_name(batch_file_name, archive)
            batch_reference = UMR_EntityReference(
                name=batch.name,
                reference=get_reference(archive.metadata.upload_id, batch_entry_id),
                lab_id=batch.lab_id
            )
            self.created_entities.append(batch_reference)

            # CREATE SUBSTRATES AND SAMPLES
            for substrate_id in self.substrate_ids:
                # Substrate setup
                substrate_lab_id = f"{batch_abbreviation}_{str(self.our_batch_number).zfill(3)}_{str(substrate_id)}"
                substrate_file_name = f"Batch/Substrates/substrate_{substrate_lab_id}.archive.json"
                substrate_entry_id = get_entry_id_from_file_name(substrate_file_name, archive)

                substrate = UMR_ExternalSubstrate(
                    name = f"Substrate {substrate_lab_id}",
                    datetime = self.datetime,
                    lab_id = substrate_lab_id,
                    batch = get_reference(archive.metadata.upload_id, batch_entry_id), #Reference batch in substrate
                    supplier = self.supplier,
                    substrate_material = self.substrate_material,
                    substrate_thickness = self.substrate_thickness,
                    conducting_layer = self.conducting_layer,
                    length = self.substrate_length,
                    width = self.substrate_width,
                    number_of_pixels = self.number_of_solar_cells_on_substrate,
                    samples = [],
                )
                
                # Add optional advanced properties
                if self.advanced_substrate_settings:
                    substrate.substrate_area = self.advanced_substrate_settings.substrate_area 
                    substrate.conducting_layer_thickness = self.advanced_substrate_settings.conducting_layer_thickness
                    substrate.structuring = self.advanced_substrate_settings.structuring
                    substrate.surface_resistivity = self.advanced_substrate_settings.surface_resistivity
                    substrate.transmission = self.advanced_substrate_settings.transmission
                    if self.advanced_substrate_settings.description:
                        substrate.description = self.advanced_substrate_settings.description

                # ADD BASIC SAMPLE

                sample_lab_id = f"{substrate_lab_id}_X"
                sample_file_name = f"Batch/Samples/sample_{sample_lab_id}.archive.json"
                sample = UMR_BasicSample(
                    name=f"Sample {sample_lab_id}",
                    datetime=self.datetime,
                    lab_id=sample_lab_id,
                    batch=get_reference(archive.metadata.upload_id, batch_entry_id),
                    substrate = get_reference(archive.metadata.upload_id, substrate_entry_id),
                    width=substrate.width,
                    length=substrate.length,
                )
                
                # Save sample and get reference
                create_archive(sample, archive, sample_file_name)
                sample_entry_id = get_entry_id_from_file_name(sample_file_name, archive)
                sample_reference = UMR_EntityReference(
                    name=sample.name,
                    reference=get_reference(archive.metadata.upload_id, sample_entry_id),
                    lab_id=sample.lab_id
                )
                # Add sample to substrate
                substrate.samples.append(sample_reference)

                for solar_cell_name in self.solar_cell_names:
                    # Create Solar Cell
                    solar_cell_lab_id = f"{batch_abbreviation}_{str(self.our_batch_number).zfill(3)}_{substrate_id}_{solar_cell_name}"
                    solar_cell_archive_name=f"solar_cell_{solar_cell_lab_id}"
                    solar_cell_file_name = f'Batch/SolarCells/{solar_cell_archive_name}.archive.json'

                    solar_cell = UMR_ExternalSolarCell(
                        name = f"Solar Cell {solar_cell_lab_id}",
                        datetime = self.datetime,
                        lab_id = solar_cell_lab_id,
                        batch = get_reference(archive.metadata.upload_id, batch_entry_id), #Reference batch in solar_cell
                        substrate = get_reference(archive.metadata.upload_id, substrate_entry_id),  #Reference substrate in solar cell
                        supplier = self.supplier,
                        architecture = self.architecture,
                        encapsulation = self.encapsulation,
                        width = self.solar_cell_width,
                        length = self.solar_cell_length,
                        #description= self.description
                    )
                    # Add optional advanced properties
                    if self.advanced_solar_cell_settings:
                        solar_cell.area = self.advanced_solar_cell_settings.area 
                        solar_cell.layers = self.advanced_solar_cell_settings.layers
                        if self.advanced_solar_cell_settings.description:
                            solar_cell.description = self.advanced_solar_cell_settings.description  

                    # Save solar cell and get reference
                    create_archive(solar_cell, archive, solar_cell_file_name)
                    solar_cell_entry_id = get_entry_id_from_file_name(solar_cell_file_name, archive)
                    solar_cell_reference = UMR_EntityReference(
                        name=solar_cell.name,
                        reference=get_reference(archive.metadata.upload_id, solar_cell_entry_id),
                        lab_id=solar_cell.lab_id
                    )
                    
                    # Add solar cell to substrate
                    substrate.samples.append(solar_cell_reference)
                        
                    # Add to batch and created_entities
                    batch.samples.append(solar_cell_reference)
                    self.created_entities.append(solar_cell_reference)

                
                # Save substrate with solar cell references
                #substrate.normalize(archive, logger)
                create_archive(substrate, archive, substrate_file_name)
                

                # Create substrate reference
                #substrate_entry_id = get_entry_id_from_file_name(substrate_file_name, archive)
                substrate_reference = UMR_EntityReference(
                    name=substrate.name,
                    reference=get_reference(archive.metadata.upload_id, substrate_entry_id),
                    lab_id=substrate.lab_id
                )

                # Add to batch and created_entities
                batch.substrates.append(substrate_reference)
                self.created_entities.append(substrate_reference)
                batch.samples.append(sample_reference)
                self.created_entities.append(sample_reference)



            # SAVE BATCH (only once, at the end)
            try:
                create_archive(batch, archive, batch_file_name)
                log_info(self, logger, f"Created batch archive: {batch_file_name} with lab_id '{batch_lab_id}'")
               # Mark batch as created
                self.batch_was_created = True
            except Exception as e:
                log_error(self, logger, f"An error occurred when creating an Internal Batch. --- Exception {e}")
                return





class UMR_CreateExternalBatchViaCSV(UMR_CreateExternalBatch, EntryData):

    m_def = Section(
        categories=[UMRCreateCategory],
        label='Create External Batch via csv file',
        a_eln=dict(
            hide=['lab_id', "name", "create_batch",
                  "enter_substrates", "number_of_substrates", "substrate_ids", "substrate_width", "substrate_length", "substrate_thickness", "substrate_material", "conducting_layer",
                  "enter_cells", "number_of_solar_cells_on_substrate", "solar_cell_names", "solar_cell_length", "solar_cell_width", "architecture", "encapsulation",
                  "advanced_substrate_settings", "advanced_solar_cell_settings"],
            properties=dict(
                editable=dict(exclude=["batch_id"]),
                order=[
                    "batch_id",
                    "fill_general_info",
                    'datetime','supplier','batch_name_supplier','our_batch_number', 'responsible_person', "description",
                    'csv_file', 'create_batch_from_csv_file',
                    'batch_was_created',
                    ])))
    
    csv_file = Quantity(
        type=str,
        description='Upload a CSV or XLSX file to create the External Batch based on the information given in the file (see example file)',
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    
    create_batch_from_csv_file = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ActionEditQuantity'))
        

    def normalize(self, archive, logger):
        
        super().normalize(archive, logger)

        # Empty created entiteis subsection if batch not created
        if self.created_entities and not self.batch_was_created:
            self.created_entities = []

        # Create batch_id
        if self.supplier and self.our_batch_number:
            batch_abbreviation = supplier_abbreviations.get(self.supplier)  
            batch_id = f"{batch_abbreviation}_{str(self.our_batch_number).zfill(3)}"
            self.batch_id=batch_id

        # Check current status of Batch Plan and automatically check checkboxes
        if not (self.supplier and self.our_batch_number):
            log_warning(self, logger, "Please enter the 'supplier and the 'batch_number' in the Batch Plan")
        else:
            self.fill_general_info = True

    
        #################################### CREATE BATCH VIA CSV FILE ####################################

        if self.create_batch_from_csv_file:
            self.create_batch_from_csv_file = False

            # Log possible errors
            if self.batch_was_created:
                log_error(self, logger, "The Batch has already been created.")
                return
            if not self.csv_file:
                log_error(self, logger, "No CSV or XLSX file was given. Please choose a file first.")
                return
            if not (self.supplier and self.our_batch_number):
                log_error(self, logger, "No supplier and/or batch number is given.")  
                return
            if supplier_abbreviations.get(self.supplier) is None:
                log_error(self, logger, f"The supplier '{self.supplier}' has no abbreviation yet. Please inform the Oasis Administrator.")
                return


            # READ THE CSV/XLSX FILE into a pandas DataFrame
            with archive.m_context.raw_file(self.csv_file) as f:
                file_extension = os.path.splitext(f.name)[1].lower()
                if file_extension == '.xlsx':
                    try:
                        df = pd.read_excel(f.name, engine='openpyxl', na_values=[''])
                    except Exception as exc:
                        log_error(self, logger, f"Failed to read XLSX file: {exc}")
                        return
                elif file_extension == '.csv':
                    # Determine delimiter of csv file (, or ;)
                    delimiter = get_delimiter(f.name)
                    if delimiter is None:
                        log_error(self, logger, "The delimiter of the CSV file is neither ',' nor ';'. Please check that.")
                        return
                    with open(f.name, 'rb') as raw_file:
                        encoding = get_encoding(raw_file)

                        df = pd.read_csv(
                            f.name,
                            sep=delimiter,
                            encoding=encoding,
                            na_values=[''],
                        )
                else:
                    log_error(self, logger, "Unsupported file type. Please upload a CSV or XLSX file.")
                    return

            # Substitute empty cells (nan) for architecture
            df['architecture'].replace(np.nan, 'Unknown', inplace=True)
            #df['encapsulation'].replace(np.nan, 'None', inplace=True)

            # Check if substrate material is in suggestion lists
            # TODO: Maybe check more entries
            valid_entries_substrate_material = df['substrate_material'].fillna(pd.NA).isin(suggestions_substrate_material) | df['substrate_material'].isna()
            if not valid_entries_substrate_material.all():
                log_error(self, logger, "The given substrate_material is not part of the suggestion list. Please check the spelling again or add a Substrate Material to the suggestion list (Inform Oasis Administrator).")
                return

            # Clear the list with created entities
            self.created_entities = []

            # Create directory structure
            for dir_path in ["Batch", "Batch/Substrates", "Batch/Samples", "Batch/SolarCells"]:
                create_directory(self, archive, logger, dir_path)

            # Prepare batch identifiers
            batch_abbreviation = supplier_abbreviations[self.supplier]  
            batch_lab_id = f"{batch_abbreviation}_{str(self.our_batch_number).zfill(3)}"
            batch_name = f"batch_{batch_lab_id}"
            batch_file_name = f"Batch/{batch_name}.archive.json"
            
            # CREATE BATCH
            batch = UMR_ExternalBatch(
                name = f"Batch {batch_lab_id}",
                datetime = self.datetime,
                lab_id = batch_lab_id,
                supplier = self.supplier,
                batch_number = self.our_batch_number,
                external_batch_name_supplier = self.batch_name_supplier,
                description = self.description,
                samples = [],
                substrates = [],
            )

            # Get batch entry ID (will be created at the end)
            batch_entry_id = get_entry_id_from_file_name(batch_file_name, archive)
            batch_reference = UMR_EntityReference(
                name=batch.name,
                reference=get_reference(archive.metadata.upload_id, batch_entry_id),
                lab_id=batch.lab_id
            )
            self.created_entities.append(batch_reference)


            # CREATE SUBSTRATES
            for index, row in df.iterrows():

                # If Values are NaN make the variable None (no quantities should be created)
                substrate_material = None if pd.isna(row['substrate_material']) else row['substrate_material']
                substrate_thickness = None if pd.isna(row['substrate_thickness [mm]']) else row['substrate_thickness [mm]'] * ureg('mm')
                conducting_layer = None if pd.isna(row['conducting_layer']) else row['conducting_layer']
                conducting_layer_thickness = None if pd.isna(row['conducting_layer_thickness [nm]']) else row['conducting_layer_thickness [nm]']* ureg('nm')
                encapsulation = None if pd.isna(row['encapsulation']) else row['encapsulation']

                substrate_lab_id = f"{batch_abbreviation}_{str(self.our_batch_number).zfill(3)}_{row['substrate_id']}"
                substrate_name=f"substrate_{substrate_lab_id}"
                substrate_file_name = f"Batch/Substrates/{substrate_name}.archive.json"
                substrate_entry_id = get_entry_id_from_file_name(substrate_file_name, archive)

                substrate = UMR_ExternalSubstrate(
                    name = f"Substrate {substrate_lab_id}",
                    datetime = self.datetime,
                    lab_id = substrate_lab_id,
                    batch = get_reference(archive.metadata.upload_id, batch_entry_id), #Reference batch in substrate
                    supplier = self.supplier,
                    substrate_material = substrate_material,
                    substrate_thickness = substrate_thickness,
                    conducting_layer = conducting_layer,
                    conducting_layer_thickness = conducting_layer_thickness,
                    length = row['substrate_length [cm]'] * ureg('cm'),
                    width = row['substrate_width [cm]'] * ureg('cm'),
                    number_of_pixels=row['number_of_solar_cells_on_substrate'],
                    #description = self.description,
                    samples = [],
                )


                # ADD BASIC SAMPLE
                sample_lab_id = f"{substrate_lab_id}_X"
                sample_file_name = f"Batch/Samples/sample_{sample_lab_id}.archive.json"
                sample = UMR_BasicSample(
                    name=f"Sample {sample_lab_id}",
                    datetime=self.datetime,
                    lab_id=sample_lab_id,
                    batch=get_reference(archive.metadata.upload_id, batch_entry_id),
                    substrate = get_reference(archive.metadata.upload_id, substrate_entry_id),
                    width=substrate.width,
                    length=substrate.length,
                )

                # Save sample and get reference
                create_archive(sample, archive, sample_file_name)
                sample_entry_id = get_entry_id_from_file_name(sample_file_name, archive)
                sample_reference = UMR_EntityReference(
                    name=sample.name,
                    reference=get_reference(archive.metadata.upload_id, sample_entry_id),
                    lab_id=sample.lab_id
                )

                # Add sample to substrate
                substrate.samples.append(sample_reference)

                # CREATE SOLAR CELLS
                for j in range(row['number_of_solar_cells_on_substrate']):
                    solar_cell_lab_id = f"{batch_abbreviation}_{str(self.our_batch_number).zfill(3)}_{row['substrate_id']}_{str(row['solar_cell_names']).split('|')[j]}"
                    solar_cell_name=f"solar_cell_{solar_cell_lab_id}"
                    solar_cell_file_name = f'Batch/SolarCells/{solar_cell_name}.archive.json'
                    
                    solar_cell = UMR_ExternalSolarCell(
                        name = f"Solar Cell {solar_cell_lab_id}",
                        datetime = self.datetime,
                        lab_id = solar_cell_lab_id,
                        batch = get_reference(archive.metadata.upload_id, batch_entry_id), #Reference batch in solar_cell
                        substrate = get_reference(archive.metadata.upload_id, substrate_entry_id),  #Reference substrate in solar cell
                        supplier = self.supplier,
                        architecture = row['architecture'],
                        encapsulation = encapsulation,
                        width = row['solar_cell_width [cm]'] * ureg('cm'),
                        length = row['solar_cell_length [cm]'] * ureg('cm'),
                        description= self.description
                    )


                    # Save solar cell and get reference
                    create_archive(solar_cell, archive, solar_cell_file_name)
                    solar_cell_entry_id = get_entry_id_from_file_name(solar_cell_file_name, archive)
                    solar_cell_reference = UMR_EntityReference(
                        name=solar_cell.name,
                        reference=get_reference(archive.metadata.upload_id, solar_cell_entry_id),
                        lab_id=solar_cell.lab_id
                    )
                    
                    # Add solar cell to substrate
                    substrate.samples.append(solar_cell_reference)
 
                    # Add to batch and created_entities
                    batch.samples.append(solar_cell_reference)
                    self.created_entities.append(solar_cell_reference)

                # Save substrate with solar cell references
                #substrate.normalize(archive, logger)
                create_archive(substrate, archive, substrate_file_name)


                # Create substrate reference
                substrate_reference = UMR_EntityReference(
                    name=substrate.name,
                    reference=get_reference(archive.metadata.upload_id, substrate_entry_id),
                    lab_id=substrate.lab_id
                )

                # Add to batch and created_entities
                batch.substrates.append(substrate_reference)
                self.created_entities.append(substrate_reference)
                batch.samples.append(sample_reference)
                self.created_entities.append(sample_reference)



            # SAVE BATCH (only once, at the end)
            try:
                create_archive(batch, archive, batch_file_name)
                log_info(self, logger, f"Created batch archive: {batch_file_name} with lab_id '{batch_lab_id}'")
               # Mark batch as created
                self.batch_was_created = True
            except Exception as e:
                log_error(self, logger, f"An error occurred when creating an Internal Batch. --- Exception {e}")
                return










m_package.__init_metainfo__()


