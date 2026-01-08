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
from baseclasses import BaseMeasurement  # TODO
from baseclasses.helper.utilities import get_encoding

# Imports HZB
from nomad.datamodel.data import ArchiveSection, EntryData
from nomad.datamodel.metainfo.eln import SolarCellEQE

# Imports Nomad
from nomad.datamodel.metainfo.plot import PlotlyFigure, PlotSection
from nomad.metainfo import MEnum, Quantity, SchemaPackage, Section, SubSection

# Imports UMR
from Solar.plotfunctions import plot_eqe
from nomad_perolab_umr.Solar.plotfunctions import plot_eqe

from ..categories import *
from ..characterization.measurement_baseclasses import UMR_MeasurementBaseclass
from ..helper_functions import *

m_package = SchemaPackage(aliases=['UMR_schemas.characterization.eqe_measurement']) 

################################ EQE ################################


class UMR_SolarCellEQE(ArchiveSection):
    '''EQE Data Section for EQE Measurement'''
    
    m_def = Section()

    # Arrays for the EQE data
    wavelength = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='nm',
        description='Wavelength Array in nm',
    )

    eqe = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        description='IPCE (EQE) Array',
    ) 
    
    device_current_density = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='mA/cm^2',
        description='Device Current Density Array in mA/cm²',
    )
    integrated_current_density = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='mA/cm^2',
        description='Integrated Device Current Density Array in mA/cm²',
    )   

    intensity = Quantity(
        type=np.dtype(np.float64),
        shape=['*'],
        unit='mW/cm^2',
        description='Light Intensity Array in mW/cm²',
    )


class UMR_EQEMeasurement(BaseMeasurement, PlotSection, EntryData, UMR_MeasurementBaseclass):
    '''Main Section for EQE Measurement'''

    m_def = Section(
        categories=[UMRMeasurementCategory],
        a_eln=dict(
            hide=[
                'lab_id', 'location',
                'steps', 'results'],
            properties=dict(
                order=[
                    'name', 'datetime', 'user', 'device',
                    'data_file', 'measurement_data_was_extracted_from_data_file', 'solar_cell_was_referenced',
                    'active_area', 'temperature',
                    'minimum_wavelength', 'wavelength_step', 'maximum_wavelength',
                    "averaging", "autorange", "delay_time", "bias_voltage", "bias_light", "spectral_mismatch",
                    "description",]    
                   )))
    
    # Quantities from Cicci file
    minimum_wavelength = Quantity(
        type=np.float64,
        unit=('nm'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='nm'))

    maximum_wavelength = Quantity(
        type=np.float64,
        unit=('nm'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='nm'))
    
    wavelength_step = Quantity(
        type=np.float64,
        unit=('nm'),
        shape=[],
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='nm'))
    
    averaging = Quantity(
        type=int,
        shape=[],
        a_eln=dict(component='NumberEditQuantity'))
            
    autorange = Quantity(
        type=MEnum('TRUE', 'FALSE'),
        a_eln=dict(component='EnumEditQuantity'))

    delay_time = Quantity(
        type=np.float64,
        unit=('s'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s'))

    bias_voltage = Quantity(
        type=np.float64,
        unit=('V'),
        a_eln=dict(
            component='NumberEditQuantity', defaultDisplayUnit='V'))

    bias_light = Quantity(
        type=np.float64,
        #unit=(''),
        a_eln=dict(
            component='NumberEditQuantity'))

    spectral_mismatch = Quantity(
        type=np.float64,
        a_eln=dict(
            component='NumberEditQuantity'))  

    # Subsection with EQE data from cicci file
    eqe_data = SubSection(section_def=UMR_SolarCellEQE)

    # Subsection with NOMAD baseclass -> Takes data automatically from file and calulates bandgap, ...
    advanced_eqe_data = SubSection(section_def=SolarCellEQE)


    def normalize(self, archive, logger):
        self.method = "EQE Measurement"
        #archive.metadata.entry_type = self.m_def.name

        if self.data_file and not self.measurement_data_was_extracted_from_data_file:
            with archive.m_context.raw_file(self.data_file, "br") as f:
                encoding = get_encoding(f)

            with archive.m_context.raw_file(self.data_file, encoding=encoding) as f:
                log_info(self, logger, f"Normalize EQE Measurement: Parse data from file: {f.name} | Encoding: {encoding}")
                from ..read_and_parse.general_parser import parse_general_info
                parse_general_info(self, f.name, encoding)
                from ..read_and_parse.eqe_parser import parse_eqe_data_to_archive
                parse_eqe_data_to_archive(self, f.name, encoding)
            
            # Normalize advanced eqe section
            try:
                self.advanced_eqe_data.normalize(archive, logger)
            except Exception as e:
                log_error(self, logger, f"An error occured during normalization of the advanced_eqe_data section. Please check: {e}")

          
        # REFERENCE SAMPLE
        if self.data_file and not self.solar_cell_was_referenced:
            from ..read_and_parse.general_parser import reference_sample
            reference_sample(self, logger, archive)


        ### PLOT EQE CURVES ###
        fig = plot_eqe(full_eqe_data=[self.m_to_dict()], toggle_grid_button=True, showplot=False)
        plotly_updateLayout_NOMAD(fig)

        # Append figure to list if plots (Clear list beforehand)   
        self.figures = []
        fig_json=fig.to_plotly_json()
        fig_json["config"] = plot_config

        self.figures.append(PlotlyFigure(label='EQE Plot', figure=fig_json))

        super().normalize(archive, logger)



m_package.__init_metainfo__()

