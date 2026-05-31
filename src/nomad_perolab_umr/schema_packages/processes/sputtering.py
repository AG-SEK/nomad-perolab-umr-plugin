import numpy as np
# Imports HZB
from baseclasses.vapour_based_deposition import Sputtering, SputteringProcess # Sputtering Baseclass
from baseclasses.helper.utilities import rewrite_json
from baseclasses.material_processes_misc import Annealing

# Imports Nomad
from nomad.datamodel.data import EntryData # Baseclass for entering data in Nomad GUI
from nomad.metainfo import ( # Nomad Baseclasses
    Quantity,
    Reference,
    SchemaPackage,
    Section,
    SubSection,
    MEnum,
)

# Imports UMR
from ..categories import *  # Import of the categories for the processes
from ..helper_functions import * # Import of helper functions for the processes
from ..processes.process_baseclasses import ( # Our UMR Baseclasses for the processes
    UMR_BaseProcess,
    UMR_ELNProcess, # Baseclass for Electronic Lab Notebook processes
)

from ..solar_cell import UMR_InternalSolarCell # Baseclass for the internal solar cell reference, which is used in some processes

from ..suggestions_lists import * # Import of suggestions lists for the processes, e.g. for dropdown menus in the ELN
from ..umr_baseclasses import UMR_Layer # Baseclass for the layer subsection of the processes
from ..umr_reference_classes import UMR_EntityReference # Baseclass for UMR entity references
from ..umr_synthesis_classes import UMR_ChemicalLot


m_package = SchemaPackage() 


# UMR Sputtering Process Baseclass, which inherits from HZB Sputtering Process Baseclass
class UMR_SputteringProcess(SputteringProcess):
    m_def = Section(
        a_eln=dict(
            hide=[
                    'target',
                    'target_2',  
                    'gas',
                    'gas_2',
                    'gas_flow_rate',
                    'pressure',
                ],
            properties=dict(
                order=[
                    # sources
                    'target_lot',
                    'source',
                    'control_mode',
                    'pulse_frequency',
                    'reverse_time',
                    'tooling_factor', 
                    # startup          
                    'base_pressure',
                    'rotation_rate',
                    # process
                    'argon_flow_rate',
                    'oxygen_flow_rate',
                    'water_flow_rate',
                    'capman_pressure',
                    'pressure_bump',
                    'ramp_power',
                    'ramp_rate',
                    'soak_time',
                    'burn_in_time',
                    'temperature',
                    'deposition_time',
                    'power',
                    'voltage',
                    'thickness',
                    'description',
                ]
            )
        )
    )

    target_lot = Quantity(
        links=['https://purl.archive.org/tfsco/TFSCO_00002035'],
        type=Reference(UMR_ChemicalLot.m_def),
        a_eln=dict(
            component='ReferenceEditQuantity',
            ),        
    )

    tooling_factor = Quantity(
        type=np.dtype(np.float64),
        description='Tooling factor for thickness calibration',
        a_eln=dict(
            component='NumberEditQuantity',
            props=dict(minValue=0),
        ),
    )

    base_pressure = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001025',
            'https://purl.archive.org/tfsco/TFSCO_00005040',
        ],
        type=np.dtype(np.float64),
        unit=('mbar'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='mbar',
            props=dict(minValue=0),
        ),
    )

    suggestions_list=['power', 'voltage', 'current']
    control_mode = Quantity(
        type=MEnum(suggestions_list),
        description='Control mode used for the sputtering process.',
        a_eln=dict(
            component='EnumEditQuantity',
            props=dict(suggestions=suggestions_list)
        ),
    )

    pulse_frequency = Quantity(
        type=np.dtype(np.float64),
        unit=('kHz'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='kHz',
            props=dict(minValue=0, maxValue=100),
        ),
    )

    reverse_time = Quantity(
        type=np.dtype(np.float64),
        unit=('us'),
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='us',
            props=dict(minValue=0),
        ),
    )

    argon_flow_rate = Quantity(
        type=np.dtype(np.float64),
        #unit="cm**3/minute" #'sccm',
        description='Argon gas flow rate during sputtering.',
        a_eln=dict(
            component='NumberEditQuantity',
            #defaultDisplayUnit="cm**3/minute",
            props=dict(minValue=0),
        ),
    )

    oxygen_flow_rate = Quantity(
        type=np.dtype(np.float64),
        #unit="cm**3/minute" #'sccm',
        description='Oxygen gas flow rate during sputtering.',
        a_eln=dict(
            component='NumberEditQuantity',
            #defaultDisplayUnit="cm**3/minute",
            props=dict(minValue=0),
        ),
    )

    water_flow_rate = Quantity(
        type=np.dtype(np.float64),
        #unit="cm**3/minute" #'sccm',
        description='Water vapour flow rate during sputtering.',
        a_eln=dict(
            component='NumberEditQuantity',
            #defaultDisplayUnit="cm**3/minute",
            props=dict(minValue=0),
        ),
    )

    capman_pressure = Quantity(
        links=[
            'http://purl.obolibrary.org/obo/PATO_0001025',
            'https://purl.archive.org/tfsco/TFSCO_00005040',
        ],
        type=np.dtype(np.float64),
        unit='mbar',
        description='Process pressure measured by the capacitance manometer.',
        a_eln=dict(
            component='NumberEditQuantity',
            label='process pressure',
            defaultDisplayUnit='mbar',
            props=dict(minValue=0),
        ),
    )

    pressure_bump = Quantity(
        type=bool,
        description='Indicates whether a pressure bump was used during the sputtering recipe.',
        default=True,
        a_eln=dict(
            component='BoolEditQuantity',
        ),
    )
    
    ramp_power = Quantity(
        type=np.dtype(np.float64),
        unit='%',
        description='ramp of power in percent of the controller maximum',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='%',
            props=dict(minValue=0),
        ),
    )
    
    ramp_rate = Quantity(
        type=np.dtype(np.float64),
        unit='%/min',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='%/min',
            props=dict(minValue=0),
        ),
    )

    soak_time = Quantity(
        type=np.dtype(np.float64),
        unit='s',
        description='initial soak time after power ramped up',
        a_eln=dict(
            component='NumberEditQuantity',
            defaultDisplayUnit='s',
            props=dict(minValue=0),
        ),
    )

