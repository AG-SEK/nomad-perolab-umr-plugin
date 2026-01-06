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
from baseclasses import BaseProcess
from baseclasses.helper.utilities import rewrite_json

# Imports HZB
from baseclasses.material_processes_misc import (
    Annealing,
    UVCleaning,
)
from baseclasses.material_processes_misc.quenching import AntiSolventQuenching
from baseclasses.wet_chemical_deposition import (
    PrecursorSolution,
)
from nomad.datamodel.data import ArchiveSection, EntryData

# Imports Nomad
from nomad.metainfo import Quantity, SchemaPackage, Section, SubSection

from ..batch import UMR_Batch
from ..categories import *
from ..helper_functions import *

# Imports UMR
from ..suggestions_lists import *
from ..umr_reference_classes import UMR_EntityReference, UMR_InstrumentReference
from ..umr_synthesis_classes import UMR_ChemicalLot, UMR_Solution

#m_package = Package() 
m_package = SchemaPackage(aliases=['UMR_schemas.processes.process_baseclasses']) 


class UMR_SolarCellSettings(ArchiveSection):
    m_def = Section(
        a_eln=dict(
            hide=[],
            properties=dict(
                order=[
                    "name",
                    "architecture",
                    "encapsulation",
                    "substrate",
                    "processes",
                    'description',
                    'number_of_solar_cells_on_substrate',
                    'solar_cell_names',
                    'area',
                    'length',
                    'width',
                ])))
       
    number_of_solar_cells_on_substrate= Quantity(
        type=int,
        default = 4,
        a_eln=dict(component='NumberEditQuantity'))
    
    solar_cell_names = Quantity(   
        type=str,
        default = ['A', 'B', 'C', 'D'],
        description='Names of the solar cells, like 1,2,3,4 or A,B,C,D',
        shape=['number_of_solar_cells_on_substrate'],
        a_eln=dict(component='StringEditQuantity'))
    
    area = Quantity(
        type=np.float64,
        unit='cm**2',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm**2'))

    length = Quantity(
        type=np.float64,
        default = 0.6,
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    width = Quantity(
        type=np.float64,
        default = 0.6,
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    architecture = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_architecture)))
    

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

        # Calculate the solar cell area
        if self.width and self.length:
            self.area = self.width * self.length



class UMR_PrecursorSolution(PrecursorSolution):
    m_def = Section(
        links=['https://purl.archive.org/tfsco/TFSCO_00001081'],       # Link to ontology class 'precursor solution'
        label_quantity='name')  

    solution = Quantity(
        type=UMR_Solution,
        a_eln=dict(component='ReferenceEditQuantity'))
    

    #solution_details = SubSection(section_def=UMR_Solution)
    # GGF. DIE SUBSECTION VON DER SOLUTION DETAILS ANZUPASSEN
    ##################################################
    

    def normalize(self, archive, logger):
        super().normalize(archive, logger) 
        #if self.solution:
        #    self.solution_details = self.solution.m_copy(deep=True)


class UMR_BaseProcess(BaseProcess):

    position_in_experimental_plan = Quantity(
        type=int,
        a_eln=dict(component='NumberEditQuantity'))

    location = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=sugggestions_locations)))
    
    batch = Quantity(
        description="The batch to which this procses belongs.",
        type=UMR_Batch,
        #a_eln=dict(component='ReferenceEditQuantity')
        )
    
    samples = SubSection(
        section_def=UMR_EntityReference,
        description="""
        The samples as that have undergone the process.
        """,
        repeats=True,
    )

    instruments = SubSection(section_def=UMR_InstrumentReference, repeats=True)

    def normalize(self, archive, logger):
        
        # Delete batch temporarily so that normalize function in BaseProcess does not set the samples new
        batch_temp = self.batch
        self.batch = None
        super().normalize(archive, logger) 
        self.batch = batch_temp
    
