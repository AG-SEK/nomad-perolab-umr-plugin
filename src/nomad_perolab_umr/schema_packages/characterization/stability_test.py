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
from nomad.metainfo import MEnum, Quantity, SubSection, Section, SchemaPackage, Reference, Datetime 
from nomad.datamodel.data import EntryData, ArchiveSection

# Imports HZB
from baseclasses.helper.utilities import get_encoding, get_reference

from baseclasses import BaseMeasurement

# Imports UMR
from .measurement_baseclasses import UMR_MeasurementBaseclass, UMR_TrackingData, UMR_JVParameters, UMR_CollectedJVMeasurements
from .jv_measurement import UMR_JVMeasurement
from ..categories import *
from ..helper_functions import *

#from Solar.plotfunctions import plot_stability_parameter

m_package = SchemaPackage(aliases=['UMR_schemas.characterization.stability_test']) 

################################ Stability Test (Ageing) ################################

class UMR_StabilityJVMeasurement(UMR_JVMeasurement):
    '''JV Measurement Section for Stability Test'''

    m_def = Section(
        a_eln=dict(
            hide=[
                'lab_id', 'location',
                'averaging', 'intensity', 'integration_time', 'settling_time', 'compliance',
                'steps', 'results',
                'best_measurement'],
            properties=dict(
                order=[
                    'name', 'datetime', 'user', 'device',
                    'data_file', 'measurement_data_was_extracted_from_data_file', 'solar_cell_was_referenced',
                    'active_area', 'temperature',
                    'minimum_voltage', 'maximum_voltage', 'voltage_step', 'scan_rate', 'auto_detect_voc', 'initial_delay', 'scan_order',
                    "description"])))
   
    def normalize(self, archive, logger):
        super(UMR_StabilityJVMeasurement, self).normalize(archive, logger)


class UMR_StabilityParameters(UMR_JVParameters):
    ''' JV Parameters Class for StabilityParameters and MPPTrackingParameters'''

    m_def = Section(
        label_quantity = 'scan',
        a_eln=dict(
            hide=['lab_id', 'location',
                  'steps', 'results',
                  'atmosphere', 'instruments',
                  'name', 'datetime', 'user', 'device',
                  'description', 'active_area', 'temperature',
                  'method', 'best_measurement'],
            properties=dict(
                order=[
                    'scan',
                    'data_file', 'measurement_data_was_extracted_from_data_file', 'solar_cell_was_referenced',
                    ])))
    
    def normalize(self, archive, logger):
        super(UMR_StabilityParameters, self).normalize(archive, logger)


# Tracking SubSection for StabilityTest
class UMR_StabilityTracking(UMR_TrackingData, PlotSection):    
    '''JV Parameters Section for Stability Test'''
  
    m_def = Section(
        a_eln=dict(
            hide=[
                'reference_helper',
                'lab_id', 'location',
                'steps', 'results',]))

    # Quantities from Cicci file
    time = Quantity(
        type=np.dtype(np.float64),
        description='Time array of the Ageing measurement',
        shape=['*'],
        unit='hour') # HOUR !!!

    
    def normalize(self, archive, logger):

        ### PLOT STABILITY TRACKING CURVES ###
        fig_power, fig_voltage_current = plot_stability(self, step=100, toggle_grid_button=True)
        plotly_updateLayout_NOMAD(fig_power)
        plotly_updateLayout_NOMAD(fig_voltage_current)

        # Append figure to list of plots (Clear list beforehand)   
        self.figures = []
        fig_power_json=fig_power.to_plotly_json()
        fig_voltage_current_json=fig_voltage_current.to_plotly_json()
        self.figures.append(PlotlyFigure(label='Power Density Plot - MPP Tracking',figure=fig_power_json))
        self.figures.append(PlotlyFigure(label='Voltage and Current Density Plot - MPP Tracking', figure=fig_voltage_current_json))
    
        super(UMR_StabilityTracking, self).normalize(archive, logger)


