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
import os
import numpy as np
import json

# Imports Nomad
from nomad.metainfo import Reference, Quantity, SubSection, Section, Package, MEnum, Datetime, SchemaPackage
from nomad.units import ureg
from nomad.datamodel.metainfo.basesections import BaseSection
from nomad.datamodel.data import EntryData, ArchiveSection, User


# Imports HZB
from baseclasses.experimental_plan import ParametersVaried, get_unit
from baseclasses.helper.execute_solar_sample_plan import set_value
from baseclasses import BaseProcess
from baseclasses.solar_energy import StandardSampleSolarCell
from baseclasses.helper.utilities import create_archive, get_entry_id_from_file_name, get_reference, update_archive
from baseclasses.solution import Solution



# Imports UMR
from .suggestions_lists import *
from .helper_functions import *
from .categories import *

from .umr_reference_classes import UMR_EntityReference
from .substrate import UMR_InternalSubstrate, UMR_SubstrateForBatchPlan
from .solar_cell import UMR_InternalSolarCell, UMR_BasicSample
from .batch import UMR_InternalBatch, UMR_Group
from .processes.process_baseclasses import UMR_ELNProcess, UMR_BaseProcess

m_package = SchemaPackage() 


################################ Standard Sample ################################

class UMR_StandardSampleSolarCell(StandardSampleSolarCell, EntryData):
    m_def = Section(
        categories=[UMRCollectionCategory],
        a_eln=dict(
            hide=['users','lab_id', 'datetime'],
            properties=dict(
                order=[
                    "name",
                    "architecture",
                    "encapsulation",
                    "substrate",
                    "processes",
                    'description',
                    'number_of_solar_cells_on_substrate',
                    'solar_cell_names',
                    'area',
                    'length',
                    'width',
                ])))
       
    number_of_solar_cells_on_substrate= Quantity(
        type=int,
        default = 4,
        a_eln=dict(component='NumberEditQuantity'))
    
    solar_cell_names = Quantity(   
        type=str,
        default = ['A', 'B', 'C', 'D'],
        description='Names of the solar cells, like 1,2,3,4 or A,B,C,D',
        shape=['number_of_solar_cells_on_substrate'],
        a_eln=dict(component='StringEditQuantity'))
    
    area = Quantity(
        type=np.float64,
        unit='cm**2',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm**2'))

    length = Quantity(
        type=np.float64,
        default = 0.6,
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    width = Quantity(
        type=np.float64,
        default = 0.6,
        unit='cm',
        a_eln=dict(component='NumberEditQuantity', defaultDisplayUnit='cm'))
    
    architecture = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_architecture)))
    
    encapsulation = Quantity(
        type=str,
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_encapsulation))) 
    
    substrate = Quantity(
        type=Reference(UMR_SubstrateForBatchPlan.m_def),
        a_eln=dict(component='ReferenceEditQuantity'))

    def normalize(self, archive, logger):
        super(UMR_StandardSampleSolarCell, self).normalize(archive, logger)

        # Calculate the solar cell area
        if self.width and self.length:
                self.area = self.width * self.length




################################ Variation of Processes ################################

class UMR_ParameterVariation(ParametersVaried):
    m_def = Section(
        label="Parameter variation for single parameter",
        description="In this section you choose a parameter, the unit and the values for a parameter variation. If you choose no unit automatically a correct unit will be displayed, after saving the entry. With the button you create 'varied_processes' in the parent Section 'UMR_VaryProcess'.",
        a_eln=dict(
            properties=dict(
                order=[
                    'parameter_path',
                    'parameter_unit',
                    'parameter_values',
                    'vary_process_by_given_parameter'])))

    parameter_path = Quantity(
        type=str,
        description="Choose a valid parameter path to the parameter you would like to vary. If the parameter is not in the list, please inform the Oasis administrator and use the other method to vary your process manually.",
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=list_path_variation_parameters)))

    parameter_unit = ParametersVaried.parameter_unit.m_copy()
    parameter_unit.description = "Choose a valid 'parameter path' above and then save the entry. This will automatically give you a valid unit for this parameter. Change it if neccesary"

    parameter_values = ParametersVaried.parameter_values.m_copy()
    parameter_values.description = "Enter your parameter values in this list. The list automatically increases once you entered a value. Use the button below to create the vareid processes."
 
    vary_process_by_given_parameter = Quantity(
        description="Use this button to create processes with the chosen Parameter variation. The processes are displayed in the parent section 'VaryProcess'. In there you can also make additional changes.",
        type=bool,
        default=False,
        a_eln=dict(component='ActionEditQuantity'))


    def normalize(self, archive, logger):
        super(UMR_ParameterVariation, self).normalize(archive, logger)

        # Determine unit automatically or log error
        if self.parameter_path and not self.parameter_unit:
            try:
                self.parameter_unit = get_unit(self.m_parent.process_reference,  self.parameter_path)
            except Exception as e:
                log_error(self, logger, f"{self.parameter_path} is not valid, can't find correct unit. Please check if the parameter is really part of your process. --- Exception: {e}")
                return

        # BUTTON: VARY PROCESS BY GIVEN PARAMETER
        if self.vary_process_by_given_parameter:
            self.vary_process_by_given_parameter = False

            if not self.parameter_values or not self.parameter_path or not self.parameter_unit:  
                log_error(self, logger, 'No parameter path, value or unit given. Please check.')
                return
            else:
                # Create with list of all parameters (Tupel: path, value, unit)
                list_parameters = []
                for value in self.parameter_values:
                    list_parameters.append((self.parameter_path, value, self.parameter_unit))

                # Append different proccesses for each parameter variation to SubSection varied_processes
                self.varied_processes = []
                for parameter_tuple in list_parameters:    
                    process = self.m_parent.process_reference.m_resolved().m_copy(deep=True)
                    path, value, unit = parameter_tuple
                    try:
                        # Change varied value in process entry
                        set_value(process, path, value, unit)
                    except Exception as e:
                        log_error(self, logger, f"Could not set {path} to {value} {unit}, most likely due to a faulty path or unit --- Exception: {e}")
                        return
                    # Create Process name
                    name = f" - {path.replace('/','-')}: {value} {unit}"
                    process.name += name.replace(" None","") # Remove Unit "None" by empty 
                    # Normalize and append varied process
                    process.normalize(archive, logger)
                    self.m_parent.varied_processes.append(process)
                
                # Fill fields in parent section "VaryProcess"
                self.m_parent.process_is_varied = True
                self.m_parent.number_of_variations = len(self.parameter_values)
                
                #self.m_parent.paremeter_variation=UMR_ParameterVariation() Maybe delete ParametersVariation Section afterwards -> make new empty one




