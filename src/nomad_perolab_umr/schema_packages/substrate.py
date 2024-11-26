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
import os


# Imports Nomad
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.metainfo import Quantity, SubSection, Section, Package, Reference, Datetime, MEnum, SchemaPackage
from nomad.metainfo.metainfo import SectionProxy
from nomad.datamodel.metainfo.basesections import Entity


# Imports HZB/Michael Götte
from baseclasses.solar_energy import Substrate
from baseclasses.helper.utilities import get_reference
from baseclasses.helper.utilities import get_reference, create_archive, get_entry_id_from_file_name


# Imports UMR
from .suggestions_lists import *
from .helper_functions import *
from .categories import *

from .umr_baseclasses import UMR_FileWithDescription
from .batch import UMR_Batch
from .umr_reference_classes import UMR_EntityReference

m_package = SchemaPackage(aliases=['UMR_schemas.substrate']) 


################################ SUBSTRATE ################################
#from nomad.datamodel.metainfo.annotations import Filter, SectionDisplayAnnotation

class LabelMEnumTest(EntryData):
    m_def=Section()
    
    suggestions_list = ["A", "B", "C"]
    enumeration = Quantity(
        label="Test",
        type=MEnum(suggestions_list),
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_list)))
    
class LabelMEnumTestAELN(EntryData):
    m_def=Section()
    
    suggestions_list = ["A", "B", "C"]
    enumeration = Quantity(
        type=MEnum(suggestions_list),
        a_eln=dict(
            label="Test",
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_list)))

class LabelMEnumTestWithoutLabel(EntryData):
    m_def=Section()
    
    suggestions_list = ["A", "B", "C"]
    enumeration = Quantity(
        type=MEnum(suggestions_list),
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_list)))

class ELNAnnotationTestDisplay(EntryData):
    m_def = Section(
        a_display=dict(  #SectionDisplayAnnotation
            visible=dict(
                exclude=['quantity_2'])))
            
    quantity_1 = Quantity(type=str)
    quantity_2 = Quantity(type=str)
    quantity_3 = Quantity(type=str)
    quantity_4 = Quantity(type=str)

              
class ELNAnnotationTestELN(EntryData):
    m_def = Section(
        a_eln=dict(
            properties=dict( #Filter
                visible=dict(
                    exclude=['quantity_3']))))

    quantity_1 = Quantity(type=str)
    quantity_2 = Quantity(type=str)
    quantity_3 = Quantity(type=str)
    quantity_4 = Quantity(type=str)
                     

class ELNAnnotationTestHide(EntryData):
    m_def = Section(
        a_eln=dict(
            hide=['quantity_4']))

    quantity_1 = Quantity(type=str)
    quantity_2 = Quantity(type=str)
    quantity_3 = Quantity(type=str)
    quantity_4 = Quantity(type=str)


class SliderTest(EntryData):
     m_def=Section()
     slider_test = Quantity(
        type=int,
        a_eln=dict(component='SliderEditQuantity', minValue=1, maxValue=20, default=1))


#class UserTest(EntryData):
#     m_def=Section()
#     user = Quantity(
#        type=user,
#        a_eln=dict(component='AuthorEditQuantity'),
#)
    
#########################################################


