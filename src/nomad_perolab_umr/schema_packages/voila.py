from baseclasses.voila import VoilaNotebook
from nomad.datamodel.data import EntryData
from nomad.metainfo import SchemaPackage, Section

m_package = SchemaPackage() 

class UMR_VoilaNotebook(VoilaNotebook, EntryData):
    m_def = Section(a_eln=dict(hide=['lab_id']))

    def normalize(self, archive, logger):
        super().normalize(archive, logger)

m_package.__init_metainfo__()