class UMR_VaryProcess(ArchiveSection):
    m_def = Section(
        description="In this Section you can create varied processes based on a given process reference. There are 2 ways to vary a process. For a simple single numerical parameter variation click on the '+' next to the 'parameter_variation' SubSection and follow the instrcutions there. For a more complex parameter variation enter the 'number of variations' in the ELN field and click on the button 'Create Processes And Vary Afterwards'. Then navigate through the created processes in the 'varied_processes' SubSection and make your changes. Makes sure to first adapt the name of each process.",
        label_quantity='name',
        a_eln=dict(
            overview=1,
            properties=dict(
                editable=dict(exclude=["name"]),
                order=[
                    'name',
                    'process_is_varied',
                    'position_in_experimental_plan',
                    'process_reference',
                    'number_of_variations',
                    'create_processes_and_vary_afterwards',
                    'parameter_variation',
                    'varied_processes',])))

    name = Quantity(
        type=str,
        description="The name of the process taken from the referenced process entry below",
        a_eln=dict(component='StringEditQuantity')
    )

    position_in_experimental_plan = Quantity(
        type=int,
        description="The position in the experimental plan. Only change it, if you have to change the order of the processes. Then make sure that you adapt the positions in all processes. When saving the entry afterwards, the processes will be brought into the new changed order.",
        a_eln=dict(component='NumberEditQuantity')
    )

    process_reference = Quantity(
        type=UMR_ELNProcess,
        description="The reference to the process which can be varied in this Section.",
        a_eln=dict(component='ReferenceEditQuantity')
    )

    number_of_variations = Quantity(
        type=int,
        description='The number of variations for this process. If you want to change the process manually please enter the number of variations here and click "Create Processes And Vary Afterwards.',
        a_eln=dict(component='NumberEditQuantity')
    )

    create_processes_and_vary_afterwards = Quantity(
        type=bool,
        description="Use this button to manually vary a process. Enter the number of variations above and click this button. Afterwards the given number of processes is created in the 'varied_processes' SubSection. Navigate through the process in there and adapt them to your needs. Make sure to adapt the process names first.",
        default=False,
        a_eln=dict(component='ActionEditQuantity')
    )

    process_is_varied = Quantity(
        type=bool,
        description="This checkbox shows if this process is varied in this batch or not. The checkbox is checked automatically.",
        a_eln=dict(component='BoolEditQuantity')
    )

    parameter_variation = SubSection(
        section_def=UMR_ParameterVariation, label="Click (+) to vary a single parameter")
    
    varied_processes = SubSection(
        section_def=UMR_BaseProcess, repeats=True, label="List with varied processes")

    def normalize(self, archive, logger):
        super(UMR_VaryProcess, self).normalize(archive, logger)

        # Set name
        self.name=self.process_reference.name

        # BUTTON: CREATE PROCESSES AND VARY AFTERWARDS
        if self.create_processes_and_vary_afterwards:
            self.create_processes_and_vary_afterwards = False

            if not self.number_of_variations:
                log_error(self, logger, 'Please give the number of variations.')
                return
            else:
                # Append given number of unvaried processes to SubSection varied_processes
                self.varied_processes = []
                for i in range(self.number_of_variations):  
                    process = self.process_reference.m_resolved().m_copy(deep=True)
                    process.name += f" - {i}"
                    self.varied_processes.append(process)
                   
        # Check process_is_varied checkbox if neccesary
        if not self.varied_processes:
            self.process_is_varied = False
        else: self.process_is_varied = True
                    


################################ Selection of Processes ################################

class UMR_SelectProcessVariation(ArchiveSection):
    m_def = Section(
        description="This Section is used to choose a varied process f. Click 'Select Process' to choose this process. This process is then also displayed in the parent section 'UMR_SelectProcess'.", 
        label_quantity = 'name',
        a_eln=dict(
            #hide=[],
            editable=dict(exclude=["name"]),
            properties=dict(
                order=['select_process', 'name', 'process_is_selected', 'reference'])))

    name = Quantity(
        description='Name of the process',
        type=str) 
    
    reference = Quantity(
        description = "Reference to the process.",
        type=BaseProcess)

    process_is_selected = Quantity(
        description = "This button is checked if this Process Variation is chosen for this group.",
        type=bool,
        default=False,
        #a_eln=dict(component='BoolEditQuantity')
    )

    select_process = Quantity(
        description="Click this Button to choose the displayed process as process for the group. It automatically is transferred to the parent Sections.",
        type=bool,
        default=False,
        a_eln=dict(component='ActionEditQuantity'))


    def normalize(self, archive, logger):
        
        # BUTTON: Select Process Variation
        if self.select_process:
            self.select_process = False

            self.m_parent.selected_process = self.reference

            for process in self.m_parent.varied_processes:
                if process.name == self.name:
                    self.process_is_selected = True
                else:
                    process.process_is_selected = False
        
            self.m_parent.normalize(archive, logger)

        super(UMR_SelectProcessVariation, self).normalize(archive, logger)


class UMR_SelectProcess(ArchiveSection):
    m_def = Section(
        description="In this Section you select if a process is applied at all or which of the varied process is applied. Uncheck 'present' to not apply the process in thir group. If you have varied processes for this process they are displayed in the 'varied_processes Subsection.",
        label_quantity='display_name',
        a_eln=dict(
            editable=dict(exclude=['selected_process','display_name']),
            properties=dict(
                order=[
                    'selected_process',
                    'display_name',
                    'present']),
        ))
 
    present = Quantity(
        description = "Check this button if the process is present for this group. Uncheck if not. Default: True",
        type=bool,
        default=True,
        a_eln=dict(component='BoolEditQuantity')
    )

    selected_process = Quantity(
        description = "This is the reference to the chosen process",
        label='Process Reference',
        type=BaseProcess,
        a_eln=dict(component='ReferenceEditQuantity')
    )
 
    display_name = Quantity(
        type=str,
        label='Process',
        description='Automatically generated name of process, displayed in SubSections',
        a_eln=dict(component='StringEditQuantity')
    )
    
    #selected_file_name= Quantity(  # Helper for later
    #    type=str,
    #)

    varied_processes = SubSection(
        section_def = UMR_SelectProcessVariation, repeats = True, label="Choose your Process here")
    
    def normalize(self, archive, logger):

        # Automatically generate display_name
        if not self.present:
            self.display_name = f"- not present -"
        elif not self.selected_process:
            self.display_name = f"-> No process chosen yet"
        else:
            self.display_name = f"{self.selected_process.name}"
        
        super(UMR_SelectProcess, self).normalize(archive, logger)



