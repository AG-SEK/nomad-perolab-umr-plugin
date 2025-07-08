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


from nomad.config.models.plugins import SchemaPackageEntryPoint


class BatchSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.batch import m_package

        return m_package

batch_schema = BatchSchemaPackageEntryPoint(
    name='Batch Schema',
    description='Schema package containing sections for Internal and External Batch including groups.',
)



class ExternalBatchPlanSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.create_external_batch import m_package

        return m_package

external_batch_plan_schema = ExternalBatchPlanSchemaPackageEntryPoint(
    name='External Batch Plan Schema',
    description='Schema package containing sections for the creation of external batches with a batch plan ELN.',
)



class InternalBatchPlanSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.create_internal_batch import m_package

        return m_package

internal_batch_plan_schema = InternalBatchPlanSchemaPackageEntryPoint(
    name='Internal Batch Plan Schema',
    description='Schema package containing sections for the creation of internal batches with a batch plan ELN.',
)



class SolarCellSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.solar_cell import m_package

        return m_package

solar_cell_schema = SolarCellSchemaPackageEntryPoint(
    name='Solar Cell Schema',
    description='Schema package containing sections for Internal and External Solar Cells and basic samples.',
)



class SubstrateSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.substrate import m_package

        return m_package

substrate_schema = SubstrateSchemaPackageEntryPoint(
    name='Substrate Schema',
    description='Schema package containing sections for Internal and External Substrates as well as Standard Substrates and Standard Substrate Lots.',
)



class BaseclassesSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.umr_baseclasses import m_package

        return m_package

baseclasses_schema = BaseclassesSchemaPackageEntryPoint(
    name='UMR Baseclasses Schema',
    description='Schema package containing for UMR customized base sections, like Instrument, Room, ...',
)



class SynthesisSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.umr_synthesis_classes import m_package

        return m_package

synthesis_schema = SynthesisSchemaPackageEntryPoint(
    name='UMR Synthesis Schema',
    description='Schema package containing secctions for Chemicals, Solutions, ...'
)


class VoilaSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.voila import m_package

        return m_package

voila_schema = VoilaSchemaPackageEntryPoint(
    name='UMR Voila Schema',
    description='Schema package containing secctions for Voila Notebooks'
)











