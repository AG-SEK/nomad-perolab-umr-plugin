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
from nomad.datamodel.metainfo.eln import SolarCellJV

# Imports HZB
from baseclasses.solar_energy import JVMeasurement
from baseclasses.helper.utilities import get_encoding

# Imports UMR
from ..categories import *
from ..helper_functions import *

#from Solar.plotfunctions import plot_jv

from ..characterization.measurement_baseclasses import UMR_MeasurementBaseclass

m_package = SchemaPackage() 

################################ JV ################################


class UMR_SolarCellJVCurve(SolarCellJV, EntryData):
    '''JV Curve Section for JV Measurement'''

    m_def = Section(
        label_quantity='scan',
        categories=[UMRCollectionCategory],
        a_eln=dict(
            hide=[
                'data_file', 'certified_values', 'certification_institute', 
                'series_resistance', 'shunt_resistance', 'current_density_at_maximun_power_point',
                'figures'],
            properties=dict(
                order=[
                    'scan', 'dark', 'light_intensity',
                    'open_circuit_voltage', 'short_circuit_current_density', 'fill_factor', 'efficiency', 'power_density_at_maximum_power_point',
                    'current_density_at_maximum_power_point', 'potential_at_maximum_power_point',
                    'series_resistance_ohm', 'shunt_resistance_ohm'])))

    # Quantity for scan direction
    scan = Quantity(
        type=MEnum('Forward', 'Reverse'),
        shape=[],
        description='Forward or Reverse Scan.',
        a_eln=dict(component='EnumEditQuantity'),
    )

    # Neccesary Quantity because Micha uses this quantity in his normalizer for JVmeasurement
    dark = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='BoolEditQuantity')
    )

    # Series resistance and Shunt resistance have the unit "Ohm*cm²" in the NOMAD baseclass
    # I create 2 new quantities with the unit "Ohm" (like in Cicci measurement files)
    series_resistance_ohm = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        description="The series resistance as extracted from the JV curve in Ohm.",
        a_eln=dict(component='NumberEditQuantity'),
    )
    shunt_resistance_ohm = Quantity(
        type=np.dtype(np.float64),
        unit='ohm',
        description="The shunt resistance as extracted from the JV curve in Ohm.",
        a_eln=dict(component='NumberEditQuantity'),
    )

    # In the NOMAD baseclass there is a typo in the Jmpp quantity (maximun !!!)
    # I created a new correct quantity but nevertheless still fill the old quantity with the same value (see normalize)
    current_density_at_maximum_power_point = Quantity(
        type=np.dtype(np.float64),
        unit='mA / cm**2',
        description="The current density at the maximum power point, *Jmp*.",
        a_eln=dict(component='NumberEditQuantity'),
    )

    # Power density at maximum power point is missing in NOMAD baseclass
    power_density_at_maximum_power_point = Quantity(
        type=np.dtype(np.float64),
        unit='mW / cm**2',
        description="""
            The power density at the maximum power point, *Pmp*.
        """,
        a_eln=dict(component='NumberEditQuantity'),
    )

    # Quantities for the JV Curve Data (Current density and voltage array)
    current_density = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='mA/cm^2',
        description='Current density array of the JV curve.',
    )
    voltage = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='V',
        description='Voltage array of the of the JV curve.',
    )


    def normalize(self, archive, logger):
        # fill "typo" quantity with the same value as new quantity
        self.current_density_at_maximun_power_point = self.current_density_at_maximum_power_point

        super(UMR_SolarCellJVCurve, self).normalize(archive, logger)