# UMR Sputtering Baseclass, which inherits from the HZB Sputtering Baseclass and the Nomad EntryData Baseclass. It defines
class UMR_Sputtering(UMR_BaseProcess, Sputtering, EntryData):
    m_def = Section(
        label_quantity = 'method', # Defines which quantity is displayed as a alabel in the list (if used as subsection)
        a_eln=dict(
            hide=[
                'present',
                'lab_id',
                'positon_in_experimental_plan',
                'location',
                'position_in_experimental_plan',
                "atmosphere",
            ],
            properties=dict(
                order=[ # Defines order of the  and Subsections in the ELN
                    # Quantities
                    'name', 
                    'datetime', 
                    'end_time',
                    'description',
                    'operator',
                    "batch",
                    # Subsections
                    'layer',
                    "processes",
                    'annealing',
                    'instruments',
                    'samples',
                    'steps',
                ]))
        )

    layer = SubSection(section_def=UMR_Layer, repeats=True) # why needed?

    processes = SubSection(section_def=UMR_SputteringProcess, repeats=False)

    annealing = SubSection(links=['http://purl.obolibrary.org/obo/BFO_0000051'], section_def=Annealing)



# UMR ELN Sputtering class, which inherits from the UMR Sputtering Baseclass and the UMR ELN Process Baseclass. It defines the category for the ELN and can be used to add ELN specific quantities or subsections in the future.
class UMR_SputteringELN(UMR_ELNProcess, UMR_Sputtering):
    m_def = Section(
        label="Sputtering ELN",
        categories=[UMRSynthesisCategory], # Defines the category for the ELN
    )

    # Redefintion of the standard process
    standard_process = UMR_ELNProcess.standard_process.m_copy()
    standard_process.type = Reference(UMR_Sputtering.m_def)


    
    def normalize(self, archive, logger):
            
        # BUTTON: Execute Process
        if self.execute_process_and_deposit_layer:
            # Reset Button
            self.execute_process_and_deposit_layer = False
            rewrite_json(['data', 'execute_process_and_deposit_layer'], archive, False)

            # Log error if no solar cell settings are given
            if self.create_solar_cells and not self.solar_cell_settings:
                log_error(self, logger, "If solar cells should be created please give the details in the subsection solar_cell_settings. Please also check if a sample was transferred to the sample subsection already and if so delete it there again.")
                return

            # Log error if no sample is chosen 
            if not self.selected_samples:
                log_error(self, logger, 'No Samples Selected. Please add the samples on which this process should be applied to the selected_samples section')
                return
            
            # Create Process and add it to sample entry 
            for sample_ref in self.selected_samples:
                process_entry = UMR_Sputtering()
                sample_entry = add_process_and_layer_to_sample(self, archive, logger, sample_ref, process_entry)
                # return new sample entry with new process (because this is not yet saved in the referenced sample (sample_ref))
                    
                # Create Solar Cells
                if self.create_solar_cells:    
                    for solar_cell_name in self.solar_cell_settings.solar_cell_names:
                        solar_cell_entry = UMR_InternalSolarCell()
                        solar_cell_entry_id, solar_cell_entry = create_solar_cell_from_basic_sample(self, archive, logger, sample_entry, solar_cell_name, solar_cell_entry)
                        # Create references in batch and substrate
                        solar_cell_reference = UMR_EntityReference(
                            name = solar_cell_entry.name,
                            reference=get_reference(archive.metadata.upload_id, solar_cell_entry_id),
                            lab_id = solar_cell_entry.lab_id)
                        create_solar_cell_references(self, archive, logger, sample_ref, solar_cell_reference)

            # Empty selected_samples Section
            self.selected_samples = []
         
        super().normalize(archive, logger) 


    m_package.__init_metainfo__()