class UMR_StabilityTest(UMR_MeasurementBaseclass, BaseMeasurement, PlotSection, EntryData):
    m_def = Section(
        categories=[UMRMeasurementCategory],
        a_eln=dict(
            hide=[
                'lab_id', 'location',
                'steps', 'results',
                'temperature',
                'helper_ref_params', 'helper_ref_jv'],
            properties=dict(
                order=[
                    'name', 'datetime', 'user', 'device',
                    'data_file', 'measurement_data_was_extracted_from_data_file', 'solar_cell_was_referenced', 'parameter_sections_were_added',
                    'active_area',
                    'algorithm', 'voltage_step_track', 'track_delay', 'jv_interval', 'test_duration', 'start_up_time',
                    'description',
                    'tracking_data','jv_parameters', 'jv_measurements',])))
    


    # Quantities from Cicci file
    algorithm = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity', defaultDisplayUnit='nm'))

    voltage_step_track = Quantity(
        type=np.float64,
        unit=('V'),
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='V'))
    
    track_delay = Quantity(
        type=np.float64,
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='s'))
    
    jv_interval = Quantity(
        type=np.float64,
        unit=('hour'),       
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='hour'))
    
    test_duration = Quantity(
        type=np.float64,
        unit=('hour'),       
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='hour'))

    start_up_time = Quantity(
        type=Datetime,
        description='The start date and time.',
        a_eln=dict(component='DateTimeEditQuantity'))
  
    # Helper variable to match MPPTracking measurements
    #directory = Quantity(type=str)

    
    # Boolean for referencing parameter sections
    parameter_sections_were_added = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity'))

    # Helper variables for filling subsections (Reference Section)
    helper_ref_params = Quantity(type=Reference(UMR_StabilityParameters.m_def))
    helper_ref_jv = Quantity(type=Reference(UMR_StabilityJVMeasurement.m_def))


    # SubSections
    tracking_data = SubSection(section_def=UMR_StabilityTracking)
    jv_parameters =SubSection(section_def=UMR_StabilityParameters, repeats=True)
    jv_measurements = SubSection(section_def=UMR_CollectedJVMeasurements)
    

    def normalize(self, archive, logger):
        self.method = "Stability Test"
        #archive.metadata.entry_type = self.m_def.name


        # READ DATA FROM DATA FILE
        if self.data_file and not self.measurement_data_was_extracted_from_data_file:
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                log_info(self, logger, f"Normalize Stability Test Measurement: Parse data from file: {f.name} | Encoding: {encoding}")
                from ..read_and_parse.general_parser import parse_general_info          
                parse_general_info(self, f.name, encoding)
                from ..read_and_parse.stability_parser import parse_stabilityTracking_data_to_archive
                parse_stabilityTracking_data_to_archive(self, f.name, encoding)
          
               
        # REFERENCE SAMPLE
        if self.data_file and not self.solar_cell_was_referenced:
            from ..read_and_parse.general_parser import reference_sample          
            reference_sample(self, logger, archive)

        # REFERENCE THE 2 StabilityParameters ENTRIES
        if not self.parameter_sections_were_added:
            self.jv_parameters = []
            parameters_references = collect_parameters(self, archive, logger, 'stability_test.UMR_StabilityParameters')
            if len(parameters_references) == 2:
                for ref in parameters_references:
                    self.helper_ref_params = ref
                    entry = self.helper_ref_params.m_resolved().m_copy(deep=True)
                    self.jv_parameters.append(entry)
                self.parameter_sections_were_added = True

        
        # REFERENCE THE CORRESPONDING StabilityJVMeasurement ENTRIES
        self.jv_measurements = UMR_CollectedJVMeasurements()
        self.jv_measurements.jv_measurements = collect_jv_curves(self, archive, logger, 'stability_test.UMR_StabilityJVMeasurement')
        
        
        #for ref in jv_curves_references:
        #    self.helper_ref_jv = ref
        #    entry = self.helper_ref_jv.m_resolved().m_copy(deep=True)
        #    self.jv_measurements.append(entry)



        ### PLOT STABILITY CURVES ###
        # PLOT JV PARAMETER OVER TIME
        # Append figure to list of plots (Clear list beforehand)   
        self.figures = []
        log_info(self, logger, f"{JVparameters_name_dict}|{JVparameters_list}")
        for parameter in JVparameters_list:
            # Plot first parameters object (Reverse or Forward)
            log_info(self, logger, f"{parameter}---{self.jv_parameters[0]}")
      #      fig = plot_stability_parameter(self.jv_parameters[0], parameter)
      #      fig.data[0].name = self.jv_parameters[0].scan
            # Plot second paramters object (other) in same plot
       #     fig = plot_stability_parameter(self.jv_parameters[1], parameter, toggle_grid_button=True, fig=fig)
       #     fig.data[1].name = self.jv_parameters[1].scan

       #     plotly_updateLayout_NOMAD(fig)
      #      fig_json=fig.to_plotly_json()
     #       fig_json["config"] = plot_config

      #      self.figures.append(PlotlyFigure(label=JVparameters_name_dict[parameter],figure=fig_json))

        super(UMR_StabilityTest, self).normalize(archive, logger)

