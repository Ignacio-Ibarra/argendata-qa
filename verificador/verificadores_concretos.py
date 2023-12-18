from typing import TextIO

from gwrappers import GResource, GFile
from utils import getattrc
from utils.files.charsets import get_codecs
from verificador.subtopico import Subtopico
from verificador.verificadores_abstractos import Verifica


class Archivo(str):
    ...


@Verifica[Archivo, "verificacion_"]
class TestCSV:
    a_verificar: Archivo

    def __init__(self, a: Archivo):
        self.a_verificar = a

    def verificacion_encoding(self, csv):
        codecs = get_codecs(csv)
        if len(codecs) > 0:
            self.log.info(' '.join(str(x) for x in codecs[0]))
        return len(codecs) > 0


@Verifica[Subtopico, "verificacion_"]
class Test:
    a_verificar: Subtopico

    class ConteoArchivos:
        declarados: None | set[str]
        efectivos: None | set[str]

        def __init__(self):
            self.declarados = None
            self.efectivos = None
            self._interseccion = None

        @property
        def interseccion(self):
            self._interseccion = self.declarados.intersection(self.efectivos)
            return self._interseccion

    def __init__(self, s: Subtopico):
        self.a_verificar = s

    def verificacion_sistema_de_archivos(self, subtopico):
        plantilla = subtopico.plantilla
        datasets = Test.ConteoArchivos()
        datasets.declarados = set(plantilla['dataset_archivo'])
        datasets.efectivos = set(
            map(getattrc('title'), GResource.from_id('1JHDYAk1hL35DOrhh5TWlSLF0YbwCi8sL').resources))

        self.dataset = datasets.interseccion

        self.log.debug(f'Datasets declarados = {datasets.declarados}')
        self.log.debug(f'Datasets efectivos = {datasets.efectivos}')
        self.log.debug(f'Intersección = {self.dataset}')

    def verificacion_dataset(self, subtopico):
        a_verificar: filter[GFile] = filter(lambda x: x.title in self.dataset, subtopico.dataset.resources)
        result = dict()
        for x in a_verificar:
            path = x.download(f'./tmp/{x.DEFAULT_FILENAME}')
            result[x.title] = TestCSV(x.title, path).verificar_todo()
        return result
