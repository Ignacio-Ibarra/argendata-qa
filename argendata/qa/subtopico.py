from logging import Logger

import pandas

from argendata.utils.gwrappers import GFolder, GResource, GDrive
from argendata.constants import carpeta_subtopico
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

    def detectar_entregas(self) -> list[GResource]:
        return self.carpeta.find_by_recursion('datasets/outputs').resources

    def __init__(self, other: GFolder | str, entrega: int):
        if isinstance(other, str):
            Subtopico.__init__(self, GResource.from_id(other))

        self.carpeta = other
        self.title = other.title
        self.log = LoggerFactory.getLogger(f'subtopico.{self.title}')

        plantilla = self.carpeta.find_by_name(carpeta_subtopico(self.carpeta.title))
        plantilla_file = GDrive.download_xlsx(plantilla.id)
        self.plantilla = pandas.read_excel(plantilla_file, sheet_name='COMPLETAR', header=0)
        self.log.debug(f'Found, downloaded and parsed metadata for {plantilla.title}')

        # FIXME: Cambiar ésto para agarrar la última entrega, o bien decidir en función de la cantidad de archivos.
        #   Está hardcodeado sólo para poder testearlo.
        # self.dataset: GFolder = next(filter(lambda x: 'segunda' in x.title, self.detectar_entregas()))
        # self.log.debug(f'Found dataset with version {self.dataset.title}')
        entregas_alias = ['primera', 'segunda', 'update']
        e_i = entrega-1
        entrega = entregas_alias[e_i]

        entregas = self.detectar_entregas()
        self.dataset: GFolder = next(filter(lambda x: entrega in x.title, self.detectar_entregas()), None)

        if self.dataset is None:
            self.log.error(f'No se encontró la entrega {entrega} en {self.title}')
        else:
            self.log.debug(f'Found dataset with version {self.dataset.title}')
            return

        # if folder 'outputs' has files ending in '.csv'
        are_csvs_in_folder = any(map(lambda x: x.title.endswith('.csv'), self.carpeta.find_by_recursion('datasets/outputs').resources))
        if not are_csvs_in_folder:
            self.log.error(f'No se encontraron archivos .csv en la entrega {entrega} en {self.title}')
            raise FileNotFoundError(f'No se encontraron archivos .csv en la entrega {entrega} en {self.title}')
        
        self.dataset = self.carpeta.find_by_recursion('datasets/outputs')


    @classmethod
    def from_name(cls, name: str, entrega: int, root: str = None):
        if not root:
            from argendata.constants import get_argendata_folder_id
            root = get_argendata_folder_id()

        result = cls(GResource.from_id(root).find_by_recursion(f'SUBTOPICOS/{name}'), entrega)
        result.log.debug('Initialized correctly from name.')
        return result

    def verificar(self, verificador: Verificador) -> dict:
        return verificador(self.title, self).verificar_todo()