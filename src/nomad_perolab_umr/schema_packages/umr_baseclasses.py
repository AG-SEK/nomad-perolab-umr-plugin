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
from nomad.datamodel.metainfo.basesections import SectionReference, Entity, EntityReference, Measurement, Instrument, InstrumentReference
from nomad.metainfo import MEnum, Reference, Quantity, SubSection, Section, SchemaPackage, Datetime
from nomad.datamodel.metainfo.plot import PlotSection
from nomad.datamodel.data import author_reference, user_reference



# Imports HZB/Michael Götte
from baseclasses import LayerProperties, BaseProcess, LayerDeposition
from baseclasses.helper.utilities import get_reference
from baseclasses.solar_energy import SolcarCellSample


# Imports UMR
from .suggestions_lists import *
from .helper_functions import *
from .categories import *
from .umr_reference_classes import UMR_ChemicalReference, UMR_InstrumentReference

m_package = SchemaPackage() 


################################ HELPER SUBSECTIONS ################################

#class UMR_DeviceName(ArchiveSection):
#    '''Helper Section for alternative device names'''
#
#    m_def=Section(label_quantity = 'device_name')
#
#    device_name = Quantity(
#        type=str,
#        description = "If you used a different device name in your measurements, type it in here",
#        a_eln=dict(component='StringEditQuantity'))
 

class UMR_MeasurementsSubsection(ArchiveSection):
    '''Measurement SubSection'''

    jv_measurements = Quantity(
        type = Measurement,
        shape=['*'])
    
    eqe_measurements = Quantity(
        type = Measurement,
        shape=['*'])
    
    stability_measurements = Quantity(
        type = Measurement,
        shape=['*'])
    
    mppt_measurements = Quantity(
        type = Measurement,
        shape=['*'])
    
    other_measurements = Quantity(
        type = Measurement,
        shape=['*'])

    def normalize(self, archive, logger):
        super(UMR_MeasurementsSubsection, self).normalize(archive,logger)
        
        # Check how many best_measurement entries exist and if applicable set one

        if self.jv_measurements:
            number_of_best_measurements = check_best_measurements(self, archive, logger, self.jv_measurements)
            if number_of_best_measurements == 0:
                # Find highest Reverse efficiency measurement and make it best_measurement
                highest_efficiency_entry = max(self.jv_measurements, key=lambda obj: obj.jv_curve[0].efficiency)
                # Set best_measurement and update archive
                highest_efficiency_entry.best_measurement=True
                highest_efficiency_entry_mainfile = highest_efficiency_entry.m_root().metadata.mainfile
                create_archive(highest_efficiency_entry, archive, highest_efficiency_entry_mainfile, overwrite=True)
                log_warning(self, logger, f"The measurement {highest_efficiency_entry.name} -  was set to best_measurement because of the highest reverse efficiency.")


        if self.eqe_measurements:
            number_of_best_measurements = check_best_measurements(self, archive, logger, self.eqe_measurements)
            if number_of_best_measurements == 0:
                set_single_measurement_as_best_measurement(self, archive, logger, self.eqe_measurements)

        if self.stability_measurements:
            check_best_measurements(self, archive, logger, self.stability_measurements)
            
        if self.mppt_measurements:
            check_best_measurements(self, archive, logger, self.mppt_measurements)

                 
        if self.other_measurements:
            check_best_measurements(self, archive, logger, self.other_measurements)


################################ Layer ################################

class UMR_Layer(LayerProperties):
    m_def = Section(
        label_quantity='layer_type',
        a_eln=dict(
            properties=dict(
                order=['layer_name', 
                       'layer_type','layer_material_name',
                       'thickness',
                       'structuring',
                       'position_in_layer_stack',
                       'deposition_process',]))
    )
    

    layer_name = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))

    display_name = Quantity(
        type=str,
        description="Automatically generated from type and material")
    
    thickness = Quantity(  # layer thickness
        type=np.float64,
        unit='nm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))
    
    structuring = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_structuring)))
    
    position_in_layer_stack =  Quantity(
        type=int,
        description='The position in the layer stack starting from the back',
        a_eln=dict(component='NumberEditQuantity'))
    
    deposition_method = Quantity(
        type=str,
        a_eln=dict(
            component='StringEditQuantity'))
    
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(component='RichTextEditQuantity'),
    )


    def normalize(self, archive, logger):

        if self.layer_type and self.layer_name:
            self.display_name = f"{self.layer_type} - {self.layer_name}"

        # Get Deposition method from parent section
        if hasattr(self.m_parent, 'method'):
            log_info(self, logger, f"Layer normalizer: GET METHOD from parent section: {self.m_parent}")
            self.deposition_method =  self.m_parent.method

        # Set position_in_layer_stack
        if hasattr(self.m_parent, 'processes'):
            log_warning(self, logger, f"Layer normalizer: SET POSITION IN LAYER STACK - parent section: {self.m_parent} - index: {self.m_parent_index}")
            self.position_in_layer_stack = self.m_parent_index + 1

        super(UMR_Layer, self).normalize(archive, logger)



