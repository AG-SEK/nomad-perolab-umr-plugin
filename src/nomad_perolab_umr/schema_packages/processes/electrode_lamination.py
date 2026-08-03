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
from baseclasses.wet_chemical_deposition import WetChemicalDeposition

# Imports HZB

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

from nomad.datamodel.metainfo.basesections import (
    PubChemPureSubstanceSection,
)

from .blade_coating import UMR_BladeCoatingProperties

from ..solar_cell import UMR_InternalSolarCell

from ..umr_synthesis_classes import UMR_ChemicalLot

# Imports UMR
from ..suggestions_lists import *
from ..umr_baseclasses import UMR_Layer
from ..umr_reference_classes import UMR_EntityReference

m_package = SchemaPackage() 



################################ ElectrodeLamination ################################

# Subsection for Electrode Preparation via Blade Coating 
class UMR_LaminationBladeCoatingProperties(UMR_BladeCoatingProperties):
    m_def = Section(
        a_eln=dict(
            properties=dict(
                order=['substrate_material', ' blade_height', 'blade_speed', 'temperature', 'gap_distance', 'gap_distance_unit', 'gap_distance_type'])))

    substrate_material = Quantity(
        type=str,
        description = "The material of the substrate on which the lamination was performed",
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_substrate_material)))
    

# Subsection for Electrode Preparation via Solvent Exchange
class UMR_SolventExchangeProperties(ArchiveSection):
    m_def = Section(
        a_eln=dict(
            properties=dict(order=['solvent_exchange_chemical', ' solvent_exchange_time', 'solvent_exchange_temperature'])))


    solvent_exchange_temperature = Quantity(
        type=np.float64,
        unit=('°C'),
        description = "The temperature at which the solvent exchange was performed in °C",
        a_eln=dict(component='NumberEditQuantity'), defaultDisplayUnit="°C")

    solvent_exchange_time = Quantity(
        type=np.float64,
        unit=('s'),
        description = "The time for which the solvent exchange was performed in seconds",
        a_eln=dict(component='NumberEditQuantity'), defaultDisplayUnit="minutes")

    solvent_exchange_chemical = Quantity(
        type=Reference(UMR_ChemicalLot.m_def),
        a_eln=dict(
            label='Solvent Exchange Chemical (Lot)',
            component='ReferenceEditQuantity'))

    solvent_exchange_chemical_2 = SubSection(
        section_def=PubChemPureSubstanceSection,
        label="Chemical PubChem")


# Subsection for Electrode Lamination
class UMR_ElectrodeLaminationProperties(ArchiveSection):
    # Electrode Lamination
    lamination_temperature = Quantity(
        type=np.float64,
        unit=('°C'),
        description = "The temperature at which the lamination was performed in °C",
        a_eln=dict(component='NumberEditQuantity'), defaultDisplayUnit="°C")

    lamination_pressure = Quantity(
        type=np.float64,
        unit=('Pa'),
        description = "The pressure at which the lamination was performed in bar",
        a_eln=dict(component='NumberEditQuantity'), defaultDisplayUnit="bar")

    lamination_time = Quantity(
        type=np.float64,
        unit=('s'),
        description = "The time for which the lamination was performed in seconds",
        a_eln=dict(component='NumberEditQuantity'), defaultDisplayUnit="minutes")
    

# Main class for Electrode Lamination Process
class UMR_ElectrodeLamination(UMR_BaseProcess, WetChemicalDeposition, EntryData):
    m_def = Section(
        label_quantity = 'method',
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan', "quenching"],
            properties=dict(
                order=[
                    'name', 'datetime', 'end_time', 'location', 'operator', 
                    'batch', 'position_in_experimental_plan',
                    'description',
                    'blade_coating_properties',
                    'solvent_exchange_properties',
                    'lamination_properties',
                    'solution',
                    'properties',
                    'layer',
                    'annealing',
                    #'quenching',
                    'sintering',
                    'instruments'])))

    blade_coating_properties = SubSection(section_def=UMR_LaminationBladeCoatingProperties)
    solvent_exchange_properties = SubSection(section_def=UMR_SolventExchangeProperties)
    lamination_properties = SubSection(section_def=UMR_ElectrodeLaminationProperties)
    

    # Wet chemical Deposition
    layer = SubSection(section_def=UMR_Layer, repeats=True)
    solution = SubSection(section_def=UMR_PrecursorSolution, repeats=True)
    operator = Quantity(
        type=str,
        a_eln=dict(component='EnumEditQuantity', props=dict(suggestions=suggestions_persons)),
    )


    def normalize(self, archive, logger):
        self.method = 'Electrode Lamination'
        super().normalize(archive, logger)

        
