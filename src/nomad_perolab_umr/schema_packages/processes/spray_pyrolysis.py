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
from baseclasses.helper.utilities import rewrite_json

# Imports UMR
from ..suggestions_lists import *
from ..helper_functions import *
from ..categories import *

from ..umr_baseclasses import UMR_Layer
from ..batch import UMR_Batch
from ..solar_cell import UMR_InternalSolarCell
from ..umr_reference_classes import UMR_EntityReference

from ..processes.process_baseclasses import UMR_BaseProcess, UMR_ELNProcess, UMR_PrecursorSolution, UMR_SolarCellSettings

m_package = SchemaPackage(aliases=['UMR_schemas.processes.spray_pyrolysis']) 


################################ Spray Pyrolysis ################################

class UMR_SprayPyrolysis(UMR_BaseProcess, SprayPyrolysis, EntryData):
    m_def = Section(
        label="Spray Pyrolysis ELN",
        label_quantity = 'method', 
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan',
                'create_solar_cells', 'solar_cell_settings'],
            properties=dict(
                order=[
                    'name', 'datetime', 'end_time', 'location', 
                    'batch', 'position_in_experimental_plan',
                    'description',
                    'layer',
                    'solution',
                    'properties',
                    'quenching',
                    'annealing',
                    'sintering'])))
    
    # Wet chemical Deposition
    layer = SubSection(section_def=UMR_Layer, repeats=True)
    solution = SubSection(section_def=UMR_PrecursorSolution, repeats=True)
        


class UMR_SprayPyrolysisELN(UMR_ELNProcess, UMR_SprayPyrolysis):
    m_def = Section(
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
                    'layer',
                    'solution',
                    'properties',
                    'quenching',
                    'annealing',
                    'sintering'])))
    
    standard_process = UMR_ELNProcess.standard_process.m_copy()
    standard_process.type = Reference(UMR_SprayPyrolysis.m_def)

    def normalize(self, archive, logger):
        
        # BUTTON: Execute Process
        if self.execute_process_and_deposit_layer:
            self.execute_process_and_deposit_layer = False
            rewrite_json(['data', 'execute_process_and_deposit_layer'], archive, False)

            
            # Create Process and add it to sample entry
            if self.selected_samples:
                for sample_ref in self.selected_samples:
                    process_entry = UMR_SprayPyrolysis()
                    add_process_and_layer_to_sample(self, archive, logger, sample_ref, process_entry)
                # Empty selected_samples Section
                self.selected_samples = []
            else:
                log_error(self, logger, 'No Samples Selected. Please add the samples on which this process should be applied to the selected_samples section')
                
        super(UMR_SprayPyrolysisELN, self).normalize(archive, logger)   



m_package.__init_metainfo__()
