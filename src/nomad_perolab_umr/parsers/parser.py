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



### Imports ###
# Python libraries
import os

# HZB methods
from baseclasses.helper.utilities import (
    create_archive,
    get_encoding,
)

# Nomad Classes
from nomad.datamodel import EntryArchive
from nomad.parsing.parser import MatchingParser

from ..schema_packages.characterization.connection_test import (
    UMR_ConnectionTest,
    UMR_ConnectionTestExtraData,
    UMR_StabilizedOpenCircuitVoltage,
    UMR_StabilizedShortCircuitCurrent,
)
from ..schema_packages.characterization.eqe_measurement import UMR_EQEMeasurement
from ..schema_packages.characterization.jv_measurement import UMR_JVMeasurement
from ..schema_packages.characterization.mpp_tracking import (
    UMR_MPPTracking,
    UMR_MPPTrackingJVMeasurement,
    UMR_MPPTrackingParameters,
)
from ..schema_packages.characterization.stability_test import (
    UMR_StabilityJVMeasurement,
    UMR_StabilityParameters,
    UMR_StabilityTest,
)

# My classes and methods
from ..schema_packages.helper_functions import *
from ..schema_packages.read_and_parse.general_parser import (
    add_data_file,
    add_standard_instrument,
)
from ..schema_packages.read_and_parse.read_header_line import read_header_line

#from UMR_schemas import UMR_TimeResolvedPhotoluminescence, UMR_PLmeasurement, UMR_Measurement, UMR_UVvismeasurement, UMR_trSPVmeasurement



