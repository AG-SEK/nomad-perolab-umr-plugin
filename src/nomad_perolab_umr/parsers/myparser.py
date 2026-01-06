
from nomad.datamodel import EntryArchive
from nomad.parsing import MatchingParser


class MyParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger=None,
        child_archives: dict[str, EntryArchive] = None,
    ) -> None:
        logger.info('MyParser called')
        logger.info('Hallo')

        from baseclasses.helper.utilities import create_archive

        from ..schema_packages.characterization.jv_measurement import UMR_JVMeasurement
        
        entry = UMR_JVMeasurement()           
        create_archive(entry, archive, f'{entry.data_file}.archive.json') 