############################## FILES #################################

class UMR_FileWithDescription(ArchiveSection):
    m_def = Section(
        label_quantity='name',
        a_eln=dict(order=['name', 'document', 'description']))
    
    name = Quantity(
        type=str,
        description='The name of the file, e.g. manual, brochure, ...',
        a_eln=dict(component='StringEditQuantity', label='Short name'))

    document = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(component='RichTextEditQuantity'))


    

################################ Room ################################



class UMR_InstructedPerson(ArchiveSection):
    m_def = Section(
        label_quantity='instructed_person',
        a_eln=dict(order=['instructed_person', 'datetime', 'instruction_document', 'description']))
    
    instructed_person = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_persons)))
    
    datetime = Quantity(
        type=Datetime,
        description='The date of the security briefing.',
        a_eln=dict(component='DateTimeEditQuantity'))

    instruction_document = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    
    description = Quantity(
        type=str,
        description='Any information that cannot be captured in the other fields.',
        a_eln=dict(component='RichTextEditQuantity'))

    #user = Quantity(
    #    type=user_reference,
    #    description='The corresponding user for the activity.',
    #    a_eln=dict(component='AuthorEditQuantity'),
    #)

    #def normalize(self, archive, logger):
    #    super(UMR_InstructedPerson, self).normalize(archive, logger)

        #log_info(self, logger, f"USER{self.user}")
        #log_info(self, logger, f"{self.user.resolve(self)}")
        #log_info(self, logger, f"USE{self.user.m_proxy_section.user.last_name}")
        #self.label =f"{self.user.first_name} {self.user.last_name}"
        # This did not work self.user is MProxy Object. I am not sure how to tackle it


class UMR_Room(Entity, EntryData):
    
    m_def = Section(
        categories=[UMRCreateCategory],
        a_eln=dict(
            hide=['datetime'],
            properties=dict(
                order=[
                    'name', 'short_name',
                    'building', 'room_number',
                    'room_category', 'description'])))
  
    lab_id = Quantity(type=str)

    name = Quantity(
        type=str,
        description="long understandable name.",
        a_eln=dict(component='StringEditQuantity'),
    )

    short_name = Quantity(
        type=str,
        description="short name of the room - used in lab id.",
        a_eln=dict(component='StringEditQuantity'))

    room_number = Quantity(
        type = str,
        a_eln=dict(
            component='StringEditQuantity'))
    
    building = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_buildings)))
    
    room_category = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_room_categories)))
      
    #instructed_user = Quantity(
    #    type=user_reference,
    #    shape=['*'],
    #    description='The corresponding user for the activity.',
    #    a_eln=dict(component='AuthorEditQuantity'),
    #)

    # SUBSECTIONS
    instructed_persons = SubSection(section_def=UMR_InstructedPerson, repeats = True)
    files = SubSection(section_def=UMR_FileWithDescription, repeats=True)
    instruments = SubSection(section_def=InstrumentReference,repeats = True)
    chemicals = SubSection(section_def=EntityReference, repeats = True)

    def normalize(self, archive, logger):
        super(UMR_Room, self).normalize(archive, logger)

        # Create lab_id
        if self.building and self.room_number and self.short_name:
            building_number = self.building.split()[0].replace('|','')
            room_number = self.room_number.replace(' ','')
            short_name = self.short_name.replace(' ', '_')
            self.lab_id = f"{building_number}_{room_number}_{short_name}"
        else: log_error(self, logger, "Please enter a short_name, a building and a room_number and save the entry to generate the lab_id")

        # Sort List of instructed persons (by date)
        #if all(person.datetime for person in self.instructed_persons):
        #    list=self.instructed_persons
        #    list.sort(key=lambda x: x.datetime)
        #    self.instructed_persons = list
        #else:
        #    log_error(self, logger, "Please make sure that for all instructed persons the date of safety instruction is given!")

        # COLLECT INSTRUMENTS REFERENCING THIS ROOM
        references = collect_referencing_entries(self, archive, logger, "UMR_Instrument")
        list_ref =[]
        for ref in references:
            instrument_ref = UMR_InstrumentReference(
                reference = ref)
            list_ref.append(instrument_ref)
        self.instruments = list_ref
        # Normalize Sections
        for instrument in self.instruments:
            instrument.normalize(archive, logger)

        # COLLECT CHEMICAL LOTS REFERENCING THIS ROOM
        references = collect_referencing_entries(self, archive, logger, "UMR_ChemicalLot")
        list_ref =[]
        for i, ref in enumerate(references):
            chemical_ref=UMR_ChemicalReference(
                reference=ref)
            #chemical_ref.name = chemical_ref.reference.name
            #chemical_ref.normalize(archive, logger)
            list_ref.append(chemical_ref)        
        # SOrt chemicals 
        self.chemicals = list_ref
        chemicals_list = [chemical for chemical in self.chemicals]
        chemicals_list.sort(key=lambda x: x.reference.order_date)
        self.chemicals = chemicals_list
        # Normalize Sections
        for chemical in self.chemicals:
            chemical.normalize(archive, logger)