class UMR_Substrate(Substrate):
    m_def = Section()

    batch = Quantity(
        type=Reference(UMR_Batch.m_def),
        a_eln=dict(component='ReferenceEditQuantity', showSectionLabel=True))
    
    supplier = Quantity(
        type=MEnum(suggestions_supplier),
        description='Choose the name of the supplier from the dropdown list or type in a new one.',
        a_eln=dict(
            label="supplier",
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_supplier)))

    substrate_area = Quantity(
        type=np.float64,
        description='Is automatically filled in if width and length are given.',
        unit='cm**2',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm**2'))
    
    width = Quantity(
        type=np.float64,
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    length = Quantity(
        type=np.float64,
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    substrate_thickness = Quantity(
        type=np.float64,
        unit='meter',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mm'))
    
    substrate_material = Quantity(
        type=str,
        description='Choose the name of the material from the dropdown list or type in a new one.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_substrate_material)))

    conducting_layer = Quantity(
        type=str,
         description='Choose the name of the condcuting layer from the dropdown list or type in a new one.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_conducting_material)))
    
    conducting_layer_thickness = Quantity(
        type=np.float64,
        unit='nm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='nm'))

    structuring = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_structuring)))
    
    surface_resistivity = Quantity(
        type=np.float64,
        unit='ohm',  # ohm/sq
        a_eln=dict(component='NumberEditQuantity'))
    
    transmission = Quantity(
        type=np.float64,
        description='Transmission value as float between 0 and 1',
        a_eln=dict(
            component='NumberEditQuantity',
            maxValue=1))
        
    samples = SubSection(
        description='List of Solar Cells on this substrate',
        sub_section = UMR_EntityReference, repeats=True)

    
    def normalize(self, archive, logger):
        super(UMR_Substrate,self).normalize(archive,logger)

        # Calculate substrate area
        if self.width and self.length:
            self.substrate_area = self.width * self.length

        # Fill hidden similar HZB baseclasses quantities, because of underlaying normalization
        if self.substrate_material:
            self.substrate = self.substrate_material            # Micha called the substrate_material only substrate
        if self.conducting_layer:
            self.conducting_material = [self.conducting_layer]  # Micha used a list of conducting_materials
        if self.substrate_area:
            self.solar_cell_area = self.substrate_area          # Micha called the substrate_area solar_cell_area)
        # Adopt pixel area from (first) referenced solar cell area if possible
        #if self.samples:
        #    self.pixel_area = self.samples[0].reference.area         # ONLY VALID IF ALL PIXELS HAVE THE SAME SIZE!
        






### Standard Substrate Classes (like Chemical and ChemicalLot) ###

class UMR_AddStandardSubstrateLot(Entity):
    m_def = Section(
        a_eln=dict(
            hide=['name', 'lab_id', 'datetime'],
            properties=dict(
                order=[
                    'lot', 'order_date', 'order_number',
                    'amount', 'opened_on', 
                    'add_lot',
                    'description',
                ])))


    order_date = Quantity(
        type=Datetime,
        description='The date of order.',
        a_eln=dict(component='DateTimeEditQuantity'),
    )

    order_number = Quantity(
        type=str,
        description="The order number from the order confirmation.",
        a_eln=dict(component='StringEditQuantity'),
    )

    lot = Quantity(
        type=str,
        description="The specified lot or batch on the substrate",
        a_eln=dict(component='StringEditQuantity'),
    )

    opened_on = Quantity(
        type=Datetime,
        description='The date of opening the substrate.',
        a_eln=dict(component='DateTimeEditQuantity'), 
    )

    amount = Quantity(
        type=np.float64,
        description='Number of substrates',
        a_eln=dict(
            component='NumberEditQuantity'))
 

    add_lot = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ActionEditQuantity')
    )

    def normalize(self, archive, logger):

    # BUTTON: add lot
        if self.add_lot:
            self.add_lot = False
            
            # Get directory (folder)
            directory, filename = os.path.split(self.m_root().metadata.mainfile)

            if directory == "":
                log_error(self, logger, f"Please always put the Chemical in a separate folder. After doing so, you can create lots, which are automatically stored in the same folder.")
                return
        
            if not self.m_parent.lab_id:
                log_error(self, logger, f"The lab_id of the Standard Substrate must be defined. Please give the name and supplier and save the archive again. The ID is then generated automatically.")
                return
            
            elif not self.lot or not self.amount:
                log_error(self, logger, "Please always give at least the name of the lot and the amount (number of substrates)")
                return
            
            else:
                # Get list with existing lots or create empty list
                if self.m_parent.lots:
                    list = self.m_parent.lots
                else:
                    list = []

                if any(item.lot == self.lot for item in list):
                    log_error(self, logger, f"The lot was not added, because it already exists")
                else:
                    lab_id = f"{self.m_parent.lab_id}_{self.lot}"
                    file_name = f"{directory}/{lab_id}.archive.json"
                    entry = UMR_StandardSubstrateLot(
                        standard_substrate = get_reference(self.m_parent.m_root().metadata.upload_id, self.m_parent.m_root().metadata.entry_id), 
                        lot = self.lot,
                        lab_id = lab_id,
                        order_date = self.order_date,
                        order_number = self.order_number,
                        opened_on = self.opened_on,
                        amount = self.amount,
                        current_storage = self.amount,
                        description = self.description
                    )
                    create_archive(entry, archive, file_name)
                  
                    self.m_parent.normalize(archive, logger)
                    self.m_parent.add_substrate_lot = None

        super(UMR_AddStandardSubstrateLot, self).normalize(archive, logger)

class UMR_StandardSubstrate(UMR_Substrate, EntryData):
    m_def = Section(
        categories=[UMRCreateCategory],
        a_eln=dict(
            hide=['conducting_material', 'substrate', 'solar_cell_area', 'pixel_area',
                  'datetime', 'batch', 'samples'],
            properties=dict(
                order=[
                    'name', 'short_name', 'link',
                    'supplier', 'product_number',
                    'substrate_material', 'substrate_thickness',
                    'conducting_layer', 'conducting_layer_thickness',
                    'substrate_area', 'length', 'width', 
                    'number_of_pixels',
                    'description',
                    'structuring','surface_resistivity','transmission'])))
    

    name = Quantity(
        type=str,
        description="long understandable name.",
        a_eln=dict(component='StringEditQuantity'),
    )

    supplier = Quantity(
        type=MEnum(suggestions_supplier_chemicals),
        description='Choose the name of the supplier from the dropdown list or type in a new one.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_supplier_chemicals)))
    
    short_name = Quantity(
        type=str,
        description="short name or abbreviation of the substrate - used in lab id.",
        a_eln=dict(component='StringEditQuantity'),
    )

    lab_id = Quantity(type=str)

    link = Quantity(
        type = str,
        description="URL to the product on the supplier website",
        a_eln=dict(component='URLEditQuantity'))
    
    product_number = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))
    
    lots = Quantity(
        type = ArchiveSection,
        shape = ['*'],
    )  

    files = SubSection(section_def=UMR_FileWithDescription, repeats=True)

    add_substrate_lot = SubSection(
        section_def = UMR_AddStandardSubstrateLot
    )

    def normalize(self, archive, logger):        
        
        # Generate lab_id
        if self.short_name and self.supplier:
            supplier_abbreviation = supplier_chemicals_abbreviations[self.supplier]  
            short_name = self.short_name.replace(' ', '_')
            self.lab_id = f"{short_name}_{supplier_abbreviation}"
        else: log_error(self, logger, "Please enter a short_name and a supplier and save the entry to generate the lab_id")


        #search for all Standard SUbstrate Lots referencing this Standard Substrate
        self.lots = []
        query = {
            'entry_references.target_entry_id': archive.metadata.entry_id,
            'entry_type': "UMR_StandardSubstrateLot"}
        search_result = UMR_search(archive, query)
        log_info(self, logger, f'SUBSTRATE-LOT-SEARCH-RESULT-DATA:{search_result.data}---LENGTH:{len(search_result.data)}')

        if search_result.data:
            # Extract data from search results
            for res in search_result.data:
                try:
                    upload_id, entry_id = res['upload_id'], res['entry_id']
                    # Create measurement reference
                    lot_reference = get_reference(upload_id, entry_id)
                    #lot_reference.normalize(archive, logger)
                    log_info(self, logger, f'INFORMATION ABOUT COLLECTED LOTS --- UPLOAD_ID: {upload_id} | ENTRY_ID: {entry_id}')
                    #self.lots.append(lot_reference) # .append funktioniert nicht 
                    list = self.lots
                    list.append(lot_reference)
                    self.lots = list
                except Exception as e:
                    log_error(self, logger, f"Error during processing (Collecting Substrate Lots) --- EXEPTION:{e}")
        else: 
            log_warning(self, logger, f'No Substrate Lots were found for this Chemical: {self.lab_id}')
        

        super(UMR_StandardSubstrate, self).normalize(archive,logger)


class UMR_StandardSubstrateLot(UMR_AddStandardSubstrateLot, EntryData): 
    m_def = Section(
        categories=[UMRCollectionCategory],
        label_quantity = 'lab_id',
        a_eln=dict(
            hide=['name', 'add_lot', 'datetime'],
            properties=dict(
                order=[
                    'lab_id', 'standard_substrate', 'lot',
                    'order_date', 'order_number',
                    'amount', 'opened_on', 
                    'current_storage', 'description',
                ])))

    standard_substrate = Quantity(
        type=UMR_StandardSubstrate,
        a_eln=dict(component='ReferenceEditQuantity'))

    current_storage = Quantity(
        type=np.float64,
        description='Current storage',
        a_eln=dict(component='NumberEditQuantity')
    )


    def normalize(self, archive, logger):        
        super(UMR_StandardSubstrateLot, self).normalize(archive, logger)


##### External and Internal Substrate #####

class UMR_ExternalSubstrate(UMR_Substrate, EntryData):
    m_def = Section(
        categories=[UMRCollectionCategory],
        label='External Substrate',
        label_quantity = 'lab_id',
        a_eln=dict(
            hide=[
                'conducting_material', 'substrate', 'solar_cell_area', 'pixel_area'],
            properties=dict(
                order=[
                    'name', 'datetime', 'lab_id','supplier',
                    'batch',
                    'substrate_material','substrate_thickness',
                    'conducting_layer', 'conducting_layer_thickness',
                    'substrate_area','length','width',
                    'number_of_pixels',
                    'description',
                    'structuring','surface_resistivity','transmission'])))
   
    def normalize(self, archive, logger):
        super(UMR_ExternalSubstrate,self).normalize(archive,logger)

     

class UMR_InternalSubstrate(UMR_Substrate, EntryData):
    m_def = Section(
        categories=[UMRCollectionCategory],
        label='Internal Substrate',
        label_quantity = 'lab_id',
        a_eln=dict(
            hide=['conducting_material', 'substrate', 'solar_cell_area', 'pixel_area'],
            properties=dict(
                order=[
                    'name', 'datetime', 'lab_id', 'batch',
                    'group_number',
                    'supplier', 'standard_substrate_lot',
                    'substrate_material', 'substrate_thickness',
                    'conducting_layer', 'conducting_layer_thickness',
                    'substrate_area', 'length', 'width', 
                    'number_of_pixels',
                    'description',
                    'structuring','surface_resistivity','transmission'])))

    standard_substrate_lot = Quantity(
        #type=SectionProxy('UMR_StandardSubstrateLot'),
        #description="Click on the Pencil to choose a 'StandardSubstrateLot'. Afterwards click 'Load Data From Standard Substrate'. The ELN fields will be filled with the values from the corresponding Standard Substrate",
        # description not visible
        type=UMR_StandardSubstrateLot,
        a_eln=dict(component='ReferenceEditQuantity')
    )

    load_standard_substrate = Quantity(
        type=bool,
        label='Load data from Standard Substrate',
        description="Click on the Pencil to choose a 'UMR_StandardSubstrateLot'. Afterwards click 'Load Data From Standard Substrate'. The ELN fields will be filled with the values from the corresponding Standard Substrate",
        default=False,
        a_eln=dict(component='ActionEditQuantity'))
    
    group_number = Quantity(
        type=int,
        a_eln=dict(component='NumberEditQuantity'))
    # Brauche ich die Group-number wirklich??? Wird demnäcsht gelöscht

    standard_substrate_lot_id = Quantity(type=str,)


    
    def normalize(self, archive, logger):        
        
        self.group_number = None # Die Quantity wird demnächst gelöscht. Brauche ich nicht.

        # BUTTON: load standard substrate
        if self.load_standard_substrate:
            self.load_standard_substrate = False
            
            if not self.standard_substrate_lot:
                log_error(self, logger, f"Please enter a reference in the standard_substrate_lot field to load the data from this Standard Substrate")
            else:
                standard_substrate_entry = self.standard_substrate_lot.standard_substrate
                
                self.name = standard_substrate_entry.name
                self.supplier = standard_substrate_entry.supplier
                self.substrate_material = standard_substrate_entry.substrate_material
                self.substrate_thickness = standard_substrate_entry.substrate_thickness
                self.conducting_layer = standard_substrate_entry.conducting_layer
                self.conducting_layer_thickness = standard_substrate_entry.conducting_layer_thickness
                self.substrate_area = standard_substrate_entry.substrate_area
                self.length = standard_substrate_entry.length
                self.width = standard_substrate_entry.width
                self.number_of_pixels = standard_substrate_entry.number_of_pixels
                self.structuring = standard_substrate_entry.structuring
                self.surface_resistivity = standard_substrate_entry.surface_resistivity
                self.transmission = standard_substrate_entry.transmission
                self.description = standard_substrate_entry.description
                self.standard_substrate_lot_id = standard_substrate_entry.lab_id

        super(UMR_InternalSubstrate,self).normalize(archive,logger)


        # If no solar cells are referenced find solar cells which reference this substrate and add them to samples subsection
        #if not self.samples:
        #    self.samples = []
        #    references = collect_referencing_entries(self, archive, logger, 'UMR_InternalSolarCell') 
        #    for ref in references:
        #        solar_cell_reference = UMR_EntityReference(
        #            name='Solar Cell',
        #            reference=ref)
        #        solar_cell_reference.normalize(archive, logger)
        #        # Append solar cell reference to list
        #        self.samples.append(solar_cell_reference)
    
#from nomad.datamodel.metainfo.annotations import Filter, SectionDisplayAnnotation

class UMR_SubstrateForBatchPlan(UMR_InternalSubstrate, EntryData):
    
    m_def = Section(
        description="A Section which is used to create the substrate entry in the 'UMR_Batch Plan'. It inherits from 'UMR_InternalSubstrate', but does not display all quantities. Here you can choose to either load a standard substrate from an already existing 'UMR_StandardSubstrateLot' or you enter the parameters manually. Whenever possible please use standard substrates and if neccesary make some changes to the parameters (e.g. if you only use the pure glass side).",
        categories=[UMRSynthesisCategory],
        label='Substrate in Batch Plan',
        a_eln=dict(
            hide=['conducting_material', 'substrate', 'solar_cell_area', 'pixel_area',
                  'lab_id', 'datetime', 'batch', 'samples', 'group_number'],
            properties=dict(
                order=[
                    'standard_substrate_lot', 'load_standard_substrate',
                    'name',
                    'supplier',
                    'substrate_material', 'substrate_thickness',
                    'conducting_layer', 'conducting_layer_thickness',
                    'substrate_area', 'length', 'width', 
                    'number_of_pixels',
                    'description',
                    'structuring','surface_resistivity','transmission'])),)
        #_display=SectionDisplayAnnotation(
        #    visible=Filter(
        #        exclude=['conducting_material', 'substrate', 'solar_cell_area', 'pixel_area',
        #           'lab_id', 'datetime', 'batch', 'samples', 'group'])))



    def normalize(self, archive, logger):        
        # BUTTON: load standard substrate
        # if self.load_standard_substrate:
        #     self.load_standard_substrate = False
            
        #     if not self.standard_substrate:
        #         log_error(self, logger, f"Please enter a reference in the standard_substrate field to load the data from this Standard Substrate")
        #     else:
                
        #         ##self.name = self.standard_substrate.m_resolved().name
        #         self.supplier = self.standard_substrate.supplier
        #         self.substrate_material = self.standard_substrate.substrate_material
        #         self.substrate_thickness = self.standard_substrate.substrate_thickness
        #         self.conducting_layer = self.standard_substrate.conducting_layer
        #         self.conducting_layer_thickness = self.standard_substrate.conducting_layer_thickness
        #         self.substrate_area = self.standard_substrate.substrate_area
        #         self.length = self.standard_substrate.length
        #         self.width = self.standard_substrate.width
        #         self.number_of_pixels = self.standard_substrate.number_of_pixels
        #         self.structuring = self.standard_substrate.structuring
        #         self.surface_resistivity = self.standard_substrate.surface_resistivity
        #         self.transmission = self.standard_substrate.transmission
        #         self.description = self.standard_substrate.descriptio

        super(UMR_SubstrateForBatchPlan,self).normalize(archive,logger)


    
    # TODO: Find how many Internal_Substrates are referenced. Then you know how many are left




m_package.__init_metainfo__()
