from typing import Dict

from nomad.datamodel import EntryArchive
from nomad.parsing import MatchingParser


class MyParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger=None,
        child_archives: Dict[str, EntryArchive] = None,
    ) -> None:
        logger.info('MyParser called')
        logger.info('Hallo')

        from ..schema_packages.characterization.jv_measurement import UMR_JVMeasurement
        from baseclasses.helper.utilities import create_archive
        
        entry = UMR_JVMeasurement()           
        create_archive(entry, archive, f'{entry.data_file}.archive.json') 
