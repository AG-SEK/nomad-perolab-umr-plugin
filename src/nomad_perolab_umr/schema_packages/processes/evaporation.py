from baseclasses.helper.utilities import rewrite_json
from baseclasses.vapour_based_deposition import Evaporations
from nomad.datamodel.data import EntryData

# Imports Nomad
from nomad.metainfo import (
    Reference,
    SchemaPackage,
    Section,
    SubSection,
)

from ..categories import *
from ..helper_functions import *
from ..processes.process_baseclasses import (
    UMR_BaseProcess,
    UMR_ELNProcess,
)
from ..solar_cell import UMR_InternalSolarCell

# Imports UMR
from ..suggestions_lists import *
from ..umr_baseclasses import UMR_Layer
from ..umr_reference_classes import UMR_EntityReference

m_package = SchemaPackage() 



class UMR_Evaporation(UMR_BaseProcess, Evaporations, EntryData):
    m_def = Section(
        label_quantity = 'method',
        a_eln=dict(
            hide=['present', 'lab_id', 'positon_in_experimental_plan'],
            properties=dict(
                order=[
                    'name', 'datetime', 'end_time', 'location',
                    'description',
                    'position_in_experimental_plan',
                    'layer',
                    'organic_evaporation',
                    'inorganic_evaporation',
                    'perovskite_evaporation',
                    'instruments',
                    'steps',
                    'samples'
                ]))
        )

    layer = SubSection(section_def=UMR_Layer, repeats=True)
    

class UMR_EvaporationELN(UMR_ELNProcess, UMR_Evaporation):
    m_def = Section(
        label="Evaporation ELN",
        categories=[UMRSynthesisCategory],
        # label_quantity = 'method',
        # a_eln=dict(
        #     hide=['present', 'lab_id', 'positon_in_experimental_plan',
        #           'create_solar_cells', 'solar_cell_settings'],
        #     properties=dict(
        #         order=[
        #             'standard_process', 'load_standard_process',
        #             'name', 'datetime', 'end_time', 'location', 
        #             'recipe',
        #             'description',
        #             'batch', 'position_in_experimental_plan',
        #             'use_current_datetime', 'execute_process_and_deposit_layer',
        #             'solution',
        #             'recipe_steps',
        #             'layer',
        #             'annealing',
        #             'quenching',
        #             'sintering',
        #             'samples']))
        )
    
    standard_process = UMR_ELNProcess.standard_process.m_copy()
    standard_process.type = Reference(UMR_Evaporation.m_def)

    def normalize(self, archive, logger):
            
        # BUTTON: Execute Process
        if self.execute_process_and_deposit_layer:
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
                process_entry = UMR_Evaporation()
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
         
        super(UMR_EvaporationELN, self).normalize(archive, logger) 


    m_package.__init_metainfo__()