# TODO: Ask Micha to add (if self.batch.entities condition in baseclasses init.py line 275)
    


class UMR_ELNProcess(EntryData, ArchiveSection):
    m_def = Section(
        description="This is the Base ELN Section for ELN Processes. Please choose the desired ELN Process from the Dropdown List. Afterwards either load a 'standard_process' or enter the parameters for a new processes manually.",
        label_quantity = 'name',
        a_eln=dict(
            hide=['standard_process', 'load_standard_process', 'use_current_datetime','create_solar_cells', 'execute_process_and_deposit_layer', 'selected_samples','solar_cell_settings']))

    standard_process = Quantity(
        type=UMR_BaseProcess,
        #description="Click on the Pencil to choose a Standard Process. Afterwards click 'Load Standard Process'. The ELN fields will be filled with the values from the chosen Standard Process.",
        a_eln=dict(component='ReferenceEditQuantity', showSectionLabel = False))

    load_standard_process = Quantity(
        type=bool,
        description="Click on the Pencil to choose a Standard Process. Afterwards click 'Load Standard Process'. The ELN fields will be filled with the values from the chosen Standard Process.",
        default=False,
        a_eln=dict(component='ActionEditQuantity'))
    
    use_current_datetime = Quantity(
        type=bool,
        default=True,
        a_eln=dict(component='BoolEditQuantity'))
    
    create_solar_cells = Quantity(
        type=bool,
        default=True,
        a_eln=dict(component='BoolEditQuantity'))

    execute_process_and_deposit_layer = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ActionEditQuantity'))

    selected_samples = SubSection(section_def=UMR_EntityReference, repeats=True)
    solar_cell_settings = SubSection(section_def=UMR_SolarCellSettings)

    def normalize(self, archive, logger):
        super().normalize(archive, logger)  

        # Sort Samples and Selected Samples List
        if hasattr(self, 'samples') and self.samples:
            self.samples = sort_and_deduplicate_subsection(self.samples)
        if hasattr(self, 'selected_samples') and self.selected_samples:
            self.selected_samples = sort_and_deduplicate_subsection(self.selected_samples)

        # BUTTON: load standard process
        if self.load_standard_process and self.standard_process:
            self.load_standard_process = False
            rewrite_json(['data', 'load_standard_process'], archive, False)

            
            # Update entry with data from standard process
            self.m_update_from_dict(self.standard_process.m_to_dict())
            if self.m_parent:
                self.datetime = self.m_parent.datetime
                #self.position_in_experimental_plan = self.m_parent_index
            else:
                self.datetime = None


            
            



#class UMR_WetChemicalDepositionBaseclass(ArchiveSection):
#    layer = SubSection(section_def=UMR_Layer, repeats=True)
#    solution = SubSection(section_def=UMR_PrecursorSolution, repeats=True)
# Das hat nicht geklappt mit dieser Klasse als Klasse die ich erbe. Der normalize von UMR_Layer wurde dann nicht ausgeführt.



################################ UV Annealing (for annealing subsection) ################################

class UMR_UVAnnealing(UVCleaning, Annealing, EntryData):
    '''Section for Annealing SubSection'''
    m_def = Section(categories=[UMRCollectionCategory])

    uv_annealing = Quantity(
        type=bool,
        default = True,
    )
    #time, pressure, temperature



class UMR_SpinCoatingAntiSolventQuenching(AntiSolventQuenching):
    '''Section for Quenching SubSection'''

    anti_solvent = Quantity(
        type=UMR_ChemicalLot,
        a_eln=dict(component='ReferenceEditQuantity'))    
    
    lab_id = Quantity(type =str)

    def normalize(self, archive, logger):
        super().normalize(archive, logger) 
        if self.anti_solvent:
            self.anti_solvent_2 = self.anti_solvent.chemical.pure_substance.m_copy(deep=True)
            self.lab_id = self.anti_solvent.lab_id


m_package.__init_metainfo__()




