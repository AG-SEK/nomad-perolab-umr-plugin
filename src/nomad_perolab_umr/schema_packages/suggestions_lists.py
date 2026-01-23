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


### Lists with suggestions for the EnumEditFields (Enumerations)

# substrate material
suggestions_substrate_material = [
    'glass',
    'aluminoborosilicate glass',
    'sodalime glass',
    'low-iron sodalime glass',
    'Ti-foil',
    'silicon wafer',
]

# Conducting materials (on substrate)
suggestions_conducting_material = [
    'None', # No conducting layer present
    'TCO',  # Unknown conductive layer (Transparent Conductive Oxide)
    'SLG',
    'FTO',
    'ITO',
    'TCO',
    'PET',
    'PEN',
    'AZO',
    'IZO',
    'Graphene',
    'Ti',
    'Ag',
    'Ag-nw', 
    'Ag-grid',
    'Au',
    'PDMS',
]

# structuring
suggestions_structuring = [
    'laser patterned',
    'laser patterned, with cTiO2 stripes',
    'laser patterned, with cTiO2 on specific zones',
]

# architecture
suggestions_architecture = [
    'Unknown',
    'pin',
    'nip',
    'Pn-Heterojunction',
    'Front contacted',
    'Back contacted',
    'Schottky',
] 
    
# Encapsulations
suggestions_encapsulation = [
    'None',
    'lamination',
    'lamination + edge seal',
    'glass frit',
    'UV glue',
]    


# Dictionary with supplier abbreviations
supplier_abbreviations = {
    'Fraunhofer-Institut für Solare Energiesysteme ISE': 'ISE' ,
    'University of Oxford': 'UOX',
    'University of Freiburg': 'UFr',
    'École Polytechnique Fédérale de Lausanne': 'EPL',
    'Solaronix SA': 'SNX',
    'Rijksuniversiteit Groningen': 'UGR',
    'Uppsala Universitet': 'UUP',
    'Università degli Studi di Roma Tor Vergata': 'UTV',
    'Universidade do Porto': 'UPO',
    "Commissariat à l'Énergie Atomique et aux Énergies Alternatives": 'CEA',
}

# Supplier
suggestions_supplier = [supplier for supplier in supplier_abbreviations.keys()]


# Deposition process
suggestions_deposition_process = [
    'Spin Coating',
    'Blade Coating',
    'TODO',
]

# Suppliers of Chemicals
# Please no spaces in the abbreviations!!!
supplier_chemicals_abbreviations = {
    'Greatcell Solar Materials Pty Ltd': 'GreatcellSolar',
    'Sigma-Aldrich Chemie GmbH': 'SigmaAldrich',
    'Carl Roth GmbH & CO KG': 'CarlRoth',
    'TCI Deutschland GmbH': 'TCI',
    'Fisher Scientific GmbH': 'Fisher',
    'Dyenamo AB': 'Dyenamo',
    'Solaronix SA': 'Solaronix',
    'Luminescence Technology Corp.': 'Lumtec',
    'Strem Chemicals Inc.': 'Strem',
    'Ossila B.V.': 'Ossila',
    "Solaveni GmbH": "Solaveni",
    "Avantama AG": "Avantama",
    "Liaoning Yike Precision New Energy Technology Co. Ltd.": "LNYK",
    "LinXole AB": "LinXole",
    "Xiamen Funano Material Technology Co., Ltd": "Funano",
    "Dockweiler Chemicals GmbH": "Dock",
    "Yingkou Shangsheng Business Co.,Ltd.": "Yingkou",
}

# Suppliers of Chemicals
suggestions_supplier_chemicals = [supplier for supplier in supplier_chemicals_abbreviations.keys()]


# Suppliers of Instruments
# Please no spaces in the abbreviations!!!
supplier_instruments_abbreviations = {
    'Ossila B.V.': 'Ossila',
    'CICCI Research s.r.l.': 'Cicci',
    'GS GLOVEBOX Systemtechnik GmbH': 'GS',
    'G2V Optics Inc.': 'G2V',
    'Automatic Research GmbH': 'AutomaticResearch',
    'Sartorius AG': 'Sartorius',
    'Thermo Fisher Scientific Inc.': 'ThermoFisher',
    'Laurell Technologies Corporation': 'Laurell',
    'IKA-Werke GmbH & CO. KG': 'IKA',
    'VWR International GmbH': 'VWR',
    'PerkinElmer LAS GmbH': 'PerkinElmer',
    'LINSEIS Messgeräte GmbH': 'Linseis',
    "QYB Quantum Yield Berlin GmbH": "QYB",
    "Harry Gestigkeit GmbH": "Gestigkeit",
}

# Suppliers of Instruments
suggestions_supplier_instruments = [supplier for supplier in supplier_instruments_abbreviations.keys()]


# Persons/ User
suggestions_persons = [
    "Aaron Schüller-Ruhl",
    "Lukas Wagner",
    "Jan Christoph Goldschmidt",
    "Lea Obermüller",
    "Dominik Muth",
    "Sandra Schmidt",
    "Christopher Janas",
    "Ali Reza Nazari Pour",
    "Annika Schneider",
    "Malwine Lühder",
    "Gülüsüm Babayeva",	
    "Max Gorenflo",
    "Immo Petersen",			
]

# Dictionary with batch abbreviations
batch_abbreviations = {
    "Single Junction NIP Carbon": "SNC",
    "Single Junction PIN Top Cell": "SPT",
    "Test Batch": "Test",
}