class UMR_JVMeasurement(JVMeasurement, UMR_MeasurementBaseclass, PlotSection, EntryData):
    '''Main Section for JV Measurement'''

    m_def = Section(
        categories=[UMRMeasurementCategory],
        a_display=dict(editable=dict(exclude=['description'])),
        a_eln=dict(
            hide=[
                'lab_id', 'location',
                'averaging', 'intensity', 'integration_time', 'settling_time', 'compliance',
                'steps', 'results',
                'directory'],
            properties=dict(
                order=[
                    'name', 'datetime', 'user', 'device',
                    'data_file', 'measurement_data_was_extracted_from_data_file', 'solar_cell_was_referenced',
                    'active_area', 'temperature',
                    'minimum_voltage', 'maximum_voltage', 'voltage_step', 'scan_rate', 'initial_delay', 'auto_detect_voc', 'scan_order',
                    'description',
                    'jv_curve',])))

    # Helper variable to match JV Measurements to MPP Tracking or Stability Test Measureemnts
    #directory = Quantity(type=str)
    
    # Quantities corresponding to values in Cicci files
    minimum_voltage = Quantity(
        type=np.float64,
        unit=('V'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V'))

    maximum_voltage = Quantity(
        type=np.float64,
        unit=('V'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='V'))
    
    voltage_step = Quantity(
        type=np.float64,
        unit=('V'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mV'))
    
    auto_detect_voc= Quantity(
        type=MEnum('Yes', 'No'),
        a_eln=dict(component='EnumEditQuantity'))

    scan_rate = Quantity(
        type=np.float64,
        unit=('mV/s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mV/s'))

    initial_delay = Quantity(
        type=np.float64,
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))
    
    scan_order = Quantity(
        description="RV: reverse scan, FW: forward scan",
        type=MEnum('FW->RV', 'RV->FW'),
        a_eln=dict(component="EnumEditQuantity")
    )
    
    # JV Curve Subsection with JV Curve data and JV parameters
    jv_curve = SubSection(
        section_def=UMR_SolarCellJVCurve, repeats=True)
    

    def normalize(self, archive, logger):
        self.method = "JV Measurement"
        self.measurement_data_was_extracted_from_data_file = False # NUr übergangsweise - kann dann wieder gelöscht werden.

        #archive.metadata.entry_type = self.m_def.name


        # READ DATA FROM DATA FILE
        if self.data_file and not self.measurement_data_was_extracted_from_data_file:
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            # self.data_file is not the full path, so we have to use "with archive..... "
            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                log_info(self, logger, f"Normalize JV Measurement: Parse data from file: {f.name} | Encoding: {encoding}")
                from ..read_and_parse.general_parser import parse_general_info          
                parse_general_info(self, f.name, encoding)
                from ..read_and_parse.jv_parser import parse_jv_data_to_archive
                parse_jv_data_to_archive(self, f.name, encoding)
          
        # REFERENCE SAMPLE
        if self.data_file and not self.solar_cell_was_referenced:
            from ..read_and_parse.general_parser import reference_sample          
            reference_sample(self, logger, archive)


    #        if self.samples:
    #            from UMR_schemas.umr_baseclasses import UMR_MeasurementReference
    #            from baseclasses.helper.utilities import get_reference
    #            measurement_reference = UMR_MeasurementReference(
    #                name="JV",
    #                reference=get_reference(archive.metadata.upload_id, archive.metadata.entry_id))
    #            log_info(self, logger, f"JVVVVVV{self.samples}++++{self.samples[0]}+++++++++++{self.samples[0].reference.jv_measurements}")    
                
    #            for sample in self.samples:
    #                measurement_ref=get_reference(archive.metadata.upload_id, archive.metadata.entry_id)
    #                log_info(self, logger, f"111 {measurement_ref}")
    #                list = [measurement_ref]
    #                sample.reference.jv_measurement = list
    #                log_info(self, logger, f"222 {sample.reference.jv_measurement}")
    #                #sample.reference.jv_measurement.append(measurement_ref)
    #                log_info(self, logger, "333")
    #                #sample.reference.measurements.jv_measurements = [measurement_ref]
    #                #log_info(self, logger, "444")
    #                sample.reference.measurements.jv_measurements = [measurement_ref]

# Das klappt so nicht, da Archiv nicht geupdatet wird!


        ### PLOT JV CURVES ###
    #    fig = plot_jv(self.m_to_dict()['jv_curve'], toggle_grid_button=True, toggle_table_button=True)
        # We need m_to_dict() because otherwise error: 
            # File "/app/plugins/Solar/plotfunctions/jv.py", line 120, in plot_jv
            # curve['fill_factor'] = round(curve['fill_factor'], 1)
            # TypeError: 'UMR_SolarCellJVCurve' object does not support item assignment

        # Set Settings again (overwrite NOMAD defaults)
    #    plotly_updateLayout_NOMAD(fig)
        
        # Append figure to list of plots (Clear list beforehand)   
   #     self.figures = []
    #    fig_json=fig.to_plotly_json()
    #    fig_json["config"] = plot_config

   #     self.figures.append(PlotlyFigure(label='JV Curve Plot', figure=fig_json))
        
        super(UMR_JVMeasurement, self).normalize(archive, logger)



m_package.__init_metainfo__()
