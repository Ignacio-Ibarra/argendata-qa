import csv
from typing import TextIO
from pandas import DataFrame, read_csv
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

    def verificacion_encoding(self, a_verificar):
        codecs = get_codecs(a_verificar)
        self.codec = 'utf-8' if len(codecs) <= 0 else codecs[0][0]
        return self.codec
    
    def verificacion_delimiter(self, a_verificar):
        codec = self.codec
        with open(a_verificar, 'r', encoding=codec) as csvfile:
            self.delimiter = str(csv.Sniffer().sniff(csvfile.read()).delimiter)
        return self.delimiter

class Plantilla(DataFrame):
    ...

class Consistencia(tuple[DataFrame, Plantilla]):
    ...

@Verifica[Consistencia, "verificacion_"]
class TestConsistencia:
    a_verificar: Consistencia
    name: str

    def __init__(self, df, plantilla) -> None:
        self.a_verificar = (df, plantilla)
    
    def verificacion_nueva(self, a_verificar: Consistencia):
        df, plantilla = a_verificar
        ds_declarados = plantilla.loc[plantilla.dataset_archivo == self.name, ['dataset_archivo','variable_nombre','tipo_dato','primary_key','nullable']].drop_duplicates()
        var_dtypes: list[tuple[str, str]] = \
            df.dtypes.apply(lambda x: str(x)).reset_index().to_records(index=False).tolist()
        
        self.log.debug(var_dtypes)


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
            resultados_csv = TestCSV(x.title, path).verificar_todo()
            encoding = resultados_csv['verificacion_encoding']
            delimiter = resultados_csv['verificacion_delimiter']
            df = read_csv(path, delimiter=delimiter, encoding=encoding)
            resultados_consistencia = TestConsistencia(x.title, df, subtopico.plantilla).verificar_todo()
            
        return result