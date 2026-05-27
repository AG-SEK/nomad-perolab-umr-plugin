
# Imports HZB
from baseclasses.vapour_based_deposition import Sputtering # Sputtering Baseclass
from baseclasses.helper.utilities import rewrite_json

# Imports Nomad
from nomad.datamodel.data import EntryData # Baseclass for entering data in Nomad GUI
from nomad.metainfo import ( # Nomad Baseclasses
    Reference,
    SchemaPackage,
    Section,
    SubSection,
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


m_package = SchemaPackage() 


# UMR Sputtering Baseclass, which inherits from the HZB Sputtering Baseclass and the Nomad EntryData Baseclass. It defines
class UMR_Sputtering(UMR_BaseProcess, Sputtering, EntryData):
    m_def = Section(
        label_quantity = 'method', # Defines which quntity is displayed as a alabel in the list (if used as subsection)
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan'], # Defines which quantities are hidden in the ELN    
            properties=dict(
                order=[             # Defines order of the  and SUbsections in the ELN
                    # Quantities
                    'name', 'datetime', 'end_time', 'location',
                    'description',
                    'position_in_experimental_plan', "batch",
                    "description",
                    # Subsections
                    'layer',
                    "processes",
                    'instruments',
                    'steps',
                    'samples',
                    "atmosphere",
                ]))
        )

    layer = SubSection(section_def=UMR_Layer, repeats=True)

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