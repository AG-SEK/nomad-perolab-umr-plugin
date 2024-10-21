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
from nomad.metainfo import MEnum, Quantity, SubSection, Section, SchemaPackage , Reference
from nomad.datamodel.data import EntryData, ArchiveSection

# Imports HZB
from baseclasses.helper.utilities import get_encoding, get_reference

from baseclasses import BaseMeasurement

# Imports UMR
from ..categories import *
from ..helper_functions import *

from ..characterization.measurement_baseclasses import UMR_MeasurementBaseclass, UMR_TrackingData, UMR_CollectedJVMeasurements
from ..characterization.jv_measurement import UMR_JVMeasurement
from ..characterization.stability_test import UMR_JVParameters

#from Solar.plotfunctions import plot_mppt


m_package = SchemaPackage() 

################################ MPP Tracking ################################

class UMR_MPPTrackingJVMeasurement(UMR_JVMeasurement):
    '''JV Measurement Section for MPP Tracking'''

    m_def = Section(
        label_quantity = 'datetime',
        a_eln=dict(
            hide=[
                'lab_id', 'location',
                'averaging', 'intensity', 'integration_time', 'settling_time', 'compliance',
                'steps', 'results',
                'atmosphere', 'instruments',
                'name', 'datetime', 'user', 'device',
                'best_measurement'],
            properties=dict(
                order=[
                    'name', 'datetime', 'user', 'device',
                    'data_file', 'measurement_data_was_extracted_from_data_file', 'solar_cell_was_referenced',
                    'active_area', 'temperature',
                    'minimum_voltage', 'maximum_voltage', 'voltage_step', 'scan_rate', 'initial_delay', 'auto_detect_voc', 'scan_order',
                    'description',
                    'jv_curve'])))
    
    def normalize(self, archive, logger):
        super(UMR_MPPTrackingJVMeasurement, self).normalize(archive, logger)


class UMR_MPPTrackingParameters(UMR_JVParameters):
    '''JV Parameters Section for MPP Tracking'''
    # see stability_test for UMR_JVParameters

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
        super(UMR_MPPTrackingParameters, self).normalize(archive, logger)

    
class UMR_MPPTrackingData(UMR_TrackingData):
    '''Tracking Data Section for MPP Tracking'''

    m_def = Section()
    

class UMR_MPPTracking(BaseMeasurement, PlotSection, EntryData, UMR_MeasurementBaseclass):
    '''Main Section for MPP Tracking'''

    m_def = Section(
        categories=[UMRMeasurementCategory],
        a_eln=dict(
            hide=[
                'lab_id', 'location',
                'temperature',
                'steps', 'results',
                'helper_ref_params', 'helper_ref_jv'],
            properties=dict(
                order=[
                    'name', 'datetime', 'user', 'device',
                    'data_file', 'measurement_data_was_extracted_from_data_file', 'solar_cell_was_referenced', 'parameter_sections_were_added',
                    'active_area', 'mpp_duration'
                    'description',
                    'tracking_data', 'jv_parameters', 'jv_measurements'])))

    # Quantites from the Cicci file
    mpp_duration = Quantity(
        type=np.float64,
        unit='minute',
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='minute'))

    # Helper variable to match MPPTracking measurements
    #directory = Quantity(type=str)

    # Boolean for referencing parameter sections
    parameter_sections_were_added = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
    # Helper variables for filling subsections (Reference Section)
    helper_ref_params = Quantity(type=Reference(UMR_MPPTrackingParameters.m_def))
    helper_ref_jv = Quantity(type=Reference(UMR_MPPTrackingJVMeasurement.m_def))

    # SubSections
    tracking_data = SubSection(section_def=UMR_MPPTrackingData)                                # Subsection with data in array quantities
    jv_parameters = SubSection(section_def=UMR_MPPTrackingParameters, repeats=True)        # Subsection with JV Parameters over time
    jv_measurements = SubSection(section_def=UMR_CollectedJVMeasurements)


    def normalize(self, archive, logger):
        self.method = "MPP Tracking"
        #archive.metadata.entry_type = self.m_def.name

        # READ DATA FROM DATA FILE
        if self.data_file and not self.measurement_data_was_extracted_from_data_file:
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                log_info(self, logger, f"Normalize MPPT Tracking Measurement: Parse data from file: {f.name} | Encoding: {encoding}")
                from UMR_schemas.read_and_parse.general_parser import parse_general_info          
                parse_general_info(self, f.name, encoding)
                from UMR_schemas.read_and_parse.mppt_parser import parse_mppt_data_to_archive
                parse_mppt_data_to_archive(self, f.name, encoding)
           
        # REFERENCE SAMPLE
        if self.data_file and not self.solar_cell_was_referenced:
            from UMR_schemas.read_and_parse.general_parser import reference_sample          
            reference_sample(self, logger, archive)
     

        # REFERENCE THE CORRESPONDING MPPTrackingJVMeasurements ENTRIES
        self.jv_measurements = UMR_CollectedJVMeasurements()
        self.jv_measurements.jv_measurements = collect_jv_curves(self, archive, logger, 'mpp_tracking.UMR_MPPTrackingJVMeasurement')
        
        # REFERENCE THE 2 MPPTrackingParameters ENTRIES
        if not self.parameter_sections_were_added:
            self.jv_parameters = []
            parameters_references = collect_parameters(self, archive, logger, 'mpp_tracking.UMR_MPPTrackingParameters')
            if len(parameters_references) == 2:
                for ref in parameters_references:
                    self.helper_ref_params = ref
                    entry = self.helper_ref_params.m_resolved().m_copy(deep=True)
                    self.jv_parameters.append(entry)
                self.parameter_sections_were_added = True


        #for ref in jv_curves_references:
        #    self.helper_ref_jv = ref
        #    entry = self.helper_ref_jv.m_resolved().m_copy(deep=True)
        #    self.jv_measurements.append(entry)


        ### PLOT MPP TRACKING CURVES ###
    #    fig_power, fig_voltage_current = plot_mppt(self.tracking_data, toggle_grid_button=True)
    #    plotly_updateLayout_NOMAD(fig_power)
   #     plotly_updateLayout_NOMAD(fig_voltage_current)

        # Append figure to list of plots (Clear list beforehand)   
    #    self.figures = []

   #     fig_power_json=fig_power.to_plotly_json()
   #     fig_power_json["config"] = plot_config
   #     self.figures.append(PlotlyFigure(label='Power Density Plot - MPP Tracking',figure=fig_power_json))

    #    fig_voltage_current_json=fig_voltage_current.to_plotly_json()
   #     fig_voltage_current_json["config"] = plot_config
    #    self.figures.append(PlotlyFigure(label='Voltage and Current Density Plot - MPP Tracking', figure=fig_voltage_current_json))
    
        super(UMR_MPPTracking, self).normalize(archive, logger)


m_package.__init_metainfo__()
