import csv
from typing import TextIO
from pandas import DataFrame, read_csv
from argendata.utils.gwrappers import GResource, GFile
from argendata.utils import getattrc
from argendata.utils.files.charsets import get_codecs
from .subtopico import Subtopico
from .verificador.abstracto import Verifica


@Verifica["Archivo", "verificacion_"]
class ControlCSV:
    a_verificar: str

    def __init__(self, path: str):
        self.a_verificar = path

    def verificacion_encoding(self, a_verificar):
        codecs = get_codecs(a_verificar)
        self.codec = 'utf-8' if len(codecs) <= 0 else codecs[0][0]
        return self.codec
    
    def verificacion_delimiter(self, a_verificar):
        codec = self.codec
        with open(a_verificar, 'r', encoding=codec) as csvfile:
            self.delimiter = str(csv.Sniffer().sniff(csvfile.read()).delimiter)
        return self.delimiter

@Verifica["Consistencia", "verificacion_"]
class ControlConsistencia:
    df : DataFrame
    plantilla : DataFrame
    name: str

    def __init__(self, df, plantilla) -> None:
        self.df = df
        self.plantilla = plantilla
    
    def verificacion_nueva(self, df, plantilla):
        ds_declarados = plantilla.loc[plantilla.dataset_archivo == self.name, ['dataset_archivo','variable_nombre','tipo_dato','primary_key','nullable']].drop_duplicates()
        var_dtypes: list[tuple[str, str]] = \
            df.dtypes.apply(lambda x: str(x)).reset_index().to_records(index=False).tolist()
        
        self.log.debug(var_dtypes)


@Verifica[Subtopico, "verificacion_"]
class ControlSubtopico:
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

    def verificacion_sistema_de_archivos(self, a_verificar):
        plantilla = a_verificar.plantilla
        datasets = ControlSubtopico.ConteoArchivos()
        datasets.declarados = set(plantilla['dataset_archivo'])
        datasets.efectivos = set(
            map(getattrc('title'), GResource.from_id('1JHDYAk1hL35DOrhh5TWlSLF0YbwCi8sL').resources))

        self.dataset = datasets.interseccion

        self.log.debug(f'Datasets declarados = {datasets.declarados}')
        self.log.debug(f'Datasets efectivos = {datasets.efectivos}')
        self.log.debug(f'Intersección = {self.dataset}')

    def verificacion_dataset(self, a_verificar):
        csvs: filter[GFile] = filter(lambda x: x.title in self.dataset, a_verificar.dataset.resources)
        result = dict()
        for x in csvs:
            path = x.download(f'./tmp/{x.DEFAULT_FILENAME}')
            resultados_csv = ControlCSV(x.title, path).verificar_todo()
            encoding = resultados_csv['verificacion_encoding']
            delimiter = resultados_csv['verificacion_delimiter']
            df = read_csv(path, delimiter=delimiter, encoding=encoding)
            resultados_consistencia = ControlConsistencia(x.title, df, a_verificar.plantilla).verificar_todo()
            
        return result