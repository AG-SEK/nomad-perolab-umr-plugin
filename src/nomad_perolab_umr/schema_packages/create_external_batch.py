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
import numpy as np
import pandas as pd


# Imports Nomad
from nomad.datamodel.metainfo.eln import Entity
from nomad.datamodel.data import EntryData
from nomad.metainfo import Quantity, SubSection, Section, Package, MEnum, SchemaPackage
from nomad.units import ureg

# Imports HZB
from baseclasses.helper.utilities import create_archive, get_reference, get_entry_id_from_file_name, update_archive


# Imports UMR
from .suggestions_lists import *
from .helper_functions import *
from .categories import *

from .substrate import UMR_ExternalSubstrate, UMR_Substrate
from .solar_cell import UMR_ExternalSolarCell, UMR_BasicSample
from .batch import UMR_ExternalBatch
from .umr_reference_classes import UMR_EntityReference



m_package = SchemaPackage() 

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
            hide=['lab_id'],
            properties=dict(
                order=[
                    'name', 'batch_was_created',
                    'datetime','supplier','batch_name_supplier','our_batch_number',
                    'csv_file', 'create_batch_from_csv_file',
                    'number_of_substrates','substrate_ids', 'substrate_length','substrate_width','substrate_thickness', 'substrate_material', 'conducting_layer',
                    'number_of_solar_cells_on_substrate', 'solar_cell_names', 'solar_cell_length','solar_cell_width', 'architecture', 'encapsulation', 'create_batch',
                    'description'])))
        
    # Quantities

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
    
    csv_file = Quantity(
        type=str,
        description='Upload a CSV file to create the External Batch based on the Information given in the CSV file (see example file)',
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    
    create_batch_from_csv_file = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ActionEditQuantity'))


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
        
        if self.created_entities and not self.batch_was_created:
            self.created_entities = []

        #################################### CREATE BATCH VIA CSV FILE ####################################

        if self.create_batch_from_csv_file:
            self.create_batch_from_csv_file = False

            # Log possible errors
            if self.batch_was_created:
                log_error(self, logger, "The Batch has already been created. This cannot been undone without deleting the Batch folder and creating an new empty one. If you did that uncheck the batch_was_created checkbox.")
                return
            if not self.csv_file:
                log_error(self, logger, "No csv file was given. Please choose a csv-file first.")  
                return
            if not (self.supplier and self.our_batch_number):
                log_error(self, logger, "No supplier and/or batch number is given.")  
                return
            if supplier_abbreviations.get(self.supplier) is None:
                log_error(self, logger, f"The supplier '{self.supplier}' has no abbreviation yet. Please inform the Oasis Administrator.")
                return


            # READ THE CSV FILE into a pandas DataFrame
            with archive.m_context.raw_file(self.csv_file) as f:
                # Determine delimiter of csv file (, or ;)
                delimiter = get_delimiter(f.name)
                if delimiter == None:
                    log_error(self, logger, "Teh delimiter of the csv file is neither ',' nor ';' . Please check that.")
                    return
                df = pd.read_csv(f.name, sep=delimiter, encoding = 'utf-8', na_values=[''])

            # Substitute empty cells (nan) for architecture
            df['architecture'].replace(np.nan, 'Unknown', inplace=True)
            #df['encapsulation'].replace(np.nan, 'None', inplace=True)
            log_info(self, logger, f"READ CSV FILE - DATAFRAME: {df}")

            # Check if substrate material is in suggestion lists
            # TODO: Maybe check more entries
            valid_entries_substrate_material = df['substrate_material'].fillna(pd.NA).isin(suggestions_substrate_material) | df['substrate_material'].isna()
            if not valid_entries_substrate_material.all():
                log_error(self, logger, "The given substrate_material is not part of the suggestion list. Please check the spelling again or add a Substrate Material to the suggestion list (Inform Oasis Administrator).")
                return


            # Clear the list with created entities
            self.created_entities = []

            # Create Batch folder
            from nomad.files import UploadFiles
            upload = UploadFiles.get(archive.metadata.upload_id)
            upload.raw_create_directory("Batch")

            # Get supplier abbreviation
            supplier_abbreviation = supplier_abbreviations[self.supplier]  

            # CREATE BATCH
            batch_lab_id = f"{supplier_abbreviation}_{str(self.our_batch_number).zfill(3)}"
            batch_name = f"batch_{batch_lab_id}"
            batch_file_name = f"Batch/{batch_name}.archive.json"
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
            try:
                create_archive(batch, archive, batch_file_name)
            except Exception as e:
                # Catch Errors, because Batch folder does not exist
                log_error(self, logger, f"An error occured when creating an External Batch. --- Exception {e}")

            # Create batch reference in created_entities
            batch_entry_id = get_entry_id_from_file_name(batch_file_name, archive)
            batch_reference = UMR_EntityReference(
                reference=get_reference(archive.metadata.upload_id, batch_entry_id))
            self.created_entities.append(batch_reference)


            # CREATE SUBSTRATES
            for index, row in df.iterrows():

                # If Values are NaN make the variable None (no quantities should be created)
                substrate_material = None if pd.isna(row['substrate_material']) else row['substrate_material']
                substrate_thickness = None if pd.isna(row['substrate_thickness [mm]']) else row['substrate_thickness [mm]'] * ureg('mm')
                conducting_layer = None if pd.isna(row['conducting_layer']) else row['conducting_layer']
                conducting_layer_thickness = None if pd.isna(row['conducting_layer_thickness [nm]']) else row['conducting_layer_thickness [nm]']* ureg('nm')
                encapsulation = None if pd.isna(row['encapsulation']) else row['encapsulation']

                substrate_lab_id = f"{supplier_abbreviation}_{row['substrate_id']}"
                substrate_name=f"substrate_{substrate_lab_id}"
                substrate_file_name = f"Batch/{substrate_name}.archive.json"
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
                    description = self.description,
                    samples = [],
                )
                # Create Substrate Archive
                create_archive(substrate, archive, substrate_file_name)

                # Create substrate reference in created_entities
                substrate_entry_id = get_entry_id_from_file_name(substrate_file_name, archive)
                substrate_reference = UMR_EntityReference(
                    reference=get_reference(archive.metadata.upload_id, substrate_entry_id))
                # Add substrate reference to batch and in created_entities
                batch.substrates.append(substrate_reference)
                #batch.substrates[i].normalize(archive, logger)
                self.created_entities.append(substrate_reference)


                # CREATE SOLAR CELLS
                for j in range(row['number_of_solar_cells_on_substrate']):
                    solar_cell_lab_id = f"{supplier_abbreviation}_{str(self.our_batch_number).zfill(3)}_{row['substrate_id']}_{str(row['solar_cell_names']).split('|')[j]}"
                    solar_cell_name=f"solar_cell_{solar_cell_lab_id}"
                    solar_cell_file_name = f'Batch/{solar_cell_name}.archive.json'
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
                    # Create Solar Cell Archive
                    create_archive(solar_cell, archive, solar_cell_file_name)

                    # Create solar cell reference
                    solar_cell_entry_id = get_entry_id_from_file_name(solar_cell_file_name, archive)
                    solar_cell_reference = UMR_EntityReference(
                        reference=get_reference(archive.metadata.upload_id, solar_cell_entry_id))
                    # Add solar cell reference to substrate and batch and in created_entities
                    substrate.samples.append(solar_cell_reference)
                    #substrate.samples[j].normalize(archive, logger)
                    batch.samples.append(solar_cell_reference)
                    #batch.samples[j].normalize(archive, logger)
                    self.created_entities.append(solar_cell_reference)


                # Update Substrate Archive (because of appended solar cell references)
                create_archive(substrate, archive, substrate_file_name, overwrite=True)
            # Update Batch Archive (because of appended solar cell and substrate references)
            create_archive(batch, archive, batch_file_name, overwrite=True)

            # Check box batch_was_created
            self.batch_was_created = True


        #################################### CREATE BATCH VIA GUI ####################################
            
        if self.create_batch:
            self.create_batch = False
            
            # Log possible errors
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

            # Create Batch folder
            from nomad.files import UploadFiles
            upload = UploadFiles.get(archive.metadata.upload_id)
            upload.raw_create_directory("Batch")

            # Get supplier abbreviation
            supplier_abbreviation = supplier_abbreviations[self.supplier]  

            # CREATE BATCH
            batch_lab_id = f"{supplier_abbreviation}_{str(self.our_batch_number).zfill(3)}"
            batch_name = f"batch_{batch_lab_id}"
            batch_file_name = f"Batch/{batch_name}.archive.json"
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
            try:
                create_archive(batch, archive, batch_file_name)
            except Exception as e:
                # Catch Errors, because Batch folder does not exist
                log_error(self, logger, f"An error occured when creating an External Batch. --- Exception {e}")

            # Create batch reference in created_entities
            batch_entry_id = get_entry_id_from_file_name(batch_file_name, archive)
            batch_reference = UMR_EntityReference(
                reference=get_reference(archive.metadata.upload_id, batch_entry_id))
            self.created_entities.append(batch_reference)


            # CREATE SUBSTRATES
            for i, substrate_id in enumerate(self.substrate_ids):
                substrate_lab_id = f"{supplier_abbreviation}_{substrate_id}"
                substrate_name=f"substrate_{substrate_lab_id}"
                substrate_file_name = f"Batch/{substrate_name}.archive.json"
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
                    #description = self.description,
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
                # Create Substrate Archive
                create_archive(substrate, archive, substrate_file_name)

                # Create substrate reference in created_entities
                substrate_entry_id = get_entry_id_from_file_name(substrate_file_name, archive)
                substrate_reference = UMR_EntityReference(
                    reference=get_reference(archive.metadata.upload_id, substrate_entry_id))
                # Add substrate reference to batch and in created_entities
                batch.substrates.append(substrate_reference)
                #batch.substrates[i].normalize(archive, logger)
                self.created_entities.append(substrate_reference)


                # CREATE SOLAR CELLS
                for j, solar_cell_name in enumerate(self.solar_cell_names):
                    solar_cell_lab_id = f"{supplier_abbreviation}_{str(self.our_batch_number).zfill(3)}_{substrate_id}_{solar_cell_name}"
                    solar_cell_name=f"solar_cell_{solar_cell_lab_id}"
                    solar_cell_file_name = f'Batch/{solar_cell_name}.archive.json'
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
                    # Create Solar Cell Archive
                    create_archive(solar_cell, archive, solar_cell_file_name)

                    # Create solar cell reference
                    solar_cell_entry_id = get_entry_id_from_file_name(solar_cell_file_name, archive)
                    solar_cell_reference = UMR_EntityReference(
                        reference=get_reference(archive.metadata.upload_id, solar_cell_entry_id))
                    # Add solar cell reference to substrate and batch and in created_entities
                    substrate.samples.append(solar_cell_reference) 
                    #substrate.samples[j].normalize(archive, logger)
                    batch.samples.append(solar_cell_reference)
                    #batch.samples[j].normalize(archive, logger)
                    self.created_entities.append(solar_cell_reference)
                
                # Update Substrate Archive (because of appended solar cell references)
                create_archive(substrate, archive, substrate_file_name, overwrite=True)
            # Update Batch Archive (because of appended solar cell and substrate references)
            create_archive(batch, archive, batch_file_name, overwrite=True)

            # Check box batch_was_created
            self.batch_was_created = True

        super(UMR_CreateExternalBatch, self).normalize(archive, logger)

        ########################################################################


m_package.__init_metainfo__()


