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

from nomad.config.models.plugins import ParserEntryPoint


class CicciTXTParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_perolab_umr.parsers.parser import CicciTXTParser

        return CicciTXTParser(**self.dict())


cicci_txt_parser_entry_point = CicciTXTParserEntryPoint(
    name='TXT Parser',
    aliases=['parser/UMR'],
    description='Parser which parses txt measurement files. It creates the corrsponding entry and references the  parser entry point configuration.',
    mainfile_name_re=r'.*\.txt$', # match ".txt" am Dateinamensende
    mainfile_contents_re = r'^\s*##\s+Header\s+##\s*',  # Match with "## Header ##" --> Cicci
)


# Test Parser - can be deleted
class MyParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_perolab_umr.parsers.myparser import MyParser

        return MyParser(**self.dict())


myparser = MyParserEntryPoint(
    name = 'MyParser',
    description = 'My custom parser.',
    mainfile_name_re = '.*\.myparser',
)