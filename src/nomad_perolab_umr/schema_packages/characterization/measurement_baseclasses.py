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
from baseclasses import BaseMeasurement

# Imports HZB
from baseclasses.helper.utilities import get_encoding
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.basesections import Measurement
from nomad.datamodel.metainfo.plot import PlotSection

# Imports Nomad
from nomad.metainfo import (
    MEnum,
    Quantity,
    Section,
    SubSection,
)

from ..umr_reference_classes import UMR_EntityReference
from ..categories import *

# Imports UMR
from ..helper_functions import *

################################ MEASUREMENT BASECLASS ################################

# Class with general quantites which are needed for most Cicci measurements
class UMR_MeasurementBaseclass(ArchiveSection):
    '''General Section for Cicci Measurement.
    Other sections inherit from this Baseclass
    '''

    m_def = Section()
    
    data_file = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    
    user = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    solar_cell_was_referenced = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity'))

    measurement_data_was_extracted_from_data_file = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
    device = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))
    
    active_area = Quantity(
        type=np.float64,
        unit=('cm**2'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='cm**2'))
    
    temperature = Quantity(
        type=np.float64,
        unit=('°C'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='°C'))
    
    best_measurement = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
    # Helper variable to match JV Measurements to MPP Tracking or Stability Test Measureemnts
    directory = Quantity(type=str)

    samples = SubSection(
        section_def=UMR_EntityReference, repeats=True)
    

################################ TRACKING BASECLASS ################################

class UMR_TrackingData(ArchiveSection):
    '''Tracking Data Section for MPP Tracking, Stability Tracking and Connection Test'''

    m_def = Section()

    # Quantites for the Tracking Data from the the Cicci file
    time = Quantity(
        type=np.dtype(np.float64),
        description='Time array of the tracking measurement',
        shape=['*'],
        unit='s')

    voltage = Quantity(
        type=np.dtype(np.float64),
        description='Voltage array of the tracking measurement',
        shape=['*'],
        unit='V') 

    current_density = Quantity(
        type=np.dtype(np.float64),
        description='Current density array of the tracking measurement',
        shape=['*'],
        unit='mA/cm^2')

    power_density = Quantity(
        type=np.dtype(np.float64),
        description='Power density array of the MPP tracking measurement',
        shape=['*'],
        unit='mW/cm**2')
    
################################ PARAMETERS BASECLASS ################################

class UMR_JVParameters(UMR_MeasurementBaseclass, BaseMeasurement, EntryData, PlotSection):
    ''' General JV Parameters Class for StabilityParameters and MPPTrackingParameters'''

    m_def = Section(
        label_quantity="scan",
        categories=[UMRCollectionCategory])
    
    # Helper variable to match Parameters and Tracking measurements
    directory = Quantity(type=str)

    # Quantities from Stability (Parameters) Cicci file
    scan = Quantity(
        type=MEnum('Forward', 'Reverse'),
        shape=[],
        description='Forward or Reverse Scan.',
        a_eln=dict(component='EnumEditQuantity'),
    )
    
    time = Quantity(
        type=np.dtype(np.float64),
        description='Time array of the Stability Parameters measurement',
        shape=['*'],
        unit='hour')

    open_circuit_voltage = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        shape=['*'],
        description="Open circuit voltage."
    )

    short_circuit_current_density = Quantity(
        type=np.dtype(np.float64),
        unit='mA / cm**2',
        shape=['*'],
        description="Short circuit current density.",
    )

    fill_factor = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description="Fill factor."
    )

    efficiency = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description="Power conversion efficiency."
    )

    potential_at_maximum_power_point = Quantity(
        type=np.dtype(np.float64),
        unit='V',
        shape=['*'],
        description="The potential at the maximum power point, Vmp."
    )

    current_density_at_maximum_power_point = Quantity(
        type=np.dtype(np.float64),
        unit='mA / cm**2',
        shape=['*'],
        description="The current density at the maximum power point, *Jmp*."
    )

    power_at_maximum_power_point = Quantity(
        type=np.dtype(np.float64),
        unit='mW / cm**2',
        shape=['*'],
        description="The power density at the maximum power point, *Vmp*."
    )

    series_resistance_ohm = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        shape=['*'],
        description="The series resistance as extracted from the JV curve in Ohm."
    )

    shunt_resistance_ohm = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        shape=['*'],
        description="The shunt resistance as extracted from the JV curve in Ohm."
    )
    
    def normalize(self, archive, logger):
        #archive.metadata.entry_type = self.m_def.name

        
        # READ DATA FROM DATA FILE
        if self.data_file and not self.measurement_data_was_extracted_from_data_file:
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                log_info(self, logger, f"Normalize JV Parameters Measurement: Parse data from file: {f.name} | Encoding: {encoding}")
                from ..read_and_parse.general_parser import parse_general_info
                parse_general_info(self, f.name, encoding)
                from ..read_and_parse.parameters_parser import (
                    parse_parameters_data_to_archive,
                )
                parse_parameters_data_to_archive(self, f.name, encoding)
         
        # REFERENCE SAMPLE
        if self.data_file and not self.solar_cell_was_referenced:
            from ..read_and_parse.general_parser import reference_sample
            reference_sample(self, logger, archive)
 
        super().normalize(archive, logger)



class UMR_CollectedJVMeasurements(ArchiveSection):
    ''' Subsection for Collected JV Measurements'''

    jv_measurements= Quantity(
        type = Measurement,
        shape=['*'])
    
    def normalize(self, archive, logger):
        super().normalize(archive,logger)
        if self.jv_measurements:
            self.jv_measurements.sort(key=lambda x: x.datetime)
