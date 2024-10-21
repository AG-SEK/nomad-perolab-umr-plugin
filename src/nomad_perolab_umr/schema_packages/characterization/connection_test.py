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

### Measurement classes, like JV measurement, EQE measurement


# Imports Python
import numpy as np
import os
import plotly.graph_objects as go


# Imports Nomad
from nomad.datamodel.metainfo.plot import PlotSection, PlotlyFigure
from nomad.metainfo import MEnum, Quantity, SubSection, Section, SchemaPackage 
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import BaseSection

# Imports HZB
from baseclasses.helper.utilities import get_encoding

from baseclasses import BaseMeasurement # TODO

# Imports UMR
from .measurement_baseclasses import UMR_MeasurementBaseclass, UMR_TrackingData
from ..categories import *
from ..helper_functions import *

m_package = SchemaPackage() 

################################ CONNECTION TEST - FOR STABILIZED VOC AND JSC ################################

class UMR_ConnectionTestTrackingData(UMR_TrackingData):
    '''Tracking Data Section for Connection Test'''

    m_def = Section(
        a_eln=dict(
            hide=['power_density']))
    

class UMR_ConnectionTestExtraData(UMR_MeasurementBaseclass, BaseMeasurement, BaseSection, EntryData):
    
    m_def = Section(
        a_eln=dict(
            hide=['lab_id', 'description',
                  'name', 'user', 'device', 'datetime', 'directory',
                  'location', 'active_area','best_measurement',
                  'results', 'instruments', 'atmosphere', 'steps', 'method'],
            properties=dict(
                order=[
                    'scan',
                    'data_file', 'measurement_data_was_extracted_from_data_file', 'solar_cell_was_referenced',
                    ])))
    # Quantites for the Tracking Data from the the Cicci file
    time = Quantity(
        type=np.dtype(np.float64),
        description='Time array of the Connection Test Extra  measurement',
        shape=['*'],
        unit='s')
    
    temperature = Quantity(
        type=np.dtype(np.float64),
        description='Temperature array of the Connection Test Extra measurement',
        shape=['*'],
        unit='°C')
    

    def normalize(self, archive, logger):

        # READ DATA FROM DATA FILE
        if self.data_file and not self.measurement_data_was_extracted_from_data_file:
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                log_info(self, logger, f"Normalize Connection Test Measurement: Parse data from file: {f.name} | Encoding: {encoding}")
                from ..read_and_parse.general_parser import parse_general_info          
                parse_general_info(self, f.name, encoding)
                from ..read_and_parse.connection_test_extra_parser import parse_connectionTestExtra_data_to_archive
                parse_connectionTestExtra_data_to_archive(self, f.name, encoding)
        
        # REFERENCE SAMPLE
        if self.data_file and not self.solar_cell_was_referenced:
            from ..read_and_parse.general_parser import reference_sample          
            reference_sample(self, logger, archive)
        
        super(UMR_ConnectionTestExtraData, self).normalize(archive, logger)