# Batch descriptions/ topics
suggestions_batch_descriptions = [name for name in batch_abbreviations.keys()]

# Projects
suggestions_projects = [
    "Diamond",
    "PeroGAIN",
    "KPFM",
]

# List with paths to variation parameters
list_path_variation_parameters = [
    # Original from HZB
    # Quenching
    "quenching/anti_solvent_2/name",
    "quenching/anti_solvent_dropping_time",
    "quenching/anti_solvent_volume",
    "quenching/anti_solvent_dropping_flow_rate",
    "quenching/anti_solvent_dropping_height",
    # Annealing
    "annealing/time",
    "annealing/temperature",
    "annealing/pressure",
    # Spin Coating
    "recipe_steps/0/time",
    "recipe_steps/0/speed",
    "recipe_steps/0/acceleration",
    "recipe_steps/1/time",
    "recipe_steps/1/speed",
    "recipe_steps/1/acceleration",
    # Sintering
    "sintering/time",
    "sintering/temperature",
    "sintering/ramp",
    # Solution
    "solution/0/solution_volume",
    # ????????????
    "solution/0/solution_details/datetime",
    "solution/0/solution_details/solute/0/concentration_mol",
    "solution/0/solution_details/solute/0/concentration_mass",
    "solution/0/solution_details/solute/0/amount_relative",
    "solution/0/solution_details/additive/0/concentration_mol",
    "solution/0/solution_details/additive/0/concentration_mass",
    "solution/0/solution_details/additive/0/amount_relative",
    "solution/0/solution_details/solvent/0/concentration_mol",
    "solution/0/solution_details/solvent/0/concentration_mass",
    "solution/0/solution_details/solvent/0/amount_relative",
    "solution/0/solution_details/other_solution/0/solution_volume",
    "solution/0/solution_details/other_solution/0/amount_relative",
    # Slot Die Coatin ???
    "properties/flow_rate",
    "properties/slot_die_head_width",
    "properties/slot_die_shim_width",
    "properties/slot_die_shim_thickness",
    "properties/slot_die_head_distance_to_thinfilm",
    "properties/slot_die_head_speed",
    "properties/temperature",
    "properties/time",
    # Evaporation ???
    "organic_evaporation/0/chemical_2/name",
    "organic_evaporation/0/thickness",
    "organic_evaporation/0/pressure",
    "organic_evaporation/0/start_rate",
    "organic_evaporation/0/target_rate",
    "organic_evaporation/0/time",
    "inorganic_evaporation/0/chemical_2/name",
    "inorganic_evaporation/0/thickness",
    "inorganic_evaporation/0/pressure",
    "inorganic_evaporation/0/start_rate",
    "inorganic_evaporation/0/target_rate",
    "inorganic_evaporation/0/time",
    # Datetime
    "datetime",
    
    # Cleaning
    "cleaning/0/time",
    "cleaning/0/solvent_2/name",
    "cleaning/0/temperature",
    "cleaning/0/time",
    # UV Cleaning
    "cleaning_uv/0/time",
    "cleaning_uv/0/pressure",
    # Cleaning Plasma
    "cleaning_plasma/0/time",
    "cleaning_plasma/0/pressure",
    "cleaning_plasma/0/power",
    "cleaning_plasma/0/plasma_type",
    # Layer
    'layer/0/...',
    # BladeCoating
    'properties/blade_height',
    'properties/blade_speed',
    'properties/temperature',



]

# suggestions for location of processes
sugggestions_locations = [
    'Fume hood',
    'Glovebox', # früher "GS Glovebox"
]


suggestions_buildings = [
    "H|04 Hans-Meerwein-Straße 6 (Mehrzweckgebäude)",
    "R|05 Renthof 7",
    "H|01 Hans-Meerwein-Straße 4 (Chemie)",
]

suggestions_room_categories = [
    "Characterization Laboratory",
    "Synthesis Laboratory",
    "Office",
]

suggestions_instrument_categories = [
    "Characterization",
    "Synthesis",
    "Miscellaneous",
]



# dictionary which links to every Measurement Type a list of the standard instruments (lab_ids)
standard_instruments_dictionary = dict(
    UMR_JVMeasurement = ['JV_Setup_Cicci', 'Sun_Simulator_G2V'],
    UMR_MPPTrackingJVMeasurement = ['JV_Setup_Cicci', 'Sun_Simulator_G2V'],
    UMR_StabilityJVMeasurement = ['JV_Setup_Cicci', 'Sun_Simulator_G2V'],
    UMR_EQEMeasurement = ['EQE_Setup_Cicci'],
    UMR_StabilityTest = ['Ageing_Setup_Cicci'],
    UMR_ConnectionTest = ['JV_Setup_Cicci', 'Sun_Simulator_G2V'],
    UMR_StabilizedShortCircuitCurrent = ['JV_Setup_Cicci', 'Sun_Simulator_G2V'],
    UMR_StabilizedOpenCircuitVoltage = ['JV_Setup_Cicci', 'Sun_Simulator_G2V'],
    UMR_MPPTracking = ['JV_Setup_Cicci', 'Sun_Simulator_G2V'],
)

suggestions_chemical_category = [
    "Perovskite Precursor",
    "Solvent",
    "Electron Transport Material",
    "Hole Transport Material",
    "Additive",
    "Electrode Material",
    "Encapsulation Material",
    "Buffer and Passivation Material",
    "Miscellaneous",
]

