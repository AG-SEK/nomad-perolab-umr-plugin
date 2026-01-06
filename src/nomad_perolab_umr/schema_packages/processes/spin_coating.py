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
from baseclasses.wet_chemical_deposition import SpinCoating
from nomad.datamodel.data import EntryData
from nomad.metainfo import (
    MEnum,
    Quantity,
    Reference,
    SchemaPackage,
    Section,
    SubSection,
)

from ..categories import *
from ..helper_functions import *
from ..processes.process_baseclasses import (
    UMR_BaseProcess,
    UMR_ELNProcess,
    UMR_PrecursorSolution,
)

# Imports UMR
from ..suggestions_lists import *
from ..umr_baseclasses import UMR_Layer

m_package = SchemaPackage(aliases=['UMR_schemas.processes.spin_coating']) 


################################ SpinCoating ################################

# OUTDATED - nicht mehr benötigt 
#class UMR_SpinCoating_Recipe(SpinCoatingRecipe, EntryData):
#    m_def = Section(
#        a_eln=dict(hide=['lab_id', 'users']),
#        categories=[UMRCreateCategory])


class UMR_SpinCoating(UMR_BaseProcess, SpinCoating, EntryData):
    m_def = Section(
        label_quantity = 'method',
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan', 'recipe'],
            properties=dict(
                order=[
                    'name', 'datetime', 'end_time', 'location', 'spin_coating_method',
                    'batch',
                    'description',
                    'position_in_experimental_plan',
                    'layer',
                    'solution',
                    'recipe_steps',
                    'quenching',
                    'annealing',
                    'sintering',
                    'samples',])))
    
    # Wet chemical Deposition
    layer = SubSection(section_def=UMR_Layer, repeats=True)
    solution = SubSection(section_def=UMR_PrecursorSolution, repeats=True)

    spin_coating_method = Quantity(
        type=MEnum(["Static", "Dynamic"]),
        description = 'The Spin Coating method used.',
        a_eln=dict(
            label="spin coating method",
            component='RadioEnumEditQuantity', # früher nur EnumEditQuantity
            props=dict(suggestions=["Static", "Dynamic"])))
    

class UMR_SpinCoatingELN(UMR_ELNProcess, UMR_SpinCoating):
    m_def = Section(
        label="Spin Coating ELN",
        categories=[UMRSynthesisCategory],
        label_quantity = 'method',
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan',
                  'create_solar_cells', 'solar_cell_settings', 'recipe'],
            properties=dict(
                order=[
                    'standard_process', 'load_standard_process',
                    'name', 'datetime', 'end_time', 'location', 
                    'spin_coating_method',
                    'description',
                    'batch', 'position_in_experimental_plan',
                    'use_current_datetime', 'execute_process_and_deposit_layer',
                    'layer',
                    'solution',
                    'recipe_steps',
                    'quenching',
                    'annealing',
                    'sintering',
                    'samples'])))
    
    standard_process = UMR_ELNProcess.standard_process.m_copy()
    standard_process.type = Reference(UMR_SpinCoating.m_def)

    def normalize(self, archive, logger):

        # Transfer Recipe Steps from recipe to SubSection (if Recipe is given)
        if not self.recipe_steps and self.recipe and self.recipe.steps:
            steps = [step for step in self.recipe.steps]
            self.recipe_steps = steps

        # BUTTON: execute Process
        if self.execute_process_and_deposit_layer:
            self.execute_process_and_deposit_layer = False
            rewrite_json(['data', 'execute_process_and_deposit_layer'], archive, False)

             # Create Process and add it to sample entry
            if self.selected_samples:
                for sample_ref in self.selected_samples:
                    process_entry = UMR_SpinCoating()
                    add_process_and_layer_to_sample(self, archive, logger, sample_ref, process_entry)
                # Empty selected_samples Section
                self.selected_samples = []
            else:
                log_error(self, logger, 'No Samples Selected. Please add the samples on which this process should be applied to the selected_samples section')

        super(UMR_SpinCoatingELN, self).normalize(archive, logger)   



m_package.__init_metainfo__()




