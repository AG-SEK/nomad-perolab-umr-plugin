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

# Imports Python
import numpy as np
import json

# Imports Nomad
from nomad.metainfo import Quantity, SubSection, Section, SchemaPackage, Reference
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.datamodel.metainfo.basesections import SectionReference

# Imports HZB
from baseclasses.material_processes_misc import Cleaning, SolutionCleaning, PlasmaCleaning, UVCleaning, Annealing
from baseclasses.wet_chemical_deposition import PrecursorSolution, SpinCoating, SpinCoatingRecipe, WetChemicalDeposition, SprayPyrolysis, BladeCoating
from baseclasses.material_processes_misc.quenching import AntiSolventQuenching
from baseclasses.helper.utilities import create_archive
from baseclasses import BaseProcess
from baseclasses.helper.utilities import get_entry_id_from_file_name

# Imports UMR
from ..suggestions_lists import *
from ..helper_functions import *
from ..categories import *

from ..umr_baseclasses import UMR_Layer
from ..batch import UMR_Batch
from ..solar_cell import UMR_InternalSolarCell
from ..umr_reference_classes import UMR_EntityReference

from ..processes.process_baseclasses import UMR_BaseProcess, UMR_ELNProcess, UMR_PrecursorSolution, UMR_SolarCellSettings


m_package = SchemaPackage(aliases=['UMR_schemas.characterization.blade_coating']) 




    
################################ Blade Coating ################################

class UMR_BladeCoatingProperties(ArchiveSection):
    
    blade_height = Quantity(
          type=np.float64,
        unit=('mm'),
        description = "The distance between surface and blade in mm",
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='mm'))

    blade_speed = Quantity(
        type=np.float64,
        unit=('mm/s'),
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='mm/s'))

    temperature = Quantity(
        type=np.float64,
        unit=('°C'),
        a_eln=dict(
            component='NumberEditQuantity',defaultDisplayUnit='°C'))



class UMR_BladeCoating(UMR_BaseProcess, BladeCoating, EntryData):
    m_def = Section(
        label_quantity = 'method',
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan',],
            properties=dict(
                order=[
                    'name', 'datetime', 'end_time', 'location', 
                    'batch', 'position_in_experimental_plan',
                    'description',
                    'solution',
                    'properties',
                    'layer',
                    'annealing',
                    'quenching',
                    'sintering'])))
    
    properties = SubSection(section_def=UMR_BladeCoatingProperties)
    
    # Wet chemical Deposition
    layer = SubSection(section_def=UMR_Layer, repeats=True)
    solution = SubSection(section_def=UMR_PrecursorSolution, repeats=True)
    

class UMR_BladeCoatingELN(UMR_ELNProcess, UMR_BladeCoating):
    m_def = Section(
        label="Blade Coating ELN",
        categories=[UMRSynthesisCategory],
        label_quantity = 'method',
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan',],
            properties=dict(
                order=[
                    'standard_process', 'load_standard_process',
                    'name', 'datetime', 'end_time', 'location', 
                    'description',
                    'batch', 'position_in_experimental_plan',
                    'use_current_datetime', 'create_solar_cells', 'execute_process_and_deposit_layer',
                    'solution',
                    'properties',
                    'layer',
                    'annealing',
                    'quenching',
                    'sintering',
                    'solar_cell_settings'])))
    
    standard_process = UMR_ELNProcess.standard_process.m_copy()
    standard_process.type = Reference(UMR_BladeCoating.m_def)

    #standard_process = Quantity(
    #    type=UMR_BladeCoating,
    #    description="Click on the Pencil to choose a Standard Process. Afterwards click 'Load Standard Process'. The ELN fields will be filled with the values from the chosen Standard Process.",
    #    a_eln=dict(component='ReferenceEditQuantity', showSectionLabel = False))

    
    def normalize(self, archive, logger):
            
        # BUTTON: Execute Process
        if self.execute_process_and_deposit_layer:
            self.execute_process_and_deposit_layer = False
            
            # Log error if no solar cell settings are given
            if self.create_solar_cells and not self.solar_cell_settings:
                log_error(self, logger, "If solar cells should be created please give the details in the subsection solar_cell_settings. Please also check if a sample was transferred to the sample subsection already and if so delete it there again.")
                return

            # Log error if no sample is chosen 
            if not self.selected_samples:
                log_error(self, logger, 'No Samples Selected. Please add the samples on which this process should be applied to the selected_samples section')
                return
            
            # Create Process and add it to sample entry 
            for sample_ref in self.selected_samples:
                process_entry = UMR_BladeCoating()
                sample_entry = add_process_and_layer_to_sample(self, archive, logger, sample_ref, process_entry)
                # return new sample enty with new process (because this is not yet saved in the referenced sample (sample_ref))
                    
                # Create Solar Cells
                if self.create_solar_cells:    
                    for solar_cell_name in self.solar_cell_settings.solar_cell_names:
                        solar_cell_entry = UMR_InternalSolarCell()
                        solar_cell_entry_id, solar_cell_entry = create_solar_cell_from_basic_sample(self, archive, logger, sample_entry, solar_cell_name, solar_cell_entry)
                        # Create references in batch and substrate
                        solar_cell_reference = UMR_EntityReference(
                            name = solar_cell_entry.name,
                            reference=get_reference(archive.metadata.upload_id, solar_cell_entry_id),
                            lab_id = solar_cell_entry.lab_id)
                        create_solar_cell_references(self, archive, logger, sample_ref, solar_cell_reference)

            # Empty selected_samples Section
            self.selected_samples = []
         
        super(UMR_BladeCoatingELN, self).normalize(archive, logger)   


m_package.__init_metainfo__()