class UMR_AdvancedSampleSettings(UMR_StandardSampleSolarCell):
    m_def = Section(
        categories=[UMRCollectionCategory],
        a_eln=dict(
            hide=['name', 'processes', 'datetime', 'substrate', 'lab_id', ],  
              properties=dict(
                order=[
                    'sample_type',
                    "number_of_solar_cells_on_substrate", 'solar_cell_names',
                    'length', 'width', 'area',
                    'architecture', 'encapsulation',
                    'description'])))


    def normalize(self, archive, logger):
        
        # Delete Propreties if Basic Sample and take dimensions from substrate reference
        self.number_of_solar_cells_on_substrate = 1
        self.solar_cell_names = ["X"]
        self.area  = self.m_parent.substrate.substrate_area
        self.length = self.m_parent.substrate.length
        self.width = self.m_parent.substrate.width
        self.architecture = None
        self.encapsulation = None
        self.description = None

        # # Load standard plan properties if Sample Type "Basic Sample" was chosen and then "Solar Cell" is chosen again
        # if self.sample_type == "Solar Cell" and self.number_of_solar_cells_on_substrate == 0:
        #     self.number_of_solar_cells_on_substrate = self.m_root().data.standard_plan.number_of_solar_cells_on_substrate
        #     self.solar_cell_names = self.m_root().data.standard_plan.solar_cell_names
        #     self.area  = self.m_root().data.standard_plan.area
        #     self.length = self.m_root().data.standard_plan.length
        #     self.width = self.m_root().data.standard_plan.width
        #     self.architecture = self.m_root().data.standard_plan.architecture
        #     self.encapsulation = self.m_root().data.standard_plan.encapsulation
        #     self.description = self.m_root().data.standard_plan.description

            


class UMR_GroupSettings(UMR_Group):
    m_def = Section(
        categories=[UMRCollectionCategory],
        description="This section  is used in the 'UMR_BatchPlan' to enter groups. All samples in the same group are identical! First enter the group description and group number. Then enter the number of substrates and the engraved substrate numbers. Check if the substrate is correct otherwise change it in the 'substrate' Subsection. Finally choose which processes are applied in this group. Do this in the 'select_processes' Subsection",
        label_quantity = 'display_name',
        a_eln=dict(
            hide=['name', 'lab_id', 'batch', 'datetime',
                  'samples', 'substrates',
                  'display_name'],
            properties=dict(
                order=[
                    "group_number", 'group_description',
                    'number_of_substrates', 'substrate_engraved_numbers',
                    'description',
                    'substrate', 'select_processes'])))
    
    #substrate = Quantity(
    #    type=Reference(UMR_SubstrateForBatchPlan.m_def),
    #    a_eln=dict(component='ReferenceEditQuantity'))

    substrate_engraved_numbers = Quantity(   
        type=str,
        desrciption='Numbers engraved on the substrates',
        shape=['number_of_substrates'],
        label="Enter the on the substrates engraved numbers",
        a_eln=dict(component='StringEditQuantity'))

    select_processes = SubSection(
        section_def = UMR_SelectProcess, repeats = True, label="Choose the Processes applied in this group")                
    
    substrate = SubSection(
        section_def=UMR_SubstrateForBatchPlan, label="Check the substrate used in this group")

    #advanced_solar_cell_settings = SubSection(
    #    section_def = UMR_StandardSampleSettings, repeats=False)

    def normalize(self, archive, logger):
        super(UMR_GroupSettings, self).normalize(archive, logger)

        # Warning if number of substrates does not match given engraved_numbers
        if self.substrate_engraved_numbers:
            if len(self.substrate_engraved_numbers) != self.number_of_substrates:
                log_error(self, logger, f"Number of substrates does not match with given engraved_numbers. Please check group: {self.group_number}")
                return
            
        # Warning if a substrate engraved number is used in a different group
        if self.substrate_engraved_numbers:
            # Create empty list and fill it with all engraved numbers from all groups
            all_engraved_numbers =[]
            for group in self.m_parent.groups_for_selection_of_processes:
                if group.substrate_engraved_numbers:
                    all_engraved_numbers += group.substrate_engraved_numbers 
            # Check if any engraved number is in the list more than one time and log error
            for engraved_number in self.substrate_engraved_numbers:
                if all_engraved_numbers.count(engraved_number) > 1:
                    log_error(self, logger, f"The engraved_number {engraved_number} was given for more than 1 substrate. Please Check.")
                    return

################################ Batch Plan ################################

