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


# Imports Nomad
from nomad.datamodel.data import EntryDataCategory
from nomad.metainfo.metainfo import Category

# Categories, which are displayed in the Dropdown menu under "Create new entry from schema"


class UMRCreateCategory(EntryDataCategory):
    m_def = Category(label='UMR Create Batches', categories=[EntryDataCategory])

class UMRCollectionCategory(EntryDataCategory):
    m_def = Category(label='Other UMR Sections', categories=[EntryDataCategory])

class UMRMeasurementCategory(EntryDataCategory):
    m_def = Category(label='UMR Characterization Sections', categories=[EntryDataCategory])

class UMRSynthesisCategory(EntryDataCategory):
    m_def = Category(label='UMR Synthesis Sections', categories=[EntryDataCategory])

class UMRProcessesCategory(EntryDataCategory):
    m_def = Category(label='UMR Processes Sections', categories=[EntryDataCategory])