"""
        self.instruments = []
        query = {
            'entry_references.target_entry_id': archive.metadata.entry_id,
            'entry_type': "UMR_Instrument"}
        search_result = UMR_search(archive, query)
        log_info(self, logger, f'INSTRUMENT-SEARCH-RESULT-LENGTH:{len(search_result.data)}')

        if search_result.data:
            # Extract data from search results
            for res in search_result.data:
                try:
                    upload_id, entry_id = res['upload_id'], res['entry_id']
                    instrument_ref = get_reference(upload_id, entry_id)
                    log_info(self, logger, f'INFORMATION ABOUT COLLECTED INSTRUMENTS --- UPLOAD_ID: {upload_id} | ENTRY_ID: {entry_id}')
                    self.instruments.append(instrument_ref)
                    #self.lots.append(lot_reference) # .append funktioniert nicht 
                    #list = self.instruments
                    #list.append(lot_reference)
                    #self.instruments = list
                except Exception as e:
                    log_error(self, logger, f"Error during processing (Collecting Instruments) --- EXEPTION:{e}")
        else: 
            log_warning(self, logger, f'No Instruments were found for this Room: {self.name}')

"""
        # COLLECT CHEMICAL LOTS REFERENCING THIS ROOM


################################ Instrument ################################


class UMR_Instrument(Instrument, EntryData):
    
    m_def = Section(
        categories=[UMRCreateCategory],
        a_eln=dict(
            hide=['datetime'],
            properties=dict(
                order=[
                    'name', 'short_name',
                    'instrument_category',
                    'supplier', 'link',
                    'room', 'description',
                    'files'])))
    
    lab_id = Quantity(type=str)

    name = Quantity(
        type=str,
        description="long understandable name.",
        a_eln=dict(component='StringEditQuantity'),
    )

    short_name = Quantity(
        type=str,
        description="short name of the room - used in lab id.",
        a_eln=dict(component='StringEditQuantity'))
    
    supplier =  Quantity(
        type=MEnum(suggestions_supplier_instruments),
        description='Choose the name of the supplier from the dropdown list or type in a new one.',
         a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_supplier_instruments)))
    
    
    link = Quantity(
        type = str,
        description="URL to the product on the supplier website",
        a_eln=dict(component='URLEditQuantity'))
    
    room = Quantity(
        type=Reference(UMR_Room.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))
    
    instrument_category = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_instrument_categories)))

    files = SubSection(section_def=UMR_FileWithDescription, repeats=True)
    
    chemicals = SubSection(section_def=EntityReference,repeats = True)
    
    instructed_persons = SubSection(section_def=UMR_InstructedPerson, repeats = True)



    def normalize(self, archive, logger):
        super(UMR_Instrument, self).normalize(archive, logger)

        # Generate lab_id
        if self.short_name and self.supplier:
            supplier_abbreviation = supplier_instruments_abbreviations[self.supplier]  
            short_name = self.short_name.replace(' ', '_')
            self.lab_id = f"{short_name}_{supplier_abbreviation}"
        else: log_error(self, logger, "Please enter a short_name and a supplier and save the entry to generate the lab_id")


m_package.__init_metainfo__()
