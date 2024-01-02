import csv
from typing import TextIO
from pandas import DataFrame, read_csv
import numpy as np
from argendata.utils.gwrappers import GResource, GFile
from argendata.utils import getattrc
from argendata.utils.files.charsets import get_codecs
from .subtopico import Subtopico
from .verificador.abstracto import Verifica


@Verifica["Archivo"]
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


@Verifica[Subtopico]
class ControlSubtopico:
    a_verificar: Subtopico
    datasets: set[str]

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

    @staticmethod
    def verificar_nivel_registro(plantilla, 
                                columnas = ['orden_grafico','dataset_archivo','script_archivo', 
                                           'variable_nombre','url_path','fuente_nombre','institucion']):
        """Verifica que no haya registros duplicados en la plantilla. Los registros son
        observablemente iguales si tienen los mismos valores en todas las columnas especificadas."""

        result = None
        n_graficos = len(set(plantilla['orden_grafico']))

        nivel_registro = plantilla.groupby(columnas).size()    
        errores = np.unique(nivel_registro[nivel_registro > 1].index.get_level_values('orden_grafico').tolist())
        if len(errores) > 0:
           result = ", ".join(map(str, errores))

        return result

    @staticmethod    
    def inspeccion_fuentes(plantilla, columnas=['fuente_nombre', 'institucion']):
        return plantilla[columnas].dropna().drop_duplicates()
    
    @staticmethod
    def verificar_completitud(plantilla: DataFrame, 
                              datasets: set[str], 
                              not_target: list[str] = ['seccion_desc','nivel_agregacion', 'unidad_medida']) -> DataFrame:
        """Busca filas incompletas"""
        _plantilla = plantilla.copy()
        _plantilla = _plantilla.loc[_plantilla.dataset_archivo.isin(datasets), _plantilla.columns.difference(not_target)] 
        _plantilla = _plantilla.groupby('dataset_archivo').agg(lambda x: x.isna().sum())
        _plantilla = _plantilla.stack().reset_index()
        _plantilla.columns = ['dataset_archivo','columna_plantilla','filas_incompletas']
        _plantilla = _plantilla[_plantilla.filas_incompletas > 0]

        return _plantilla

    def verificacion_nivel_registro(self, a_verificar: Subtopico):
        return ControlSubtopico.verificar_nivel_registro(a_verificar.plantilla)

    def verificacion_fuentes(self, a_verificar: Subtopico):
        return ControlSubtopico.inspeccion_fuentes(a_verificar.plantilla)

    def verificacion_sistema_de_archivos(self, a_verificar: Subtopico):
        plantilla = a_verificar.plantilla
        datasets = ControlSubtopico.ConteoArchivos()
        datasets.declarados = set(plantilla['dataset_archivo'])
        datasets.efectivos = set(
            map(getattrc('title'), a_verificar.dataset.resources))

        self.datasets = datasets.interseccion

        self.log.debug(f'#Datasets declarados = {len(datasets.declarados)}')
        self.log.debug(f'#Datasets efectivos = {len(datasets.efectivos)}')
        self.log.debug(f'#Intersección = {len(self.datasets)}')

        scripts_carpeta = a_verificar.carpeta.find_by_name('scripts')
        scripts = ControlSubtopico.ConteoArchivos()
        scripts.declarados = set(plantilla['script_archivo'])
        scripts.efectivos = set(
            map(getattrc('title'), scripts_carpeta.resources))

        self.scripts = scripts.interseccion
        self.log.debug(f'#Scripts declarados = {len(scripts.declarados)}')
        self.log.debug(f'#Scripts efectivos = {len(scripts.efectivos)}')
        self.log.debug(f'#Intersección = {len(self.scripts)}')

        completitud = ControlSubtopico.verificar_completitud(plantilla, self.datasets)
        self.log.info('No hay filas incompletas' if completitud.empty else 'Hay filas incompletas')

    


    def verificacion_datasets(self, a_verificar):
        csvs: filter[GFile] = filter(lambda x: x.title in self.datasets, a_verificar.dataset.resources)
        result = dict()
        for x in csvs:
            path = x.download(f'./tmp/{x.DEFAULT_FILENAME}')
            resultados_csv = ControlCSV(x.title, path).verificar_todo()
            encoding = resultados_csv['verificacion_encoding']
            delimiter = resultados_csv['verificacion_delimiter']
            df = read_csv(path, delimiter=delimiter, encoding=encoding)
            
        return result