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
from nomad.datamodel.metainfo.basesections import SectionReference, EntityReference, InstrumentReference
from nomad.metainfo import Quantity, SubSection, Section, Package
from nomad.datamodel.metainfo.plot import PlotSection


# Imports HZB/Michael Götte
from baseclasses.solar_energy import SolcarCellSample


# Imports UMR
from .suggestions_lists import *
from .helper_functions import *
from .categories import *


###################### Reference Classes #####################

# Reference class for Solar Cells, Samples, Substrates, Batches
class UMR_EntityReference(EntityReference):
    m_def = Section(
        label_quantity='name',
        a_eln=dict(
            properties=dict(
                order=['name', 'reference', 'lab_id','description'])))

    description = Quantity(
        type=str,
        a_eln=dict(component='RichTextEditQuantity'))

    def normalize(self, archive, logger):
        if not self.name:
            self.name = self.reference.name
        super(UMR_EntityReference, self).normalize(archive, logger)

        
# Reference class for Solar Cells, Samples, Substrates, Batches
class UMR_InstrumentReference(InstrumentReference):
    m_def = Section(
        label_quantity='name',
        a_eln=dict(
            properties=dict(
                order=['name', 'reference', 'lab_id', 'description' ])))

    description = Quantity(
        type=str,
        a_eln=dict(component='RichTextEditQuantity'))

    def normalize(self, archive, logger):
        super(UMR_InstrumentReference, self).normalize(archive, logger)
        if self.reference:
            self.name = self.referece.name
        # Run super at end of normalizer otherwise name is already set to lab_id!


        
# Reference class for chemicals
class UMR_ChemicalReference(EntityReference):
    m_def = Section(label_quantity='label')

    label = Quantity(type=str)

    def normalize(self, archive, logger):
        if self.reference:
            self.lab_id = self.reference.lab_id
        #self.name = self.reference.name
        self.label = f"{self.lab_id}"
        super(UMR_ChemicalReference, self).normalize(archive, logger)

# WIRD CHEMICAL REFERENCE NOCH BENÖTIGT ?????????


class UMR_MeasurementReference(SectionReference, PlotSection):
    m_def = Section(label_quantity='name')
    
    display_name = Quantity(type=str)

    def normalize(self, archive, logger):
        self.name = self.reference.method
        self.display_name = f"{self.name} {self.reference.datetime}"
        self.figures=self.reference.figures
        super(UMR_MeasurementReference, self).normalize(archive, logger)

    # TODO Normalizer der Plot aus Referenz darstellt

