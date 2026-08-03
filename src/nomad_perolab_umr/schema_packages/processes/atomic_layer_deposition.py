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
from baseclasses.helper.utilities import rewrite_json

# Imports HZB
from baseclasses.vapour_based_deposition import AtomicLayerDeposition
from baseclasses.vapour_based_deposition.atomic_layer_deposition import ALDProperties, ALDMaterial
from nomad.datamodel.data import ArchiveSection, EntryData

# Imports Nomad
from nomad.metainfo import Quantity, Reference, SchemaPackage, Section, SubSection

from ..categories import *
from ..helper_functions import *
from ..processes.process_baseclasses import (
    UMR_BaseProcess,
    UMR_ELNProcess,
    UMR_PrecursorSolution,
)
from ..solar_cell import UMR_InternalSolarCell

from ..umr_synthesis_classes import UMR_ChemicalLot

# Imports UMR
from ..suggestions_lists import *
from ..umr_baseclasses import UMR_Layer
from ..umr_reference_classes import UMR_EntityReference

m_package = SchemaPackage() 


    
################################ Atomic Layer Deposition ################################


class UMR_ALDMaterial(ALDMaterial):
   m_def = Section(
        a_eln=dict(
            hide=['source', 'chemical_2'],
            properties=dict(
                order=[
                    'material_lot',
                    'manifold_temperature',
                    'bottle_temperature',
                    'pulse_flow_rate',
                    'pulse_duration',
                    'purge_flow_rate', 
                    'purge_duration',
                ]
            ),
        ),
    )

   material_lot = Quantity(
        type=Reference(UMR_ChemicalLot.m_def),
        a_eln=dict(component="ReferenceEditQuantity"))


class UMR_ALDProperties(ALDProperties):
    m_def = Section(
        a_eln=dict(
            hide=['source', 'chemical_2'],
            properties=dict(
                order=[
                    'temperature',
                    'door_temperature',
                    'temperature_hold_time',
                    'number_of_cycles',
                    'rate',
                    'time',
                    'thickness',
                ]
            ),
        ),
    )

    door_temperature = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0000146',
            'https://purl.archive.org/tfsco/TFSCO_00002111',
        ],
        type=np.dtype(np.float64),
        unit=('°C'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='°C'),
    )

    temperature_hold_time = Quantity(
        type=np.dtype(np.float64),
        unit=('s'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='s'),
        description = "The time for which the temperature was held in seconds before the process is started (Delay Time) in s",
    )


    material = SubSection(section_def=UMR_ALDMaterial)
    oxidizer_reducer = SubSection(section_def=UMR_ALDMaterial)


    def normalize(self, archive, logger):
        if self.material and self.material.material:
            if self.material.material.name:
                self.name = self.material.material.name

        if self.thickness:
            if self.name:
                self.name += ' ' + str(self.thickness)
            else:
                self.name = str(self.thickness)



class UMR_AtomicLayerDeposition(UMR_BaseProcess, AtomicLayerDeposition, EntryData):

    m_def = Section(
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan'],
            properties=dict(
                order=[
                    'name', 'datetime', 'end_time', 'location', 'operator',
                    'batch', 'position_in_experimental_plan',
                    'description',
                    'batch',
                    'method',
                    'properties',
                    'layer',
                    'selected_samples',
                    'atmosphere',
                    'steps',
                    'samples',
                    'instruments',
                ]
            ),
        )
    )

    properties = SubSection(section_def=UMR_ALDProperties)
    operator = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=suggestions_persons)),
    )



class UMR_AtomicLayerDepositionELN(UMR_ELNProcess, UMR_AtomicLayerDeposition):
    m_def = Section(
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan',
                  'create_solar_cells', 'solar_cell_settings', 'operator'],
            properties=dict(
                order=[
                        'standard_process', 'load_standard_process',
                        'name', 'datetime', 'end_time', 'location', 'operator',
                        'batch', 'position_in_experimental_plan',
                        'description',
                        'batch',
                        'method',
                        'properties',
                        'layer',
                        'selected_samples',
                        'atmosphere',
                        'steps',
                        'samples',
                        'instruments',
                ]
            ),
        )
    )

    def normalize(self, archive, logger):

            # BUTTON: execute Process
            if self.execute_process_and_deposit_layer:
                self.execute_process_and_deposit_layer = False
                rewrite_json(['data', 'execute_process_and_deposit_layer'], archive, False)

                # Create Process and add it to sample entry
                if self.selected_samples:
                    for sample_ref in self.selected_samples:
                        process_entry = UMR_AtomicLayerDeposition()
                        add_process_and_layer_to_sample(self, archive, logger, sample_ref, process_entry)
                    # Empty selected_samples Section
                    self.selected_samples = []
                else:
                    log_error(self, logger, 'No Samples Selected. Please add the samples on which this process should be applied to the selected_samples section')

            super().normalize(archive, logger)   


m_package.__init_metainfo__()
