from baseclasses.vapour_based_deposition import Evaporations

# Imports Nomad
from nomad.metainfo import Quantity, SubSection, Section, SchemaPackage, MEnum, Reference
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.datamodel.metainfo.basesections import SectionReference


from ..processes.process_baseclasses import UMR_BaseProcess, UMR_ELNProcess, UMR_PrecursorSolution, UMR_SolarCellSettings

# Imports UMR
from ..suggestions_lists import *
from ..helper_functions import *
from ..categories import *


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
                    'isntruments',
                    'steps',
                    'samples'
                ]))
        )
    

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
    
    m_package.__init_metainfo__()