class UMR_ElectrodeLaminationELN(UMR_ELNProcess, UMR_ElectrodeLamination):
    m_def = Section(
        label="Electrode Lamination ELN",
        categories=[UMRSynthesisCategory],
        label_quantity = 'method',
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan', "quenching"],
            properties=dict(
                order=[
                    'standard_process', 'load_standard_process',
                    'name', 'datetime', 'end_time', 'location', 'operator',
                    'description',
                    'batch', 'position_in_experimental_plan',
                    'use_current_datetime', 'create_solar_cells', 'execute_process_and_deposit_layer',
                    'solar_cell_settings',
                    'blade_coating_properties',
                    'solvent_exchange_properties',
                    'lamination_properties',
                    'solution',
                    'properties',
                    'layer',
                    'annealing',
                    #'quenching',
                    'sintering',
                    'instruments',
                    ])))
    
    standard_process = UMR_ELNProcess.standard_process.m_copy()
    standard_process.type = Reference(UMR_ElectrodeLamination.m_def)

    
    def normalize(self, archive, logger):
            
        # BUTTON: Execute Process
        if self.execute_process_and_deposit_layer:
            self.execute_process_and_deposit_layer = False
            rewrite_json(['data', 'execute_process_and_deposit_layer'], archive, False)

            
            # Log error if no solar cell settings are given
            if self.create_solar_cells and not self.solar_cell_settings:
                log_error(self, logger, "If solar cells should be created please give the details in the subsection solar_cell_settings. Please also check if a sample was transferred to the sample subsection already and if so delete it there again.")
                return

            # Log error if no sample is chosen 
            if not self.selected_samples:
                log_error(self, logger, 'No Samples Selected. Please add the samples on which this process should be applied to the selected_samples section')
                return
            
            # PERFORMANCE OPTIMIZATION: Collect all updates and save once at the end
            samples_to_save = {}  # {mainfile: sample_entry}
            batches_to_save = {}  # {mainfile: batch_entry}
            substrates_to_save = {}  # {mainfile: substrate_entry}
            
            # Create Process and add it to sample entry 
            for sample_ref in self.selected_samples:
                process_entry = UMR_ElectrodeLamination()
                sample_entry, mainfile = add_process_and_layer_to_sample(self, archive, logger, sample_ref, process_entry)
                # Collect sample for later batch save
                samples_to_save[mainfile] = sample_entry

                list_solar_cell_references=[]
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
                        list_solar_cell_references.append(solar_cell_reference)
                    
                    # Collect batch and substrate updates (don't save yet)
                    batch, batch_mainfile, substrate, substrate_mainfile = create_solar_cell_references(
                        self, archive, logger, sample_ref, list_solar_cell_references
                    )
                    
                    # Collect for batched save (use latest version if multiple samples reference same batch/substrate)
                    if batch and batch_mainfile:
                        batches_to_save[batch_mainfile] = batch
                    if substrate and substrate_mainfile:
                        substrates_to_save[substrate_mainfile] = substrate

            # PERFORMANCE: Save all updated entries at once (batched I/O)
            for mainfile, sample_entry in samples_to_save.items():
                create_archive(sample_entry, archive, mainfile, overwrite=True)
            for mainfile, batch_entry in batches_to_save.items():
                create_archive(batch_entry, archive, mainfile, overwrite=True)
            for mainfile, substrate_entry in substrates_to_save.items():
                create_archive(substrate_entry, archive, mainfile, overwrite=True)

            # Empty selected_samples Section
            self.selected_samples = []
         
        super().normalize(archive, logger)   


m_package.__init_metainfo__()