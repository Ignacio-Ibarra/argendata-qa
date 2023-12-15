from gwrappers import GFolder, GResource
from typing import NamedTuple

from logger import inject_logger
from utils.colors import colorize_bool
from verificador.correctitud_archivos import VerificadorCSV


class CarpetasSubtopico(NamedTuple):
    datasets: GFolder
    documento: GFolder
    scripts: GFolder

    def __str__(self):
        return (f'CarpetasSubtopicos(datasets={self.datasets.id}, '
                f'documento={self.documento.id}, '
                f'scripts={self.scripts.id})')

    def __repr__(self):
        return str(self)


@inject_logger('verificador_subtopico')
class VerificadorSubtopico:
    carpetas: CarpetasSubtopico

    def __init__(self, subtopico: GFolder):
        # noinspection PyTypeChecker
        # Asumo que el sistema de archivos es correcto. (Esencialmente que subtopico.find no es None)
        self.carpetas = CarpetasSubtopico(subtopico.find('datasets', by='name'),
                                          subtopico.find('documento', by='name'),
                                          subtopico.find('scripts', by='name'))

        # noinspection PyTypeChecker
        # Asumo que existe la carpeta.
        segunda_entrega: GFolder = (self.carpetas.datasets
                                   .find(value='outputs/datasets_segunda_entrega',
                                         by='recursion'))

        VerificadorSubtopico.log.debug(segunda_entrega)

        for resource in segunda_entrega.resources:
            results: dict = VerificadorCSV(resource).verificar_todo()
            for name, result in results.items():
                VerificadorSubtopico.log.info(f'{resource.title} - {name} : {colorize_bool(result)}')

    @classmethod
    def from_name(cls, name: str, subtopicos_folder_id='1ibHUVUoo2VGjYA2_iN_Qy2-bNQm54Rlx'):
        subtopicos = GResource.from_id(subtopicos_folder_id)
        return VerificadorSubtopico(subtopicos.find(name, by='name'))
