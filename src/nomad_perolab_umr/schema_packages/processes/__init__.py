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


class BladeCoatingSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.processes.blade_coating import m_package

        return m_package

blade_coating_schema = BladeCoatingSchemaPackageEntryPoint(
    name='Blade Coating Schema',
    description='Schema package containing sections for Blade Coating.',
)



class CleaningSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.processes.cleaning import m_package

        return m_package

cleaning_coating_schema = CleaningSchemaPackageEntryPoint(
    name='Cleaning Schema',
    description='Schema package containing sections for Cleaning.',
)



class SpinCoatingSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.processes.spin_coating import m_package

        return m_package

spin_coating_schema = SpinCoatingSchemaPackageEntryPoint(
    name='Spin Coating Schema',
    description='Schema package containing sections for Spin Coating.',
)



class SprayPyrolysisSchemaPackageEntryPoint(SchemaPackageEntryPoint):

    def load(self):
        from nomad_perolab_umr.schema_packages.processes.spray_pyrolysis import m_package

        return m_package

spray_pyrolysis_schema = SprayPyrolysisSchemaPackageEntryPoint(
    name='Spray Pyrolysis Schema',
    description='Schema package containing sections for Spray Pyrolysis.',
)


#class ProcessBaseclassesSchemaPackageEntryPoint(SchemaPackageEntryPoint):

#    def load(self):
#        from nomad_perolab_umr.schema_packages.processes.process_baseclasses import m_package

 #       return m_package

#spray_pyrolysis_schema = ProcessBaseclassesSchemaPackageEntryPoint(
#    name='Process Baseclasses Schema',
#    description='Schema package containing sections for process baseclassses.',
#)

# Process baseclasses ???



"""
Whenever you add a new process in a new python file, you have to also enter a new SchemaPackageEntryPoint for this module and in the module itelf create a m_package.

"""
