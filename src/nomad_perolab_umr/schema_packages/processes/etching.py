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

import numpy as np
from baseclasses import BaseProcess
from baseclasses.helper.utilities import rewrite_json
from baseclasses.wet_chemical_deposition import PrecursorSolution
from nomad.datamodel.data import ArchiveSection
from nomad.metainfo import Quantity, Reference, SchemaPackage, Section, SubSection

from ..umr_baseclasses import UMR_Layer

m_package = SchemaPackage() 

class EtchingProperties(ArchiveSection):


    duration = Quantity(
        type=np.dtype(np.float64),
        unit=('second'),
        description="Duration of the etching process",
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='minute',
            props=dict(minValue=0),
        ),
    )

    etch_rate = Quantity(
        type=np.dtype(np.float64),
        unit=('m/s'),
        description="Duration of the etching process",
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='nm/minute',
            props=dict(minValue=0),
        ),
    )


    temperature = Quantity(
        type=np.dtype(np.float64),
        unit=('°C'),
        description="Temperature during etching",
        a_eln=dict(component='NumberEditQuantity',
        defaultDisplayUnit='°C'),
    )

    mask_material = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=['Polyamide Tape']))
    )



class BaseEtchingShape(ArchiveSection):
    """Base class for etching of a sample"""

class SideEtchingShape(BaseEtchingShape):
    """Base class for etching of a sample from the sides"""
   
    side_etch_top = Quantity(
        type=np.dtype(np.float64),
        unit=('m'),
        description="Lateral etch offset on top edge.",
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
    )

    side_etch_bottom = Quantity(
        type=np.dtype(np.float64),
        unit=('m'),
        description="Lateral etch offset on bottom edge.",
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
    )

    
    side_etch_left = Quantity(
        type=np.dtype(np.float64),
        unit=('m'),
        description="Lateral etch offset on left edge.",
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
    )

    
    side_etch_right = Quantity(
        type=np.dtype(np.float64),
        unit=('m'),
        description="Lateral etch offset on right edge.",
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mm',
            props=dict(minValue=0),
        ),
    )

    
class EtchedLayer(UMR_Layer):
    """class for Subsection etched_layers"""
    m_def = Section(
        label_quantity='layer_type',
        a_eln=dict(
            hide=['structuring', 'deposition_method'],
            properties=dict(
                order=['layer_name', 
                       'layer_type','layer_material_name',
                       'thickness',
                       'position_in_layer_stack']))
    )



class Etching(BaseProcess):
    """Base class for etching of a sample"""

   # m_def = Section(
   #     a_eln=dict(
            #hide=['lab_id', 'user', 'author'],
   #         properties=dict(
   #             order=[])),
   # )


    etchant = SubSection(
        section_def=PrecursorSolution,
        repeats=True,
    )

    etched_layers = SubSection(
        section_def=EtchedLayer,
        repeats=True,
    )

    shape = SubSection(section_def = BaseEtchingShape)
    properties = SubSection(section_def=EtchingProperties)
    

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        self.method = 'Etching'



from nomad.datamodel.data import EntryData

from ..categories import *
from ..helper_functions import *
from ..processes.process_baseclasses import (
    UMR_BaseProcess,
    UMR_ELNProcess,
    UMR_PrecursorSolution,
)


class UMR_Etching(UMR_BaseProcess, Etching, EntryData):
     #m_def = Section(
        #a_eln=dict(
            #hide=['present', 'lab_id', 'positon_in_experimental_plan', 'recipe'],
            #properties=dict(
            #    order=[
            #        'name', 'datetime', 'end_time', 'location', 'spin_coating_method',
            #        'batch',
            #        'description',
            #        'position_in_experimental_plan',
            #       'layer',
            #        'solution',
            #        'recipe_steps',
            #        'quenching',
            #        'annealing',
            #        'sintering',
            #        'samples',])))


    # Wet chemical Deposition
    etchant = SubSection(section_def=UMR_PrecursorSolution, repeats=True)
  

class UMR_EtchingELN(UMR_ELNProcess, UMR_Etching):
    m_def = Section(
        label="Etching ELN",
        categories=[UMRSynthesisCategory],
        label_quantity = 'method',
        #a_eln=dict(
        #    hide=['present', 'lab_id', 'positon_in_experimental_plan',
        #          'create_solar_cells', 'solar_cell_settings', 'recipe'],
        #    properties=dict(
        #        order=[
        #            'standard_process', 'load_standard_process',
        #            'name', 'datetime', 'end_time', 'location', 
        #            'spin_coating_method',
        #            'description',
        #            'batch', 'position_in_experimental_plan',
        #            'use_current_datetime', 'execute_process_and_deposit_layer',
        #            'layer',
        #            'solution',
        #            'recipe_steps',
        #            'quenching',
        #            'annealing',
        #            'sintering',
        #            'samples']))
        )
    
    standard_process = UMR_ELNProcess.standard_process.m_copy()
    standard_process.type = Reference(UMR_Etching.m_def)

    def normalize(self, archive, logger):

        # BUTTON: execute Process
        if self.execute_process_and_deposit_layer:
            self.execute_process_and_deposit_layer = False
            rewrite_json(['data', 'execute_process_and_deposit_layer'], archive, False)

             # Create Process and add it to sample entry
            if self.selected_samples:
                for sample_ref in self.selected_samples:
                    process_entry = UMR_Etching()
                    add_process_and_layer_to_sample(self, archive, logger, sample_ref, process_entry)
                # Empty selected_samples Section
                self.selected_samples = []
            else:
                log_error(self, logger, 'No Samples Selected. Please add the samples on which this process should be applied to the selected_samples section')

        super(UMR_EtchingELN, self).normalize(archive, logger)   




m_package.__init_metainfo__()