class CicciTXTParser(MatchingParser):

    ########################## ACTUAL PARSING FUNCTION ##########################

    def parse(self, mainfile: str, archive: 'EntryArchive', logger):

        """
        The parse function to parse .txt files and create the corresponding measurement entries.
        - creates the correct measurement entry (JV, ...)
        - adds the measurement file in the data_file field to the entry
            -> This is used in the normalizer of the entry to extract the measurement data from the measurement file
        - references the sample (based on sample_id)
        - parses header information (notes, datetime)
        - creates Archive
        """

        # get encoding
        with open(mainfile, 'rb') as file:
            # archive.m_context.raw_file(mainfile, "br") as file:
            encoding = get_encoding(file)

        # Create empty header dictionary for header informations (Key):
            # - measurement type (Test)
            # - sample_id (Device)
            # - notes (Note)
            # - datetime (Date and Time)
        header_dict = {}

        # Open File and read it line by line
        with open(mainfile, encoding=encoding) as file:
            for line in file:
                # Remove whitespaces from the line
                line = line.strip()
                # Check if header ended -> stop loop
                if line == '## Data ##':
                    break
                # Skip empty lines and title lines ([General info],[Scan Seetings], ...) and ## Data ##
                if not line or line.startswith("[") or line.startswith("##"):
                    continue
                # Fill header_dict with keys and values
                header_dict = read_header_line(line, header_dict)

        # Transfer values from dictionary to variables using the corresponding keys
        measurement = header_dict['Test']
        sample_id = header_dict['Device']

        # log Error (if sample_id or measurement type could not be extracted)
        if not sample_id or not measurement:
            log_error(self, logger, "Error when extracting sample ID and measurement type from txt-file.")

        # log processing information
        log_info(self, logger, f'INFORMATION ABOUT PROCESSING .TXT FILE ::: MAINFILE: {mainfile} | FILE: ENCODING: {encoding} | MEASUREMENT: {measurement} | SAMPLE_ID: {sample_id}')

        ## Extract directory for helper quantity
        #directory = os.path.dirname(mainfile).split("raw/", 1)[-1]
        #directory = directory.replace('/', '_') # Replace "/"" with "_", because otherwise API search fails


        # Create new Measurement entry depending on measurement type
        if measurement == "JV":
            entry = UMR_JVMeasurement()
            add_data_file(entry, mainfile)
            add_standard_instrument(entry, archive, logger)
            # Create Nomad Archive out of entry
            create_archive(entry, archive, f'{entry.data_file}.archive.json')  # entry, archive, filename
            # The entry data is converted into json format and then written into the archive file (archive = processed data)
            # create_archive also calls the normalizer of the section


        elif measurement == "IPCE":
            entry = UMR_EQEMeasurement()
            add_data_file(entry, mainfile)
            add_standard_instrument(entry, archive, logger)
            create_archive(entry, archive, f'{entry.data_file}.archive.json')


        elif measurement == "MPPT (Tracking)":
            entry = UMR_MPPTracking()
            #entry.directory = directory
            add_data_file(entry, mainfile)
            add_standard_instrument(entry, archive, logger)
            create_archive(entry, archive, f'{entry.data_file}.archive.json')

        elif measurement == "MPPT (JV)":
            entry = UMR_MPPTrackingJVMeasurement()
            #entry.directory = directory
            add_data_file(entry, mainfile)
            add_standard_instrument(entry, archive, logger)
            create_archive(entry, archive, f'{entry.data_file}.archive.json')

        elif measurement == "MPPT (Parameters)":
            # Entry for Reverse Data
            entry_reverse = UMR_MPPTrackingParameters()
            #entry_reverse.directory = directory
            entry_reverse.scan = "Reverse"
            add_data_file(entry_reverse, mainfile)
            create_archive(entry_reverse, archive, f'{entry_reverse.data_file}_reverse.archive.json')

            # Entry for Forward Data
            entry_forward = UMR_MPPTrackingParameters()
            #entry_forward.directory = directory
            entry_forward.scan = "Forward"
            add_data_file(entry_forward, mainfile)
            create_archive(entry_forward, archive, f'{entry_forward.data_file}_forward.archive.json')


        elif measurement == "Stability (Tracking)":
            entry = UMR_StabilityTest()
            #entry.directory = directory
            add_data_file(entry, mainfile)
            add_standard_instrument(entry, archive, logger)
            create_archive(entry, archive, f'{entry.data_file}.archive.json')

        elif measurement == "Stability (JV)":
            entry = UMR_StabilityJVMeasurement()
            #entry.directory = directory
            add_data_file(entry, mainfile)
            add_standard_instrument(entry, archive, logger)
            create_archive(entry, archive, f'{entry.data_file}.archive.json')

        elif measurement == "Stability (Parameters)":
            # Entry for Reverse Data
            entry_reverse = UMR_StabilityParameters()
            #entry_reverse.directory = directory
            entry_reverse.scan = "Reverse"
            add_data_file(entry_reverse, mainfile)
            create_archive(entry_reverse, archive, f'{entry_reverse.data_file}_reverse.archive.json')

            # Entry for Forward Data
            entry_forward = UMR_StabilityParameters()
            #entry_forward.directory = directory
            entry_forward.scan = "Forward"
            add_data_file(entry_forward, mainfile)
            create_archive(entry_forward, archive, f'{entry_forward.data_file}_forward.archive.json')


        elif measurement == "Connection Test":
            # Check if "Extra" is in filename -> then the file is not parsed (only temperature over time data)
            filename = os.path.splitext(os.path.basename(mainfile))[0] # only filename without folders
            if "_Extra" in filename:
                entry = UMR_ConnectionTestExtraData()
                add_data_file(entry, mainfile)
                create_archive(entry, archive, f'{entry.data_file}.archive.json')
                return
            elif 'Mode' not in header_dict:
                entry = UMR_ConnectionTest()
                add_data_file(entry, mainfile)
                add_standard_instrument(entry, archive, logger)
                #self.addHeaderData_referenceSample(logger, archive, entry, mainfile, header_dict)
                create_archive(entry, archive, f'{entry.data_file}.archive.json')
                log_info(self, logger, "Kein Mode")
                return
            elif header_dict['Mode'] == "Short-Circuit Current": # TODO Change name
                entry = UMR_StabilizedShortCircuitCurrent()
                add_data_file(entry, mainfile)
                add_standard_instrument(entry, archive, logger)
                #self.addHeaderData_referenceSample(logger, archive, entry, mainfile, header_dict)
                create_archive(entry, archive, f'{entry.data_file}.archive.json')
                return
            elif header_dict['Mode'] == "Open-Circuit Voltage": # TODO Change name
                entry = UMR_StabilizedOpenCircuitVoltage()
                add_data_file(entry, mainfile)
                add_standard_instrument(entry, archive, logger)
                #self.addHeaderData_referenceSample(logger, archive, entry, mainfile, header_dict)
                create_archive(entry, archive, f'{entry.data_file}.archive.json')
                return

        else:
            log_warning(self, logger, f'The txt-file {mainfile} cannot be parsed -> no suitable parser for this method available')
            archive.metadata.comment = "Not parsed!"
            return






        #elif measurement == "SPV":
        #    entry = UMR_trSPVmeasurement()

        #elif measurement == "PL":
        #    entry = UMR_PLmeasurement()


        #archive.metadata.entry_name = os.path.basename(mainfile)    # Name des Rohfiles, der in Nomad gespeichert wird (ohne Parsing)




