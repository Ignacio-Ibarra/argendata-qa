from logging import Logger

import pandas

from argendata.utils.gwrappers import GFolder, GResource, GDrive
from argendata.constants import carpeta_subtopico, ARGENDATA_FOLDER_ID
from pandas import DataFrame
from .verificador.abstracto import Verificador

from argendata.utils.logger import LoggerFactory


class Subtopico:
    """Representa un subtópico. Guarda toda la información relacionada, y tiene operaciones ad-hoc específicas
       para hacer queries al mismo."""

    title: str
    carpeta: GFolder
    plantilla: DataFrame
    log: Logger

    def detectar_entregas(self):
        return self.carpeta.find_by_recursion('datasets/outputs').resources

    def __init__(self, other: GFolder | str):
        if isinstance(other, str):
            Subtopico.__init__(self, GResource.from_id(other))

        self.carpeta = other
        self.title = other.title
        self.log = LoggerFactory.getLogger(f'subtopico.{self.title}')

        plantilla = self.carpeta.find_by_name(carpeta_subtopico(self.carpeta.title))
        plantilla_file = GDrive.download_xlsx(plantilla.id)
        self.plantilla = pandas.read_excel(plantilla_file, sheet_name='COMPLETAR', header=6)
        self.log.debug(f'Found, downloaded and parsed metadata for {plantilla.title}')

        # FIXME: Cambiar ésto para agarrar la última entrega, o bien decidir en función de la cantidad de archivos.
        #   Está hardcodeado sólo para poder testearlo.
        self.dataset = next(filter(lambda x: 'primera' in x.title, self.detectar_entregas()))
        self.log.debug(f'Found dataset with version {self.dataset.title}')

    @classmethod
    def from_name(cls, name: str, root: str = ARGENDATA_FOLDER_ID):
        result = cls(GResource.from_id(root).find_by_recursion(f'SUBTOPICOS/{name}'))
        result.log.debug('Initialized correctly from name.')
        return result

    def verificar(self, verificador: Verificador) -> dict:
        return verificador(self.title, self).verificar_todo()