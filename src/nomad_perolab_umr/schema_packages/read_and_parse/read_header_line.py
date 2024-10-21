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


# HELPER FUNCTION TO READ HEADER LINES OF CICCI MEASUREMENTS

def read_header_line(line, dict):
    """
    READS HEADER LINES AND ADDS THEM TO DICTIONARY (KEY-VALUE PAIRS)
    
    Parameters:
        line (str): current line in file
        dict (dict): dictionary to be filled with data    Returns: dict (dictionary filled with data)
    Returns:
        dict (dict): dictionary filled with data
    """
    
    parts=line.split('\t')        # Split line at tab character
    key=parts[0].strip()          # First part of the line is the key (Strip whitespace) 
    if len(parts) == 2:           # Check if line correctly splits into two parts -> Value was entered
        value = parts[1].strip()  # Second part of the line is value (Strip whitespace)
        dict[key] = value         # Add key-value pair to dictionary
    #else:
    #    dict.setdefault(key, None) # Add None values for keys which did not exist before
    
    return dict