class UMR_BatchPlan(BaseSection, EntryData):
    m_def = Section(
        categories=[UMRCreateCategory],
        desricption="This is the Section for Batch Planning. Follow the steps below step by step. You can always finde more information via the Help (?) Button next to each quantity or in the Section definitions.",
        label = "Create Batch Plan",
        a_eln=dict(
            hide=['lab_id'],
            properties=dict(
                editable=dict(exclude=["batch_id", 'batch_plan_pdf']),
                order=[
                    'name', 'batch_id',

                    # Checklist
                    "fill_general_info",
                    "choose_substrate",
                    "create_processes",
                    'move_processes_to_variation_subsection',
                    "vary_process",
                    'number_of_groups',
                    'create_groups_for_selection_of_processes',
                    "create_groups",
                    'create_pdf_plan',
                    'batch_plan_pdf',
                    "approved",
                    'create_batch',
                    'batch_was_created',

                    'description',


                    # Simple ELN fields
                    'datetime', 'end_time',
                    'responsible_person',
                    'batch_description', 'batch_number', 'architecture',

                    # Subsections
                    'substrate',
                    'standard_processes',
                    'standard_processes_for_variation',
                    'groups_for_selection_of_processes',
                    'created_entities',  
                ])))
   

    ### CHECKLIST

    fill_general_info = Quantity(
        type=bool,
        label="1. Enter general information about the batch into the ELN fields below the description field.",
        description="Fill the ELN fields 'start_date', 'end_date', 'responsible_person', 'batch_description' and 'batch_number' with the general information about the Batch. Feel free to add additiona information in the 'description' field. Save the entry afterwards, the 'batch_id' is then generated automatically.",
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
    choose_substrate = Quantity(
        type=bool,
        label="2. Enter the used substrate",
        description="Enter your used substrate by clicking on the '+' next to the 'substrate' Subsection. Load the used 'standard_substrate_lot' and if neccesary adjust the substrate parameters manually.",
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
    create_processes = Quantity(
        type=bool,
        label="3. Enter the used processes",
        description="Create your processes by clicking on the '+' next to the 'standard_processes' Subsection. Choose the desired ELN process type from the Dropdown List. Then either load a 'standard_process' or enter the parameters for a new processes manually.",
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
    vary_process = Quantity(
        type=bool,
        label="5. Vary parameters in one or more processes",
        description="There are 2 ways to vary a parameter. For a simple single numerical parameter variation lick on the  '+' next to the 'parameter_variation' Subsection and follow the instrcution there. For a more complex parameter variation enter the 'number_of_variations' in the ELN field and click on the button 'Create Processes And Vary Afterwards'. Then navigate throught the created processes in the 'varied_processes' subsection and make your changes. Make sure to first adapt the name of the processes.",
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
    create_groups = Quantity(
        type=bool,
        label="8. Select the processses and substrate for each group.",
        description="Enter the 'number_of_groups' first and then press the Button 'Create Groups For Selection Of Processes'. The groups are created in the 'groups_for_selection_of_processes' Subsection. Navigate through the groups and change the substrate parameters if neccesary. Then select the processes applied for this group.",
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
    approved = Quantity(
        type=bool,
        label="10. Approval of PDF batch plan.",
        description="This checkbox is checked by your supervisor if they approve your batch plan. If so you can create the full batch with the button 'Create Batch'. If your supervisor has comments, please change them before creating the batch. Anyhow if you created the batch with totally wrong parameters you can also delete all created samples, substrates, ... in the Batch folder and create them new.",
        default=False,
        a_eln=dict(component='BoolEditQuantity'))
    
   
    ### QUANTITES
    
    datetime = Quantity(
        type=Datetime,
        label="Start date",
        description='First day of the batch fabrication. Choose from the calendar.',
        a_eln=dict(component='DateTimeEditQuantity'), # Ich hätte hier leiber DateEditQuantities, aber die funktionieren nicht mehr.
    )
    end_time = Quantity(
        type=Datetime,
        label="End date",
        description='Last day of the batch fabrication. Choose from the calendar.',
        a_eln=dict(component='DateTimeEditQuantity'),
    )

    responsible_person = Quantity(
        type = MEnum(suggestions_persons),
        description = 'Person responsible for this batch. Choose from the Dropdown List. If your name does not appear, please inform the Oasis administrator.',
        a_eln = dict(
            label="responsible person", # For type MEnum a label has to be given i the a_eln section,oterhwise it is not displayed -> bug???
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_persons)))
    
    batch_description = Quantity(
        type=MEnum(suggestions_batch_descriptions),
        description='Choose the description for this batch from the dropdown list. If your desired description does not appear, please inform the Oasis administrator.',
        a_eln=dict(
            label="batch description",
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_batch_descriptions)))
    
    batch_number = Quantity(
        type = int,
        description = "Number of the batch couting upwards from 1 to 999 for each batch description separately.",
        a_eln = dict(component='NumberEditQuantity'),
    )
   
    batch_id = Quantity(
        type = str,
        description = "Automatically generated based on batch number and description e.g. SNC_001. You cannot edit the ID.",
        a_eln=dict(component='StringEditQuantity'),
        a_display={'editable':False}) # Does not work
    
    number_of_groups = Quantity(
        type=int,
        label="6. Please enter the number of groups",
        description='The number of different groups in the batch. All Samples in one group are identical.',
        a_eln=dict(component='NumberEditQuantity'))
        #a_eln=dict(component='SliderEditQuantity', minValue=1, maxValue=20, default=1))
    
    
    # spacer = Quantity(
    #     type=str,
    #     label=" ",
    #     description='Only an empty spacer fo the GUI',
    #     a_eln=dict(component='StringEditQuantity')
    # )

    # number_test = Quantity(
    #     type=int,
    #     description='The number of different groups in the batch. All Samples in one group are identical.',
    #     a_eln=dict(component='SliderEditQuantity', minValue=1, maxValue=20, default=1))
    

    # person_test = Quantity(
    #     type=User,
    #     a_eln= dict(
    #         component='AuthorEditQuantity'
    #     ))

    # architecture = Quantity(
    #     type=str,
    #     a_eln=dict(
    #         component='EnumEditQuantity',
    #         props=dict(suggestions=suggestions_architecture)))
 
    #substrate = Quantity(
    #    type=Reference(UMR_SubstrateForBatchPlan.m_def),
    #    a_eln=dict(component='ReferenceEditQuantity'))

    
    # groups_were_created = Quantity(
    #     type=bool,
    #     default=False,
    #     a_eln=dict(
    #         label = "Groups were created in the SubSection for selection of the processes",
    #         component='BoolEditQuantity'))


    ### BUTTONS (and workflow)

    move_processes_to_variation_subsection = Quantity(
        label="4. Move all Processes to the Parameter Variation Subsection",
        description="This moves all the processes from the'standard_processes' Subsection into the 'standard_processes_for_variation' Subsection. During this step a standalone Process entry is created and referenced in the variation section. They are saved in the folder 'Processes'.",
        type=bool,
        default=False,
        a_eln=dict(component='ActionEditQuantity')
    )
    
    create_groups_for_selection_of_processes = Quantity(
        type=bool,
        label="7. Create Groups For Selection of Processes",
        description="With this button you create groups. Enter the 'number_of_groups' first and then press the Button. The groups are created in the 'groups_for_selection_of_processes' Subsection. During this step also the standalone varied process entries are created. Navigate throught the groups and change the substrate parameters if neccesary. Then select the processes applied for this group.",
        default=False,
        a_eln=dict(component='ActionEditQuantity')
    )
    
    create_pdf_plan = Quantity(
        type=bool,
        label="9. Create PDF plan",
        description="COMING SOON: with this Button you can create a standardized PDF overview of your batch plan.",
        default=False,
        a_eln=dict(component='ActionEditQuantity'))
    
    batch_plan_pdf = Quantity(
        type=str,
        a_eln=dict(component='FileEditQuantity'),
        a_browser=dict(adaptor='RawFileAdaptor'))
    
    create_batch = Quantity(
        type=bool,
        label="11. Create Batch",
        description="With this button you crete your batch including all substrates and samples as well as the batch entry with its groups. They are saved in the corresponding folders. Check the FILES tab to find them.",
        default=False,
        a_eln=dict(component='ActionEditQuantity'))

    batch_was_created = Quantity(
        type=bool,
        label="Batch was created!",
        description='This checkbox is automaticaly checked if the batch was created',
        default=False,
        a_eln=dict(component='BoolEditQuantity'))

   
    ### SUBSECTIONS

    substrate = SubSection(
        section_def=UMR_SubstrateForBatchPlan, label="Add your substrate here")

    standard_processes = SubSection(
        section_def=UMR_ELNProcess, repeats=True, label="Add your processes here")

    standard_processes_for_variation = SubSection(
        section_def=UMR_VaryProcess, repeats=True, label="Vary parameters here. Choose process from the list.")

    groups_for_selection_of_processes = SubSection(
        section_def=UMR_GroupSettings, repeats=True, label="Manage groups here. Choose group from the list.")
    
    created_entities = SubSection(
        section_def = UMR_EntityReference, repeats=True, label="List with all finally created entities.")


    def normalize(self, archive, logger):
        self.method = "Batch Plan"
        #archive.metadata.entry_type = "UMR_BatchPlan"

        # Check current status of Batch Plan and automatically check checkboxes
        if not (self.batch_description and self.batch_number and self.responsible_person):
            log_warning(self, logger, f"Please enter the 'batch_description', the 'batch_number' and the 'responsible_person' in the Batch Plan")
        else:
            self.fill_general_info = True

            if not self.substrate:
                log_warning(self, logger, f"Please enter a Substrate in the Substrate Section")
            else:
                self.choose_substrate = True
                if not self.standard_processes and not self.create_processes:
                    log_warning(self, logger, f"Please enter Processes in the 'standard_processes' Subsection")
                else:
                    self.create_processes = True


        # Create batch_id
        if self.batch_description and self.batch_number:
           
            batch_abbreviation = batch_abbreviations.get(self.batch_description)  
            batch_id = f"{batch_abbreviation}_{str(self.batch_number).zfill(3)}"
            self.batch_id=batch_id

        # TODO KLAPPT NOCH NICHT: FEHLER BEI QUERY
            # Search for InternalBatch and batchPlan with the same ID -> log error if alreadyexisting entry is found
            query = {
                'or': {
                    'and': {
                        'entry_type:any': ['UMR_InternalBatch', 'UMR_ExternalBatch'],
                        'or': {
                            'data.lab_id#UMR_schemas.batch.UMR_InternalBatch': batch_id,
                            'data.lab_id#UMR_schemas.batch.UMR_ExternalBatch': batch_id
                        }
                    },
                    'and':{
                        'entry_type': 'UMR_BatchPlan',
                        'data.batch_id#UMR_schemas.create_internal_batch.UMR_BatchPlan': batch_id
                    }
                }
            }

            #search_result = UMR_search(archive, query)
            #log_info(self, logger, f"SEARCH RESULT: {search_result['data']}")

            #if len(search_result['data']) > 1: # 1 entry is always found
            #    log_error(self, logger, f"There already exists an Internal Batch or a batch plan with this batch number.Please check this again and choose a different number!")
            #else:
            #    self.batch_id=batch_id




        #####################################################################
        # BUTTON: LOAD STANDARD PROCESSES IN VARIATION SUBSECTION

        if self.move_processes_to_variation_subsection:
            self.move_processes_to_variation_subsection = False
            
            create_directory(self, archive, logger, "Processes")
            
            if self.fill_general_info and self.choose_substrate and self.standard_processes:
    
                # Iterate through all processes
                for process in self.standard_processes: 
                    
                    # Check if process name is given, so process is not fully empty
                    if not process.name:
                        log_error(self, logger, f"At least one process in the 'standard_process' Subsection does not have a name. Please Check.")
                        break
                    
                    # Maybe here one could use no ELN sections first and then automatically create the ELN Archive
                    # Create process archive
                    file_name = f"Processes/{process.position_in_experimental_plan}_{process.name.replace(' ','_').replace('/', '_')}.archive.json"
                    create_archive(process, archive, file_name)
                    entry_id = get_entry_id_from_file_name(file_name, archive)
                    process_ref = get_reference(archive.metadata.upload_id, entry_id)


                    # Create VaryProcess Entry with reference to created process archive
                    vary_process = UMR_VaryProcess(
                        position_in_experimental_plan=process.position_in_experimental_plan,
                        process_reference=process_ref,
                        name=process.name
                    )

                    # Append the VaryProcess entry to the standard_processes_for_variation SubSection
                    if not self.standard_processes_for_variation:
                        self.standard_processes_for_variation= []
                    self.standard_processes_for_variation.append(vary_process)
                    
                # Empty standard processes
                #self.standard_processes = [UMR_ELNProcess()] - > Because Error shows up
                self.standard_processes = []
                self.vary_process = True


        #####################################################################
        # BUTTON: CREATE GROUPS FOR SELECTION OF PROCESSES
        if self.create_groups_for_selection_of_processes:
            self.create_groups_for_selection_of_processes = False
            
            # Special Case: If number of groups is 0 -> Delete all groups
            if self.number_of_groups == 0:
                self.groups_for_selection_of_processes = []

            if self.create_groups:
                log_warning(self, logger, 'The Groups have already been created. If you entered a higher number groups are added. If you want to create all groups new, first delete all old groups.')
            if not self.substrate:
                log_error(self, logger, f"There is no substrate given. Pleae give the normally used substrate before creating the groups")
                return


            full_list_processes = []

            # Create Processes folder (for the case that this was not done before and you are only using reference and ignored the standard_processes Subsection)
            create_directory(self, archive, logger, "Processes")


            # Iterate through all processes
            for standard_process in self.standard_processes_for_variation: 
                
                if standard_process.process_is_varied:
                    # Handling of varied processes
                    # Create SelectProcess Entry with empty process_variation list
                    select_process = UMR_SelectProcess(varied_processes = [])
                    
                    # Iterate through variated processes
                    for batch_process in standard_process.varied_processes:
                        # Create process archive
                        file_name = f"Processes/{batch_process.position_in_experimental_plan}_{batch_process.name.replace(' ','_').replace('/', '_')}.archive.json"
                        create_archive(batch_process, archive, file_name)

                        # Create SelectProcessVariation Entry with reference
                        entry_id = get_entry_id_from_file_name(file_name, archive)
                        reference = get_reference(archive.metadata.upload_id, entry_id)
                        select_process_variation = UMR_SelectProcessVariation(
                            name = batch_process.name,
                            reference = reference,
                        )
                        # Append SelectProcessVariation Entry to SelectProcess Entry (in SubSection varied_processes)
                        select_process.varied_processes.append(select_process_variation)
                        select_process.normalize(archive, logger)

                else:
                    # Handling of unvaried processes
                    # Process Archive already created -> Just Create SelectProcess Entry with already selected process reference
                    select_process = UMR_SelectProcess(
                        selected_process = standard_process.process_reference)
                    select_process.normalize(archive, logger)

                # Append SelectProcess Entry to full list of processes    
                full_list_processes.append(select_process)


            # Create advanced SolarCell Settings Section
            #solar_cell_settings = UMR_StandardSampleSettings(
            #    number_of_solar_cells_on_substrate = self.standard_plan.number_of_solar_cells_on_substrate,
            #    solar_cell_names = self.standard_plan.solar_cell_names,
            #    area  = self.standard_plan.area,
            #    length = self.standard_plan.length,
            #    width = self.standard_plan.width,
            #    architecture = self.standard_plan.architecture,
            #    encapsulation = self.standard_plan.encapsulation,
            #    description = self.standard_plan.description,
            #)
            
            # Create Groups in SubSection groups with full list of processes for selection and the Substrate in SubSections respectively
            #self.groups_for_selection_of_processes = []
            for i in range(self.number_of_groups):
                # Check if group already exists -> skip 
                if self.create_groups and any(group.group_number == i+1 for group in self.groups_for_selection_of_processes):
                    continue 

                group = UMR_GroupSettings(
                    group_number = i+1,
                    substrate = self.substrate,
                    select_processes = full_list_processes,
                    #advanced_solar_cell_settings = solar_cell_settings,
                )
                group.normalize(archive, logger)
                self.groups_for_selection_of_processes.append(group)

            self.create_groups = True


        #####################################################################
        # BUTTON: create batch
        if self.create_batch:
            self.create_batch = False
         
            # Log possible errors
            if not self.approved:
                log_error(self, logger, "The Batch has to be approved before creating the Batch.")
                return
            if self.batch_was_created:
                log_error(self, logger, "The batch has already been created. This can not been undone without deleting the files and entities in the subsection created_entities! If you did that uncheck the solar_cells_were_created checkbox.")
                return
            if self.batch_description not in batch_abbreviations:
                log_error(self, logger, f"This batch description '{self.batch_description}' has no abbreviation yet.")
                return
            
            for group_settings in self.groups_for_selection_of_processes:
                if group_settings.number_of_substrates != len(group_settings.substrate_engraved_numbers):
                    log_error(self, logger, f"The number of the given substrate_engraved_numbers does not match the given number_of_substrates. Please check group: {group_settings.group_number}.")
                    return
                #elif group_settings.advanced_solar_cell_settings.number_of_solar_cells_on_substrate != len(group_settings.advanced_solar_cell_settings.solar_cell_names):
                #    log_error(self, logger, f"The number of the given solar_cell_names does not match the given number_of_solar_cells_on_substrate. Please check advanced solar_cell_settings in group: {group_settings.group_number}.")
                #    return
                elif supplier_abbreviations.get(group_settings.substrate.supplier) is None:
                    log_error(self, logger, f"The supplier '{group_settings.supplier}' has no abbreviation yet. Please inform the Oasis administrator. Please check in substrate in group: {group_settings.group_number}.")
                    return
   
            # Check if numbers of substrates and engraved substrate numbers are given
            for group_settings in self.groups_for_selection_of_processes:
                if not group_settings.number_of_substrates:
                    log_error(self, logger, f"No number of substrates given for group {group_settings.group_number}. Please check.")
                    return
                if not group_settings.substrate_engraved_numbers:
                    log_error(self, logger, f"No engraved substrate numbers given for group {group_settings.group_number}. Please check.")
                    return

                # Check if number of substrates does not match with given engraved_numbers
                if len(group_settings.substrate_engraved_numbers) != group_settings.number_of_substrates:
                    log_error(self, logger, f"Number of substrates does not match with given engraved_numbers. Please check group: {self.group_number}")
                    return
            

            # Check substrate numbers oberall in every group
            # Create empty list and fill it with all engraved numbers from all groups
            all_engraved_numbers =[]
            for group_settings in self.groups_for_selection_of_processes:
                if group_settings.substrate_engraved_numbers:
                # Create empty list and fill it with all engraved numbers from all groups
                    if group_settings.substrate_engraved_numbers:
                        all_engraved_numbers += group_settings.substrate_engraved_numbers 
                # Check if any engraved number is in the list more than one time and log error
                for engraved_number in group_settings.substrate_engraved_numbers:
                    if all_engraved_numbers.count(engraved_number) > 1:
                        log_error(self, logger, f"The engraved_number {engraved_number} was given for more than 1 substrate. Please Check.")
                        return


            # Check processes in every group
            for group_settings in self.groups_for_selection_of_processes:
                for i, process in enumerate(group_settings.select_processes):
                    if process.present:
                        if not process.selected_process:
                            log_error(self, logger, f"Error in Group: {group_settings.group_number}. No process chosen. Please choose a process or uncheck present.")
                            return


            # Clear the list with created entities
            self.created_entities = []

    	    # Create Batch folder and Substrate and Sample and SolarCell Folder
            create_directory(self, archive, logger, "Batch")
            create_directory(self, archive, logger, "Batch/Substrates")
            create_directory(self, archive, logger, "Batch/Samples")
            create_directory(self, archive, logger, "Batch/SolarCells")

            # CREATE BATCH
            batch_abbreviation = batch_abbreviations[self.batch_description]  
            batch_lab_id = f"{batch_abbreviation}_{str(self.batch_number).zfill(3)}"
            batch_name = f"batch_{batch_lab_id}"
            batch_file_name = f"Batch/{batch_name}.archive.json"
            batch = UMR_InternalBatch(
                name = f"Batch {batch_lab_id}",
                datetime = self.datetime,
                lab_id = batch_lab_id,
                batch_number = self.batch_number,
                batch_description = self.batch_description,
                responsible_person=self.responsible_person,
                description = self.description,
                samples = [],
                substrates = [],
            )
            try:
                create_archive(batch, archive, batch_file_name) #, overwrite=True)
            except Exception as e:
                # Catch Errors, because Batch folder does not exist
                log_error(self, logger, f"An error occured when creating an Internal Batch. --- Exception {e}")
                return
            
            # Create batch reference in created_entities
            batch_entry_id = get_entry_id_from_file_name(batch_file_name, archive)
            batch_reference = UMR_EntityReference(
                name = batch.name,
                reference=get_reference(archive.metadata.upload_id, batch_entry_id),
                lab_id = batch.lab_id)
            self.created_entities.append(batch_reference)


            # UPDATE PROCESSES
            for group_settings in self.groups_for_selection_of_processes:
                for i, process in enumerate(group_settings.select_processes):
                    if process.present:
                
                        # "Open" process                        
                        mainfile = process.selected_process.m_root().metadata.mainfile
                        with archive.m_context.raw_file(mainfile, 'r') as file:
                            data = json.load(file)
                        process_entry = self.from_dict(data['data'])
                        # Empty samples
                        process_entry.selected_samples = []
                        process_entry.samples = []
                        # Take time from Batch Plan for Process
                        process_entry.datetime =self.datetime
                        # Add position in experimental plan
                        process_entry.position_in_experimental_plan = i+1
                        # Reference Batch
                        process_entry.batch = get_reference(archive.metadata.upload_id, batch_entry_id)
                        log_warning(self, logger, f"INTERNAL BATCH - UPDATED PROCESS:{process_entry}")    
                        create_archive(process_entry, archive, mainfile, overwrite=True)


            # CREATE GROUPS
            for group_settings in self.groups_for_selection_of_processes:
                group = UMR_Group(
                    name = group_settings.display_name,
                    group_number = group_settings.group_number,
                    group_description = group_settings.group_description,
                    number_of_substrates = group_settings.number_of_substrates,
                    description = group_settings.description,
                    substrates = [],
                )

                # CREATE SUBSTRATES
                #supplier_abbreviation = supplier_abbreviations[group_settings.substrate.supplier]  
                for engraved_number in group_settings.substrate_engraved_numbers:
                    substrate_lab_id = f"{batch_abbreviation}_{str(self.batch_number).zfill(3)}_{str(engraved_number)}"
                    #substrate_lab_id = f"{supplier_abbreviation}_{str(engraved_number).zfill(5)}"
                    substrate_name=f"substrate_{substrate_lab_id}"
                    substrate_file_name = f"Batch/Substrates/{substrate_name}.archive.json"
                    # Create Substaret entry and copy inforamtion from referenced substrate
                    substrate = UMR_InternalSubstrate()
                    substrate.m_update_from_dict(group_settings.substrate.m_to_dict())
                    # Add other information
                    substrate.name = f"Substrate {substrate_lab_id}"
                    substrate.datetime = self.datetime
                    substrate.lab_id = substrate_lab_id
                    substrate.batch = get_reference(archive.metadata.upload_id, batch_entry_id) #Reference batch in substrate
                    substrate.group_number=group_settings.group_number
                    substrate.samples = []
                    # Create Substrate Archive
                    create_archive(substrate, archive, substrate_file_name)
                    
                    # Create substrate reference in created_entities
                    substrate_entry_id = get_entry_id_from_file_name(substrate_file_name, archive)
                    substrate_reference = UMR_EntityReference(
                        name = substrate.name,
                        reference=get_reference(archive.metadata.upload_id, substrate_entry_id),
                        lab_id=substrate.lab_id)
                    # Add substrate reference to batch, group and in created_entities
                    batch.substrates.append(substrate_reference)
                    group.substrates.append(substrate_reference)
                    self.created_entities.append(substrate_reference)

                    # # CREATE SOLAR CELLS
                    # for solar_cell_name in group_settings.advanced_solar_cell_settings.solar_cell_names:
                    #     if group_settings.advanced_solar_cell_settings.sample_type == "Solar Cell":
                    #         sample_lab_id = f"{batch_abbreviation}_{str(self.batch_number).zfill(3)}_{str(engraved_number).zfill(5)}_{solar_cell_name}"
                    #         sample_name=f"solar_cell_{sample_lab_id}"
                    #         sample_file_name = f'Batch/{sample_name}.archive.json'
                    #         sample = UMR_InternalSolarCell(
                    #             name = f"Solar Cell {sample_lab_id}",
                    #             datetime = self.datetime,
                    #             lab_id = sample_lab_id,
                    #             batch = get_reference(archive.metadata.upload_id, batch_entry_id), #Reference batch in solar_cell
                    #             substrate = get_reference(archive.metadata.upload_id, substrate_entry_id),  #Reference substrate in solar cell
                    #             group_number = group_settings.group_number,
                    #             architecture = group_settings.advanced_solar_cell_settings.architecture,
                    #             encapsulation = group_settings.advanced_solar_cell_settings.encapsulation,
                    #             area = group_settings.advanced_solar_cell_settings.area,
                    #             width = group_settings.advanced_solar_cell_settings.width,
                    #             length = group_settings.advanced_solar_cell_settings.length,
                    #             description = group_settings.advanced_solar_cell_settings.description,
                    #             processes_2 = [],
                    #         )
                    #         # Create Solar Cell Archive
                    #         log_warning(self, logger, f"SOLAR CELL 1")
                    #         create_archive(sample, archive, sample_file_name)
                    #         log_warning(self, logger, f"SOLAR CELL 2")
                    #         # Create Solar cell reference
                    #         sample_entry_id = get_entry_id_from_file_name(sample_file_name, archive)
                    #         sample_reference = UMR_EntityReference(
                    #             name='Solar Cell',
                    #             reference=get_reference(archive.metadata.upload_id, sample_entry_id),
                    #             lab_id=sample_lab_id)


                    #     # CREATE BASIC SAMPLES
                    #     elif group_settings.advanced_solar_cell_settings.sample_type == "Basic Sample":
                    #         sample_lab_id = f"{batch_abbreviation}_{str(self.batch_number).zfill(3)}_{str(engraved_number).zfill(5)}_{solar_cell_name}"
                    #         sample_name=f"sample_{sample_lab_id}"
                    #         sample_file_name = f'Batch/{sample_name}.archive.json'
                    #         sample = UMR_BasicSample(
                    #                 name = f"Sample {sample_lab_id}",
                    #                 datetime = self.datetime,
                    #                 lab_id = sample_lab_id,
                    #                 batch = get_reference(archive.metadata.upload_id, batch_entry_id), #Reference batch
                    #                 substrate = get_reference(archive.metadata.upload_id, substrate_entry_id),  #Reference substrate
                    #                 group_number = group_settings.group_number,
                    #                 area = group_settings.advanced_solar_cell_settings.area,
                    #                 width = group_settings.advanced_solar_cell_settings.width,
                    #                 length = group_settings.advanced_solar_cell_settings.length,
                    #                 description = group_settings.advanced_solar_cell_settings.description,
                    #                 processes = [],
                    #             )     
                    #         # Create Basic Sample Archive
                    #         log_warning(self, logger, f"BASIC SAMPLE 1")
                    #         create_archive(sample, archive, sample_file_name)
                    #         log_warning(self, logger, f"BASIC SAMPLE 2")
                    #         # Create Solar cell reference
                    #         sample_entry_id = get_entry_id_from_file_name(sample_file_name, archive)
                    #         sample_reference = UMR_EntityReference(
                    #             name='Sample',
                    #             reference=get_reference(archive.metadata.upload_id, sample_entry_id),
                    #             lab_id=sample_lab_id)

                 
                    # CREATE BASIC SAMPLES

                    sample_lab_id = f"{batch_abbreviation}_{str(self.batch_number).zfill(3)}_{str(engraved_number)}_X"
                    sample_name=f"sample_{sample_lab_id}"
                    sample_file_name = f'Batch/Samples/{sample_name}.archive.json'
                    sample = UMR_BasicSample(
                            name = f"Sample {sample_lab_id}",
                            datetime = self.datetime,
                            lab_id = sample_lab_id,
                            batch = get_reference(archive.metadata.upload_id, batch_entry_id), #Reference batch
                            substrate = get_reference(archive.metadata.upload_id, substrate_entry_id),  #Reference substrate
                            group_number = group_settings.group_number,
                            width = group_settings.substrate.width,
                            length = group_settings.substrate.length,
                            processes = [],
                        )     
                    # Create Basic Sample Archive
                    create_archive(sample, archive, sample_file_name)
                    # Create Solar cell reference
                    sample_entry_id = get_entry_id_from_file_name(sample_file_name, archive)
                    sample_reference = UMR_EntityReference(
                        name = sample.name,
                        reference=get_reference(archive.metadata.upload_id, sample_entry_id),
                        lab_id=sample.lab_id)

                    # Append sample reference
                    substrate.samples.append(sample_reference) 
                    batch.samples.append(sample_reference)
                    group.samples.append(sample_reference)
                    self.created_entities.append(sample_reference)

                    # ADD SAMPLE TO PROCESSES
                    for i, process in enumerate(group_settings.select_processes):
                        if process.present:     
                            # "Open" process                        
                            mainfile = process.selected_process.m_root().metadata.mainfile
                            with archive.m_context.raw_file(mainfile, 'r') as file:
                                data = json.load(file)
                            process_entry = self.from_dict(data['data'])
                            log_info(self, logger, f"PROCESS ENTRY {process_entry}")
                            # Add samples to processes
                            process_entry.selected_samples.append(sample_reference)
                            log_info(self, logger, f"PROCESS ENTRY 2 {process_entry}")
                            create_archive(process_entry, archive, mainfile, overwrite=True)

                            # This works but currently not needed
                            #sample.processes.append(process_entry)

                        # Currently not needed
                        #sample.normalize(archive, logger)
                        #create_archive(sample, archive, sample_file_name, overwrite=True)

                        # Update Substrate Archive (because of appended solar cell references)
                    substrate.normalize(archive, logger)
                    create_archive(substrate, archive, substrate_file_name, overwrite=True)
                # Append groups to batch
                batch.groups.append(group)
            # Update Batch Archive (because of appended solar cell and substrate references)
            create_archive(batch, archive, batch_file_name, overwrite=True)

            # Check box batch_was_created
            self.batch_was_created = True 
        

        # Sort groups
        self.groups_for_selection_of_processes = sorted(self.groups_for_selection_of_processes, key=lambda x: x.group_number)
        # Sort Processes
        self.standard_processes_for_variation = sorted(self.standard_processes_for_variation, key=lambda x: x.position_in_experimental_plan)

        # Normalize Created Entiteies im gleichen Prozess wie creaing those archives hat ncht geklappt.
        # Entweder Proxy not found oder fehlende oder defekte Referenz




        ### Automatically sort and check positions_in_experimental_plan in Subsections ###

        # Enter position in experimental plan automatically in STANDARD_PROCESSES
        for i, process in enumerate(self.standard_processes):
            if not process.position_in_experimental_plan:
                process.position_in_experimental_plan=(i+1)
        # Check for duplicates in position_in_experimental_plan
        processes_list = [process for process in self.standard_processes]
        positions = [process.position_in_experimental_plan for process in processes_list]
        if len(positions) != len(set(positions)):
            log_error(self, logger, f"Duplicate position_in_experimental_plan values found in 'standard_processes' Subsection (Batch Plan {self.batch_id}).")
            return
        # Sort standard_processes 
        processes_list.sort(key=lambda x: x.position_in_experimental_plan)
        self.standard_processes = processes_list

        # Enter position in experimental plan automatically in STANDARD_PROCESSES_FOR_VARIATION
        for i, process in enumerate(self.standard_processes_for_variation):
            if not process.position_in_experimental_plan:
                process.position_in_experimental_plan=(i+1)
        # Check for duplicates in position_in_experimental_plan
        processes_list = [process for process in self.standard_processes_for_variation]
        positions = [process.position_in_experimental_plan for process in processes_list]
        if len(positions) != len(set(positions)):
            log_error(self, logger, f"Duplicate position_in_experimental_plan values found in 'standard_processes_for_variation' Subsection (Batch Plan {self.batch_id}).")
            return
        # Sort standard_processes_for_variation)
        processes_list.sort(key=lambda x: x.position_in_experimental_plan)
        self.standard_processes_for_variation = processes_list

        # Clear created_entities list if no batch was created
        if not self.batch_was_created:
            self.created_entities = []




        super(UMR_BatchPlan, self).normalize(archive, logger)




    # Create process reference and append it to solar cell
                                #process_entry_id = get_entry_id_from_file_name(f"{process.display_name}.archive.json", archive)
                                
                            # ADD PROCESSES AND LAYERS
                            #for process in group_settings.select_processes:
                            #    if process.present:
                            #        if not process.selected_process:
                            #            log_error(self, logger, f"Error in Group: {group_settings.group_number}. No proces chosen. Please choose a process or uncheck present.")
                            #            return
                            #    process_reference = UMR_ProcessReference(
                            #        name=process.display_name,
                            #        reference = process.selected_process)
                                    #reference = get_reference(archive.metadata.upload_id, process_entry_id))
                            #    log_info(self, logger, f"REFERENCE:{process.selected_process}")
                            #    solar_cell.processes.append(process_reference)
                                # Append layer if layer is present
                                #if hasattr(process.selected_process.m_resolved(), 'layer') and process.selected_process.m_resolved().layer:
                                #    solar_cell.layers.append(process.selected_process.m_resolved().layer)

                        #log_info(self, logger, f"SOLAR CELL: {solar_cell}")



################################ Experimental Plan OLD ################################
'''
class HySprint_ExperimentalPlan(ExperimentalPlan, EntryData):
    m_def = Section(
        categories=[UMRCreateCategory],
        a_eln=dict(
            #hide=['users'],
            properties=dict(
                order=[
                    "name",
                    "standard_plan",
                    "load_standard_processes_for_variation",
                    "create_batch",
                    "number_of_substrates",
                    "substrates_per_subbatch",
                    "lab_id"]
            )),
        #a_template=dict(institute="UMR")
        )

    solar_cell_properties = SubSection(
        section_def=SolarCellProperties)

    def normalize(self, archive, logger):
        super(UMR_ExperimentalPlan, self).normalize(archive, logger)

        from baseclasses.helper.execute_solar_sample_plan import execute_solar_sample_plan
        execute_solar_sample_plan(self, archive, UMR_InternalSolarCell, UMR_Batch, logger)

        # actual normalization!!
        archive.results = Results()
        archive.results.properties = Properties()
        archive.results.material = Material()
        archive.results.eln = ELN()
        archive.results.eln.sections = ["UMR_ExperimentalPlan"]

'''










m_package.__init_metainfo__()
