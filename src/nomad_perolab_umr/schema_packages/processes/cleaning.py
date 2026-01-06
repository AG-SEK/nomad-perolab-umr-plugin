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

# Imports Nomad
from baseclasses.helper.utilities import rewrite_json

# Imports HZB
from baseclasses.material_processes_misc import (
    Cleaning,
    PlasmaCleaning,
    SolutionCleaning,
    UVCleaning,
)
from nomad.datamodel.data import EntryData
from nomad.metainfo import Quantity, Reference, SchemaPackage, Section, SubSection

from ..categories import *
from ..helper_functions import *
from ..processes.process_baseclasses import UMR_BaseProcess, UMR_ELNProcess

# Imports UMR
from ..suggestions_lists import *
from ..umr_synthesis_classes import UMR_ChemicalLot

m_package = SchemaPackage(aliases=['UMR_schemas.processes.cleaning']) 

################################ Cleaning ################################



class UMR_SolutionCleaning(SolutionCleaning):
    m_def = Section(
        label_quantity = 'name',       
        a_eln=dict(
            overview=True,
            label = "Solution Cleaning",
            properties=dict(
                order=['solvent', 'time', 'temperature'])
            ))
  
    solvent = Quantity(
        links = ['https://purl.archive.org/tfsco/TFSCO_00000026'],  #Link to ontology class 'solvent'
        type=UMR_ChemicalLot,
        a_eln=dict(component='ReferenceEditQuantity'))
    
    lab_id = Quantity(type=str)

    ultrasonic_cleaning = Quantity(
        type=bool,
        default=True,
        a_eln=dict(component='BoolEditQuantity'))
    
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(component='RichTextEditQuantity'),
    )




    def normalize(self, archive, logger):
        super().normalize(archive, logger)
        if self.solvent:
            self.lab_id = self.solvent.lab_id
            if self.solvent.chemical.pure_substance:
                self.solvent_2 = self.solvent.chemical.pure_substance.m_copy(deep=True)
            else:
                log_warning(self, logger, f"The Pure Substance Section for the chemical {self.solvent.chemical.short_name} could not be added, becasue the section does not exist for this chemical")



class UMR_UVCleaning(UVCleaning):
    m_def = Section(
        a_eln=dict(
            overview=True,
            label = "UVO Cleaning",
            #properties=dict(order=['time', 'pressure'])
            ))

class UMR_Cleaning(UMR_BaseProcess, Cleaning, EntryData):
    m_def = Section(
        label_quantity = 'method',       
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan',],
            properties=dict(
                order=[
                    'name', 'datetime', 'end_time', 'location', 
                    'batch', '',
                    'description',  
                    'position_in_experimental_plan', 
                    'cleaning', 'cleaning_uv', 'cleaning_plasma',
                    'samples'])))

    cleaning = SubSection(section_def=UMR_SolutionCleaning, repeats=True)
    cleaning_uv = SubSection(section_def=UMR_UVCleaning, repeats=True)
    cleaning_plasma = SubSection(section_def=PlasmaCleaning, repeats=True)
    

class UMR_CleaningELN(UMR_ELNProcess, UMR_Cleaning):
    m_def = Section(
        label="Cleaning ELN",
        categories=[UMRSynthesisCategory],
        label_quantity = 'method',
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan',
                  'create_solar_cells', 'solar_cell_settings'],
            properties=dict(
                order=[
                    'standard_process', 'load_standard_process',
                    'name', 'datetime', 'end_time', 'location', 
                    'description',
                    'batch', 'position_in_experimental_plan',
                    'use_current_datetime', 'execute_process_and_deposit_layer',
                    'cleaning', 'cleaning_uv', 'cleaning_plasma',
                    'samples'])))
    
    standard_process = UMR_ELNProcess.standard_process.m_copy()
    standard_process.type = Reference(UMR_Cleaning.m_def)

    def normalize(self, archive, logger):

        # Set method
        if self.cleaning_uv:
            self.method = "UV Cleaning"
        elif self.cleaning_plasma:
            self.method = "Plasma Cleaning"

        # BUTTON: execute Process
        if self.execute_process_and_deposit_layer:
            self.execute_process_and_deposit_layer = False
            rewrite_json(['data', 'execute_process_and_deposit_layer'], archive, False)
            
            # Create Process and add it to sample entry
            if self.selected_samples:
                for sample_ref in self.selected_samples:
                    process_entry = UMR_Cleaning()
                    add_process_and_layer_to_sample(self, archive, logger, sample_ref, process_entry)
                # Empty selected_samples Section
                self.selected_samples = []
            else:
                log_error(self, logger, 'No Samples Selected. Please add the samples on which this process should be applied to the selected_samples section')

        super().normalize(archive, logger)   




m_package.__init_metainfo__()


