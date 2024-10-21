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


class ConnectionTestSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.characterization.connection_test import m_package

        return m_package

connection_test_schema = ConnectionTestSchemaPackageEntryPoint(
    name='Connection Test Schema',
    description='Schema package containing sections for Connection Test (Cicci).',
)



class EQESchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.characterization.eqe_measurement import m_package

        return m_package

eqe_schema = EQESchemaPackageEntryPoint(
    name='EQE Measurement Schema',
    description='Schema package containing sections for EQE Measurement.',
)



class JVSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.characterization.jv_measurement import m_package

        return m_package

jv_schema = JVSchemaPackageEntryPoint(
    name='JV Measurement Schema',
    description='Schema package containing sections for JV Measurement.',
)



class MPPTrackingSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.characterization.mpp_tracking import m_package

        return m_package

mpp_tracking_schema = MPPTrackingSchemaPackageEntryPoint(
    name='MPP Tracking  Schema',
    description='Schema package containing sections for Maximum Power Point Tracking.',
)



class StabilityTestSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.characterization.stability_test import m_package

        return m_package

stability_test_schema = StabilityTestSchemaPackageEntryPoint(
    name='Stability Test  Schema',
    description='Schema package containing sections for Stability Tests (Ageing Measurements).',
)












"""
Whenever you add a new characterization technique in a new python file, you have to also enter a new SchemaPackageEntryPoint for this module and in the module itelf create a m_package.

"""