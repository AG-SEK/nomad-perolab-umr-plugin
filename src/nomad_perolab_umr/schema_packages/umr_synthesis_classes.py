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


#Impors Python
import numpy as np
import os

# Imports NOMAD
from nomad.metainfo import Quantity, SubSection, Section, SchemaPackage, Reference
from nomad.datamodel.data import EntryData
from nomad.datamodel.metainfo.basesections import CASPureSubstanceSection, PureSubstance, Entity, PubChemPureSubstanceSection, EntityReference
from nomad.metainfo import MEnum, Datetime
from nomad.datamodel.metainfo.eln import Chemical

# Imports HZB
from baseclasses.chemical_energy import Electrode, Environment
from baseclasses.solution import Solution, Ink, SolutionPreparationStandard, SolutionChemical
from baseclasses import ReadableIdentifiersCustom
from baseclasses.helper.utilities import get_reference, create_archive, get_entry_id_from_file_name


# Imports UMR
from .suggestions_lists import *
from .helper_functions import *
from .categories import *

from .umr_baseclasses import UMR_Room, UMR_Instrument

m_package = SchemaPackage(aliases=['UMR_schemas.umr_synthesis_classes']) 

################################ Chemical ################################


class UMR_AddChemicalLot(Entity):
    m_def = Section(
        a_eln=dict(
            hide=['name', 'lab_id', 'datetime'],
            properties=dict(
                order=[
                    'lot', 'order_date', 'order_number',
                    'mass', 'volume', 'costs', 'opened_on',
                    'room', 'instrument', 
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
        description="The specified lot or batch on the chemical",
        a_eln=dict(component='StringEditQuantity'),
    )

    opened_on = Quantity(
        type=Datetime,
        description='The date of opening the chemical.',
        a_eln=dict(component='DateTimeEditQuantity'), 
    )

    mass = Quantity(
        type=np.float64,
        unit='g',
        description='Mass in g.',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='g',
        ))

    volume = Quantity(
        type=np.float64,
        unit='ml',
        description='Volume in ml.',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='ml'))
    
    costs = Quantity(
        type=np.float64,
        description='Costs in Euros (€)',
        a_eln=dict(component='NumberEditQuantity'))
    
    room = Quantity(
        type=UMR_Room,
        a_eln=dict(component='ReferenceEditQuantity'))
    
    instrument = Quantity(
        type=UMR_Instrument,
        a_eln=dict(component='ReferenceEditQuantity'))

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
            
            elif not self.m_parent.lab_id:
                log_error(self, logger, f"The lab_id of the chemical must be defined. Please give the name and supplier and save the archive again. The ID is then generated automatically.")
                return
              
            elif not self.lot or not (self.mass or self.volume):
                log_error(self, logger, f"Please always give at least the lot (lot, charge or batch), the order date (estimate if unknownn) and either the mass or the volume (depending if solid or liquid)")
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
                    entry = UMR_ChemicalLot(
                        chemical = get_reference(self.m_parent.m_root().metadata.upload_id, self.m_parent.m_root().metadata.entry_id), 
                        lot = self.lot,
                        lab_id = lab_id,
                        order_date = self.order_date,
                        order_number = self.order_number,
                        opened_on = self.opened_on,
                        mass = self.mass,
                        volume = self.volume,
                        current_storage = 100,
                        description = self.description,
                        costs = self.costs,
                        room = self.room,
                        instrument = self.instrument,
                    )
                    create_archive(entry, archive, file_name)
                    
                    #entry_id = get_entry_id_from_file_name(file_name, archive)
                    #entry_ref = get_reference(archive.metadata.upload_id, entry_id)
                    #list.append(entry_ref)
                    #self.m_parent.lots = list
                    # Manual Filling of List, not neccesary

                    # Call normalizer of UMR_Cehmical to update list
                    self.m_parent.normalize(archive, logger)
                    # Delete Add Chemical lot section
                    self.m_parent.add_chemical_lot = UMR_AddChemicalLot()

        super(UMR_AddChemicalLot, self).normalize(archive, logger)



class UMR_Chemical(PureSubstance, Chemical, EntryData):
    m_def = Section(
        categories=[UMRCreateCategory],
        a_eln=dict(
            hide=['datetime'],
            properties=dict(
                order=[
                    'name', 'substance_name', 'short_name', 'supplier',
                    'product_number', 'link_to_product',
                    'state_of_matter', 'chemical_formula',
                    'lab_id',
                    'description',
                    'pure_substance', 'cas_pure_substance',
                    'elemental_composition',
                    'add_chemical_lot'])))

    lab_id = Quantity(
        type=str,
        description="Automatically generated ID")


    name = Quantity(
        type=str,
        description="long understandable name.",
        a_eln=dict(component='StringEditQuantity'),
    )
    
    short_name = Quantity(
        type=str,
        description="short name or abbreviation of the chemical - used in lab id.",
        a_eln=dict(component='StringEditQuantity'),
    )

    substance_name = Quantity(
        type=str,
        description="The long name of the chemical substance. This is used for the search in the PubChem Library.",
        a_eln=dict(component='StringEditQuantity'),
    )

    supplier = Quantity(
        type=MEnum(suggestions_supplier_chemicals),
        description='Choose the name of the supplier from the dropdown list or type in a new one.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_supplier_chemicals)))
    
    link_to_product = Quantity(
        type = str,
        description="URL to the product on the supplier website",
        a_eln=dict(component='URLEditQuantity')
    )

    product_number = Quantity(
        type=str,
        a_eln=dict(component='StringEditQuantity'))
    
    category = Quantity(
        type=MEnum(suggestions_chemical_category),
        description="The category or type of chemical (e.g. precursor, solvent)",
        a_eln=dict(component='EnumEditQuantity')
    )

    state_of_matter = Quantity(
        type=MEnum('Liquid', 'Solid', 'Gas'),
        a_eln=dict(component='EnumEditQuantity')
    )

    safety_data_sheet = Quantity(
        type=str,
        a_eln=dict(
            label = 'Safety Data Sheet (EN)',
            component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    
    safety_data_sheet_2 = Quantity(
        type=str,
        a_eln=dict(
            label = 'Sicherheitsdatenblatt (DE)',
            component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    
    operating_instructions = Quantity(
        type=str,
        a_eln=dict(
            label = 'Operating Instructions (EN)',
            component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    
    operating_instructions_2 = Quantity(
        type=str,
        a_eln=dict(
            label = 'Betriebsanweisung (DE)',
            component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))

    lots = Quantity(
        type = UMR_AddChemicalLot, # Because UMR_ChemicalLot is not yet defined
        shape = ['*'],
    )  


    pure_substance = SubSection(
        section_def=PubChemPureSubstanceSection,
        description="""Section with properties describing the substance.""",
        )

    cas_pure_substance = SubSection(
        section_def=CASPureSubstanceSection,
        description="""Section with properties describing the substance.""",
    )

    add_chemical_lot = SubSection(
        section_def = UMR_AddChemicalLot
    )

    def normalize(self, archive, logger):



        # Generate lab_id
        if self.short_name and self.supplier:
            supplier_abbreviation = supplier_chemicals_abbreviations[self.supplier]  
            short_name = self.short_name.replace(' ', '_')
            self.lab_id = f"{short_name}_{supplier_abbreviation}"
        else: log_error(self, logger, "Please enter a short_name and a supplier and save the entry to generate the lab_id")

        # Create PubChemPureSubstanceSection and get Information from PubChem
        if not self.pure_substance.pub_chem_cid and self.substance_name:
            pubchem_section = PubChemPureSubstanceSection(name=self.substance_name)
            pubchem_section.normalize(archive, logger)
            self.pure_substance = pubchem_section   
            
            # Create CasPureSubstanceSection and get Information from CAS (based o cas_number from PubChem section)
            if self.pure_substance.cas_number:
                cas_section = CASPureSubstanceSection(cas_number=self.pure_substance.cas_number)
                cas_section.normalize(archive, logger)
                self.cas_pure_substance = cas_section   
            
            # Fill molecular formula (based on Pub chem Section)
            if self.pure_substance.molecular_formula and not self.chemical_formula:
                self.chemical_formula = self.pure_substance.molecular_formula

            # Info: elemental composition is filled from formula of pure_substance subsection
            # This happens only if elemental composition is empty, so delete it first if it is wrong and then normalize again 

        # Delete deleted Lots from list
        if self.lots:
            list = self.lots
            for item in list:
                log_warning(self, logger, f"ITEM.LOT {item.lot}")
                try:
                    item.m_resolved()
                except:
                    log_warning(self, logger, f"EXCEPTION {item.lot}")
                    list.remove(item)

        #   self.lots = list
# TODO: Ask in discrod how to ckeck if a reference still exists programmatically.


        #search for all Chemical Lots referencing this Chemical
        references = collect_referencing_entries(self, archive, logger, "UMR_ChemicalLot")
        self.lots = references
        self.lots.sort(key=lambda x: x.order_date)



        
        #query = {
        #    'entry_references.target_entry_id': archive.metadata.entry_id,
        #    'entry_type': "UMR_ChemicalLot"}
        #search_result = UMR_search(archive, query)
        #log_info(self, logger, f'CHEMICAL-LOT-SEARCH-RESULT-DATA:{search_result.data}---LENGTH:{len(search_result.data)}')

        #if search_result.data:
            # Extract data from search results
        #    for res in search_result.data:
        #        try:
        #            upload_id, entry_id = res['upload_id'], res['entry_id']
         #           # Create measurement reference
        #            lot_reference = get_reference(upload_id, entry_id)
        #            #lot_reference.normalize(archive, logger)
         #           log_info(self, logger, f'INFORMATION ABOUT COLLECTED LOTS --- UPLOAD_ID: {upload_id} | ENTRY_ID: {entry_id}')
         #           #self.lots.append(lot_reference) # .append funktioniert nicht 
         #           list = self.lots
          #          list.append(lot_reference)
          #          self.lots = list
          #      except Exception as e:
          #          log_error(self, logger, f"Error during processing (Collecting Chemical Lots) --- EXEPTION:{e}")
        #else: 
        #    log_warning(self, logger, f'No Chemical Lots were found for this Chemical: {self.lab_id}')

        super(UMR_Chemical, self).normalize(archive, logger)


class UMR_ChemicalLot(UMR_AddChemicalLot, EntryData):   ## ggf. hier noch von Chemical o.ä. erben
    m_def = Section(
        categories=[UMRCollectionCategory],
        label_quantity = 'lab_id',
        a_eln=dict(
            hide=['name', 'add_lot', 'datetime'],
            properties=dict(
                order=[
                    'lab_id', 'chemical', 'lot',
                    'order_date', 'order_number',
                    'mass', 'volume', 'costs', 'opened_on', 
                    'current_storage', 'room', 'instrument', 'description',
                ])))

    chemical = Quantity(
        type=Reference(UMR_Chemical.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    current_storage = Quantity(
        type=np.float64,
        description='Current storage in %.',
        a_eln=dict(component='NumberEditQuantity')
    )


    def normalize(self, archive, logger):        
        super(UMR_ChemicalLot, self).normalize(archive, logger)

        #if self.current_storage and self.opened_on:
            # Set Name
        #    if self.mass:
        #        current_mass = round(self.current_storage*0.01*self.mass, 2)
        #        self.name = f'{self.lab_id} opened on {self.opened_on.date()} - {current_mass.magnitude}/{self.mass} ({self.current_storage}%)'
        #    elif self.volume:
        #        current_volume = round(self.current_storage*0.01*self.volume, 2)
        #        self.name = f'{self.lab_id}_{self.lot}_{self.opened_on.date()}-{current_volume}/{self.volume} ({self.current_storage}%)'
          



################################ Solution ################################
class UMR_SolutionChemical(SolutionChemical):

    chemical = Quantity(
        type=Reference(UMR_ChemicalLot.m_def),
        a_eln=dict(component='ReferenceEditQuantity'),
        label="Chemical Lot")

    chemical_2 = SubSection(
        section_def=PubChemPureSubstanceSection,
        label="Chemical PubChem")
     
    # Again defined here only because of units 
    chemical_volume = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000918', 'https://purl.archive.org/tfsco/TFSCO_00002158'],
        type=np.dtype(np.float64),
        unit=('ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='ml'))

    chemical_mass = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000125', 'https://purl.archive.org/tfsco/TFSCO_00005020'],
        type=np.dtype(np.float64),
        unit=('mg'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg'))

    concentration_mass = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000033'],
        type=np.dtype(np.float64),
        unit=('mg/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mg/ml'))

    concentration_mol = Quantity(
        links=['http://purl.obolibrary.org/obo/PATO_0000033'],
        type=np.dtype(np.float64),
        unit=('mol/ml'),
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='mmol/ml'))
    
    
    short_name = Quantity(
        type =str,
        a_eln=dict(component='StringEditQuantity'))
    
    lab_id = Quantity(type =str)
    

    def normalize(self, archive, logger):
        super(UMR_SolutionChemical, self).normalize(archive, logger)

        if self.chemical:
            self.chemical_2 = self.chemical.chemical.pure_substance.m_copy(deep=True)
            self.lab_id = self.chemical.lab_id
            self.short_name = self.chemical.chemical.short_name

        if self.short_name:
            if self.chemical_volume:
                self.name = f"{self.short_name} {self.chemical_volume}"
            elif self.chemical_mass:
                self.name = f"{self.short_name} {self.chemical_mass}"
            else:
                self.name = self.short_name



class UMR_StandardSolution(Solution, EntryData):
    m_def = Section(
        categories=[UMRCreateCategory],
        a_eln=dict(
            hide=[
                'components', 'elemental_composition',
                'lab_id',
                'solution_id', # currently not needed
                'method', 'temperature', 'time', 'speed', 'solvent_ratio' # This is entered in preparation SubSection
                ],
            properties=dict(
                order=[
                    'name', 'datetime', 'description',
                    "preparation", "solute", "solvent",
                    "other_solution", "additive", "storage", 'properties',
                ])))

    solute = SubSection(section_def=UMR_SolutionChemical, repeats=True)
    solvent = SubSection(section_def=UMR_SolutionChemical, repeats=True)
    additive = SubSection(section_def=UMR_SolutionChemical, repeats=True)
    preparation = SubSection(section_def=SolutionPreparationStandard)

    def normalize(self, archive, logger):        
        super(UMR_StandardSolution, self).normalize(archive, logger)



class UMR_Solution(Solution, EntryData):
    m_def = Section(
        categories=[UMRCollectionCategory],
        #a_display = dict(visible = ['standard_solution', 'description', 'name', 'datetime'],
        #                 editable = ['description', 'name'],
        #                 order = ['name', 'description', 'datetime']),
# Klappt so nicht!!!!!!!!!!
        a_eln=dict(
            hide=[
                'components', 'elemental_composition',
                'lab_id',
                'solution_id', # currently not needed
                'method', 'temperature', 'time', 'speed', 'solvent_ratio' # This is entered in preparation SubSection
                ],
            properties=dict(
                order=[
                    'standard_solution', 'load_standard_solution',
                    'name', 'datetime', 'description',
                    "preparation", "solute", "solvent",
                    "other_solution", "additive", "storage", 'properties'])))

    standard_solution = Quantity(
        type=Reference(UMR_StandardSolution.m_def),
        description="Fill this field to retrieve data from a Standard Solution",
        a_eln=dict(component='ReferenceEditQuantity', showSectionLabel = True))

    load_standard_solution = Quantity(
        type=bool,
        default=False,
        a_eln=dict(component='ActionEditQuantity'))
    
    solute = SubSection(section_def=UMR_SolutionChemical, repeats=True)
    solvent = SubSection(section_def=UMR_SolutionChemical, repeats=True)
    additive = SubSection(section_def=UMR_SolutionChemical, repeats=True)
    preparation = SubSection(section_def=SolutionPreparationStandard)


    def normalize(self, archive, logger):        
        # BUTTON: load standard solution
        if self.load_standard_solution and self.standard_solution:
            self.load_standard_solution = False
            
            self.description = self.standard_solution.description
            self.preparation = self.standard_solution.preparation
            self.solute = self.standard_solution.solute
            self.solvent = self.standard_solution.solvent
            self.other_solution = self.standard_solution.other_solution
            self.additive = self.standard_solution.additive
            self.storage = self.standard_solution.storage
            self.properties = self.standard_solution.properties

        super(UMR_Solution,self).normalize(archive,logger)





################################ Electrode ################################

class UMR_Electrode(Electrode, EntryData):
    m_def = Section(
        a_eln=dict(hide=['users', 'components', 'elemental_composition', 'origin'],
                   properties=dict(
            order=[
                "name", "lab_id",
                "chemical_composition_or_formulas"
            ])))




################################ Environment ################################

class UMR_Environment(Environment, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users', 'components', 'elemental_composition',
                'origin'],
            properties=dict(
                editable=dict(
                    exclude=["chemical_composition_or_formulas"]),
                order=[
                    "name",
                    "lab_id",
                    "chemical_composition_or_formulas",
                    "ph_value",
                    "solvent"])))

    environment_id = SubSection(
        section_def=ReadableIdentifiersCustom)








################################ Ink ################################


class UMR_Ink(Ink, EntryData):
    m_def = Section(
        a_eln=dict(
            hide=[
                'users', 'components', 'elemental_composition',
                'chemical_formula'],
            properties=dict(
                order=[
                    "name",
                    "method",
                    "temperature",
                    "time",
                    "speed",
                    "solvent_ratio"])),
        a_template=dict(
            temperature=45,
            time=15,
            method='Shaker'))
    


m_package.__init_metainfo__()
