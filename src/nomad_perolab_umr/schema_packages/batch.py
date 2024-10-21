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



# Imports Nomad
from nomad.config import config
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import Entity
from nomad.metainfo import Quantity, SubSection, Section, Reference, Package, MEnum, SchemaPackage

# Imports UMR
from .suggestions_lists import *
from .helper_functions import *
from .categories import *

from .umr_reference_classes import UMR_EntityReference


m_package = SchemaPackage(
#    aliases=[
#        'UMR_schemas',
#    ],
)

# Create Package instance, which organize metainfo definitions alongside Python modules.
# Definitions (categories, sections) in Python modules are automatically added to the module's :class:`Package`.



################################ Group ################################

class UMR_Group(Entity, EntryData):
    m_def = Section(
        label_quantity='display_name',
        categories=[UMRCollectionCategory],
        label='Group',
        a_eln=dict(
            hide=['lab_id', 'datetime', 'name'],
            editable=dict(exclude=["display_name"]),
            properties=dict(
                order=[
                    'display_name',
                    'name', 'datetime',
                    'batch', 'group_number', 'group_description',
                    'number_of_substrates',
                    'description',
                    ]))
    )

    display_name = Quantity(
        label='Group',
        type=str,
        description='Automatically generated name of group, displayed in SubSections',
    )

    group_number = Quantity(
        description='Number of this group',
        type=int,
        a_eln=dict(component='NumberEditQuantity')   
    ) 

    group_description = Quantity(   
        type=str,
        description='short description of this group',
        a_eln=dict(component='StringEditQuantity'))

    number_of_substrates = Quantity(
        description='Number of identical substrates in this group',
        type=int,
        a_eln=dict(component='NumberEditQuantity')   
    ) 

    samples = SubSection(
        section_def = UMR_EntityReference, repeats=True)

    substrates = SubSection(
        section_def = UMR_EntityReference, repeats=True)
        
    def normalize(self, archive, logger):
        # Automatically generate display_name
        self.display_name = f"{self.group_number} - {self.group_description}"
        
        super(UMR_Group, self).normalize(archive, logger)



################################ BATCH ################################

class UMR_Batch(Entity):
    m_def = Section()
    
    batch_number = Quantity(
        type = int,
        description = "3-digits number of the batch (001-999) ",
        a_eln = dict(component='NumberEditQuantity'))

    samples = SubSection(
        section_def = UMR_EntityReference, repeats=True)

    substrates = SubSection(
        section_def = UMR_EntityReference, repeats=True)
    
    groups = SubSection(
        section_def = UMR_Group, repeats=True)
    

class UMR_ExternalBatch(UMR_Batch, EntryData):
    m_def = Section(
        categories=[UMRCollectionCategory],
        label='External Batch',
        label_quantity = 'lab_id',
        a_eln=dict( 
           hide=[],
            properties=dict(
                order=[
                    'name', 'datetime', 'lab_id',
                    'supplier', 'batch_number',
                    'external_batch_name_supplier',
                    'description'])))

    external_batch_name_supplier = Quantity(
        type=str,
        description='The Batch name corresponding to the external supplier.',
        a_eln=dict(component='StringEditQuantity'))

    supplier = Quantity(
        type=MEnum(suggestions_supplier),
        description='Choose the name of the supplier from the dropdown list or type in a new one.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_supplier)))
    

class UMR_InternalBatch(UMR_Batch, EntryData):
    m_def = Section(
        categories=[UMRCollectionCategory],
        label='Internal Batch',
        label_quantity='lab_id',
        a_eln=dict(
            hide=[],
            properties=dict(
                order=[
                    'name', 'datetime', 'lab_id',
                    'batch_description', 'batch_number',
                    'responsible_person',
                    'description'])))
    
    batch_description = Quantity(
        type=str,
        description='Choose the description for this batch from the dropdown list.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_batch_descriptions)))
   
    responsible_person = Quantity(
        type=str,
        description='Choose the responsible person for this batch from the dropdown list.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_persons)))
   




m_package.__init_metainfo__()