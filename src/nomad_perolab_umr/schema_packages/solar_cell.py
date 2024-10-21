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

# Imports Nomad
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.metainfo import Reference, Quantity, SubSection, Section, Package, MEnum, SchemaPackage
from nomad.datamodel.metainfo.basesections import Measurement, Process


# Imports HZB/Michael Götte
from baseclasses.solar_energy import SolcarCellSample
from baseclasses.helper.utilities import get_reference

# Imports UMR
from .suggestions_lists import *
from .helper_functions import *
from .categories import *

from .umr_baseclasses import UMR_Layer, UMR_MeasurementsSubsection
from .substrate import UMR_Substrate
from .batch import UMR_Batch


m_package = SchemaPackage() 


################################ BASIC SAMPLE ################################

class UMR_BasicSample(SolcarCellSample):  # inherit from SolcarCellSample, because of normalize functions for laye stack
    m_def = Section(
        categories=[UMRCollectionCategory],
        label='Basic Sample',
        label_quantity = 'lab_id',
        a_eln=dict(
            hide=['components', 'elemental_composition','sample_id'],
            properties=dict(
                order=[
                    'name', 'datetime', 'lab_id',
                    'batch', 'group_number', 'substrate',
                    'supplier',
                    'area','width','length',
                    'description',
                    'device_names'])))
    
    batch = Quantity(
        type=Reference(UMR_Batch.m_def),
        a_eln=dict(component='ReferenceEditQuantity', showSectionLabel=True))
    
    substrate = Quantity(
        type=Reference(UMR_Substrate.m_def),
        a_eln=dict(component='ReferenceEditQuantity', showSectionLabel=True))
    
    group_number = Quantity(
        type=int,
        a_eln=dict(component='NumberEditQuantity'))
    
    area = Quantity(
        type=np.dtype(np.float64),
        description='The area is filled in automatically if length and width are given',
        unit='cm**2',
        a_eln=dict(component='NumberEditQuantity'))
 
    width = Quantity(
        type=np.dtype(np.float64),
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
 
    length = Quantity(
        type=np.dtype(np.float64),
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    group_number = Quantity(
        type=int,
        a_eln=dict(component='NumberEditQuantity'))
 
    architecture = Quantity(
        type = MEnum(suggestions_architecture),
        #type=str,
        description = 'The architecture of the device',
        a_eln=dict(
            label='architecture',
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_architecture)))
 
    encapsulation = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_encapsulation)))  
    

    # SubSections
    layers = SubSection(section_def=UMR_Layer, repeats=True,)
    measurements = SubSection(section_def = UMR_MeasurementsSubsection)
    processes = SubSection(section_def=Process, repeats=True)


    #other_device_names = SubSection(section_def=UMR_DeviceName, repeats=True)
    


    def normalize(self, archive, logger):
        super(UMR_BasicSample, self).normalize(archive,logger)

        #self.processes_ref = UMR_ProcessesSubsection()

        # Calculate the solar cell area
        if self.width and self.length:
            self.area = self.width * self.length

        # CREATE MEASUREMENTS SUBSECTION
        if not self.measurements:
            self.measurements = UMR_MeasurementsSubsection()
        # COLLECT MEASUREMENTS
        self.measurements.jv_measurements = collect_referencing_entries(self, archive, logger, "UMR_JVMeasurement")
        self.measurements.eqe_measurements = collect_referencing_entries(self, archive, logger, "UMR_EQEMeasurement")
        self.measurements.stability_measurements = collect_referencing_entries(self, archive, logger, "UMR_StabilityTest")
        self.measurements.mppt_measurements = collect_referencing_entries(self, archive, logger, "UMR_MPPTracking")
        self.measurements.other_measurements = collect_referencing_entries(self, archive, logger, ['UMR_StabilizedOpenCircuitVoltage','UMR_StabilizedShortCircuitCurrent', 'UMR_ConnectionTest'])

        # SORT MEASUREMENTS
        self.measurements.jv_measurements = sorted(self.measurements.jv_measurements, key=lambda x: x.datetime)
        self.measurements.eqe_measurements = sorted(self.measurements.eqe_measurements, key=lambda x: x.datetime)
        self.measurements.stability_measurements = sorted(self.measurements.stability_measurements, key=lambda x: x.datetime)
        self.measurements.mppt_measurements = sorted(self.measurements.mppt_measurements, key=lambda x: x.datetime)
        self.measurements.other_measurements = sorted(self.measurements.other_measurements, key=lambda x: x.datetime)
        
        # NOTE: Sorting the list directly does not work
        # self.measurements.jv_measurements.sort(key=lambda x: x.datetime) # does not work
        
        # Check for best measurements (in UMR_MeasurementSubsection normalizer)
        self.measurements.normalize(archive, logger)

        # COLLECT PROCESSES
        #list_processes = ['UMR_SpinCoating', 'UMR_Cleaning', 'UMR_BladeCoating', 'UMR_SprayPyrolysis']
        #self.processes_ref.processes = collect_referencing_entries(self, archive, logger, list_processes)

   

################################ SOLAR CELL ################################

class UMR_ExternalSolarCell(UMR_BasicSample, EntryData):
    m_def = Section(
        categories=[UMRCollectionCategory],
        label='External Solar Cell',
        label_quantity = 'lab_id',
        a_eln=dict(
            hide=['components', 'elemental_composition','sample_id', 'processes'],
            properties=dict(
                order=[
                    'name', 'datetime', 'lab_id', 'supplier',
                    'batch', 'group_number', 'substrate',
                    'architecture', 'encapsulation',
                    'area','width','length',
                    'description'])))
  
    supplier = Quantity(
        type=MEnum(suggestions_supplier),
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_supplier)))
    
    def normalize(self, archive, logger):
        super(UMR_ExternalSolarCell, self).normalize(archive,logger)
        


class UMR_InternalSolarCell(UMR_BasicSample, EntryData):
    m_def = Section(
        categories=[UMRCollectionCategory],
        label='Internal Solar Cell',
        label_quantity = 'lab_id',
        a_eln=dict(
            hide=['users', 'components', 'elemental_composition'],
                properties=dict(
                order=[
                    'name', 'datetime', 'lab_id',
                    'batch', 'group_number', 'substrate',
                    'architecture', 'encapsulation',
                    'area','width','length',
                    'description',
                    'device_names'])))
 

    
    def normalize(self, archive, logger):
        #collectMeasurements(self, archive)
        super(UMR_InternalSolarCell, self).normalize(archive, logger)
        
        # Sort Processes
        #process_list = [process for process in self.processes]
        #process_list.sort(key=lambda x: x.position_in_experimental_plan)
        #self.processes = process_list

        #self.layers = []
        #for process in self.processes:
        #    if hasattr(process, 'layer'):
        #        self.layers.append(process.layer)
        #for layer in self.layers:
        #    layer.normalize(archive, logger)


m_package.__init_metainfo__()