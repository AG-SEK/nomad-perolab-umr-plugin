
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
from nomad.datamodel.data import EntryData
from nomad.metainfo import Quantity, SchemaPackage, Section
from nomad_luqy_plugin.schema_packages.schema_package import (
    AbsPLMeasurement,
    AbsPLResult,
    AbsPLSettings,
)

m_package = SchemaPackage() 


class UMR_AbsPLResult(AbsPLResult):
    m_def = Section(label='AbsPLResult with iVoc')

    i_voc = Quantity(
        type=np.float64,
        unit='V',
        description='iVoc in V, e.g. 1.23.',
        a_eln=dict(component='NumberEditQuantity', label='iVoc'),
    )



class UMR_AbsPLMeasurement(AbsPLMeasurement, EntryData):
    m_def = Section(label='Absolute PL Measurement')

    def normalize(self, archive, logger):  # noqa: PLR0912, PLR0915
        logger.debug('Starting UMR_AbsPLMeasurement.normalize', data_file=self.data_file)
        if self.settings is None:
            self.settings = AbsPLSettings()

        if self.data_file:
            try:
                from nomad_perolab_umr.schema_packages.read_and_parse.luqy_parser import (
                    parse_abspl_data,
                )

                # Call the new parser function
                (
                    settings_vals,
                    result_vals,
                    wavelengths,
                    lum_flux,
                    raw_counts,
                    dark_counts,
                ) = parse_abspl_data(self.data_file, archive, logger)

                # Set settings
                for key, val in settings_vals.items():
                    setattr(self.settings, key, val)

                # Set results header values
                if not self.results:
                    self.results = [UMR_AbsPLResult()]
                for key, val in result_vals.items():
                    setattr(self.results[0], key, val)

                # Set spectral array data
                self.results[0].wavelength = np.array(wavelengths, dtype=float)
                self.results[0].luminescence_flux_density = np.array(lum_flux, dtype=float)
                self.results[0].raw_spectrum_counts = np.array(raw_counts, dtype=float)
                self.results[0].dark_spectrum_counts = np.array(dark_counts, dtype=float)

            except Exception as e:
                logger.warning(f'Could not parse the data file "{self.data_file}": {e}')
                print(e)
        super().normalize(archive, logger)



m_package.__init_metainfo__()