class UMR_ConnectionTest(UMR_MeasurementBaseclass, BaseMeasurement, PlotSection, EntryData):
    '''Base Section for all sorts of Connection Tests'''

    m_def = Section(
        label = "Connection Test",
        categories=[UMRMeasurementCategory],
        a_eln=dict(
            hide=[
                'temperature', 'lab_id', 'location',
                'steps',
                'helper_ref_extra'],
            properties=dict(
                order=[
                    'name', 'datetime', 'user', 'device',
                    'data_file', 'measurement_data_was_extracted_from_data_file', 'solar_cell_was_referenced', 'extra_section_was_added',
                    'active_area',
                    'mode',
                    "description",
                    'tracking_data', 'extra_data'])))

    # Quantities from the Cicci file
    mode = Quantity(
        type=str,
        description='Chosen mode: Constant Voltage, Constant Current, Open-Circuit Voltage, Short-Circuit Current',
        a_eln=dict(component='StringEditQuantity'))
    
    # Helper variables for filling subsections (Reference Section)
    helper_ref_extra = Quantity(type=UMR_ConnectionTestExtraData)

    # Boolean for referencing parameter sections
    extra_section_was_added = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    

    # SubSection
    tracking_data = SubSection(section_def=UMR_ConnectionTestTrackingData)
    extra_data = SubSection(section_def=UMR_ConnectionTestExtraData) 


    def normalize(self, archive, logger):
        self.method = "Connection Test"

        # READ DATA FROM DATA FILE
        if self.data_file and not self.measurement_data_was_extracted_from_data_file:
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                log_info(self, logger, f"Normalize Connection Test Measurement: Parse data from file: {f.name} | Encoding: {encoding}")
                from ..read_and_parse.general_parser import parse_general_info          
                parse_general_info(self, f.name, encoding)
                from ..read_and_parse.connection_test_parser import parse_connectionTest_data_to_archive
                parse_connectionTest_data_to_archive(self, f.name, encoding)
        
        # REFERENCE SAMPLE
        if self.data_file and not self.solar_cell_was_referenced:
            from ..read_and_parse.general_parser import reference_sample          
            reference_sample(self, logger, archive)

        
        ## REFERENCE THE UMR_ConnectionTestExtraData ENTRY
        if not self.extra_section_was_added:
            log_warning(self, logger, "EXTRA SECTION")
            extra_data_reference = collect_extra_data(self, archive, logger)
            if len(extra_data_reference) == 1:
                for ref in extra_data_reference:
                    self.helper_ref_extra = ref
                    self.extra_data = self.helper_ref_extra.m_resolved().m_copy(deep=True)
                self.extra_section_was_added = True   



        ### PLOT CONNECTION TEST CURVES ###
        #fig = plot_connectionTest(self, toggle_grid_button=True)
        #plotly_updateLayout_NOMAD(fig)
        
        
        # Append figure to list of plots (Clear list beforehand)   
        #self.figures = []
        #fig_json=fig.to_plotly_json()
        #self.figures.append(PlotlyFigure(label=f'Connection Test - {self.datetime}', figure=fig_json))

        super(UMR_ConnectionTest, self).normalize(archive, logger)


class UMR_StabilizedShortCircuitCurrent(UMR_ConnectionTest):
    '''Extra Section for Mode "Short-Circuit Current"'''

    m_def = Section(
        label = "Stabilized Short-Circuit Current Measurement (Connection Test)",
        categories=[UMRMeasurementCategory],
        a_eln=dict(
             hide=[
                'temperature', 'lab_id', 'location',
                'steps',
                'helper_ref_extra'],
            properties=dict(
                order=[
                    'name', 'datetime', 'user', 'device',
                    'data_file', 'measurement_data_was_extracted_from_data_file', 'solar_cell_was_referenced',
                    'active_area',
                    'mode',
                    "description",
                    'time', 'voltage', 'current_density'])))
    
    def normalize(self, archive, logger):
        self.method = "Stabilized Short-Circuit Current Measurement"
        #archive.metadata.entry_type = self.m_def.name
        super(UMR_StabilizedShortCircuitCurrent, self).normalize(archive, logger)


class UMR_StabilizedOpenCircuitVoltage(UMR_ConnectionTest):
    '''Extra Section for Mode "Open-Circuit Voltage"'''

    m_def = Section(
        categories=[UMRMeasurementCategory],
        label = "Stabilized Open-Circuit Voltage Measurement (Connection Test)",
        a_eln=dict(
             hide=[
                'temperature', 'lab_id', 'location',
                'steps',
                'helper_ref_extra'],
            properties=dict(
                order=[
                    'name', 'datetime', 'device',
                    'data_file', 'measurement_data_was_extracted_from_data_file',
                    'active_area',
                    'mode',
                    "description",
                    'time', 'voltage', 'current_density'])))
    
    def normalize(self, archive, logger):
        self.method = "Stabilized Open-Circuit Voltage Measurement"
        #archive.metadata.entry_type = self.m_def.name
        super(UMR_StabilizedOpenCircuitVoltage, self).normalize(archive, logger)



m_package.__init_metainfo__()
