import csv
from typing import TextIO
from pandas import DataFrame, read_csv
import numpy as np
from argendata.utils.gwrappers import GResource, GFile
from argendata.utils import getattrc, strip_accents, dtypes_conversion as dtype_map
from argendata.utils.files.charsets import get_codecs
from .subtopico import Subtopico
from .verificador.abstracto import Verifica
from .controles_calidad import make_controls
import chardet

def encoding_with_chardet(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read(10000)
        result = chardet.detect(raw_data)

    return result['encoding']

@Verifica["Archivo"]
class ControlCSV:
    a_verificar: str

    def __init__(self, path: str):
        self.a_verificar = path

    def verificacion_encoding(self, a_verificar):
        codecs = get_codecs(a_verificar)
        if len(codecs) > 0:
            self.codec = codecs[0][0]
        else:
            self.log.debug('Usando chardet para detectar encoding.')
            self.codec = encoding_with_chardet(a_verificar)

        if self.codec is None:
            self.log.error('Encoding invalido. Usando utf-8 como default.')
            self.codec = 'utf-8'
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
        plantilla = s.plantilla

        _tipo_dato = plantilla.loc[:, 'tipo_dato']
        _tipo_dato = _tipo_dato.str.lower().apply(strip_accents)
        _tipo_dato = _tipo_dato.map(dtype_map).fillna("no completo")

        plantilla.loc[:, 'tipo_dato'] = _tipo_dato

        plantilla['variable_nombre'].apply(lambda x: x.strip())

        self.a_verificar = s

    @staticmethod
    def verificar_nivel_registro(plantilla,
                                 columnas=['orden_grafico', 'dataset_archivo', 'script_archivo',
                                           'variable_nombre', 'url_path', 'fuente_nombre', 'institucion']):
        """Verifica que no haya registros duplicados en la plantilla. Los registros son
        observablemente iguales si tienen los mismos valores en todas las columnas especificadas."""

        result = 'OK'
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
                              not_target: list[str] = ['seccion_desc', 'nivel_agregacion',
                                                       'unidad_medida']) -> DataFrame:
        """Busca filas incompletas"""
        _plantilla = plantilla.copy()
        _plantilla = _plantilla.loc[
            _plantilla.dataset_archivo.isin(datasets), _plantilla.columns.difference(not_target)]
        _plantilla = _plantilla.groupby('dataset_archivo').agg(lambda x: x.isna().sum())
        _plantilla = _plantilla.stack().reset_index()
        _plantilla.columns = ['dataset_archivo', 'columna_plantilla', 'filas_incompletas']
        _plantilla = _plantilla[_plantilla.filas_incompletas > 0]

        return _plantilla

    def verificacion_nivel_registro(self, a_verificar: Subtopico):
        return ControlSubtopico.verificar_nivel_registro(a_verificar.plantilla)

    def verificacion_fuentes(self, a_verificar: Subtopico):
        return ControlSubtopico.inspeccion_fuentes(a_verificar.plantilla).to_records(index=False).tolist()

    def verificacion_sistema_de_archivos(self, a_verificar: Subtopico):
        plantilla = a_verificar.plantilla

        columnas = ['dataset_archivo', 'variable_nombre', 'tipo_dato', 'primary_key', 'nullable']
        datasets_declarados_df: DataFrame = plantilla[columnas].drop_duplicates()

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
        return completitud.empty

    def verificacion_datasets(self, a_verificar):
        csvs: filter[GFile] = filter(lambda x: x.title in self.datasets, a_verificar.dataset.resources)
        result = dict()
        for x in csvs:
            partial_result = dict()
            slice_plantilla = a_verificar.plantilla.loc[a_verificar.plantilla.dataset_archivo == x.title]
            variables = slice_plantilla.loc[:, 'variable_nombre']

            path = x.download(f'./tmp/{x.DEFAULT_FILENAME}')
            resultados_csv = ControlCSV(x.title, path).verificar_todo()

            encoding = resultados_csv['verificacion_encoding']
            delimiter = resultados_csv['verificacion_delimiter']
            partial_result['detected_encoding'] = encoding
            partial_result['delimiter'] = delimiter

            df = read_csv(path, delimiter=delimiter, encoding=encoding)
            df.columns = df.columns.map(lambda x: x.strip())

            if set(df.columns) != set(variables.to_list()):
                self.log.error(f'Columnas mal formadas en {x}')
                continue;

            keys = variables.loc[slice_plantilla.primary_key == True]
            keys = keys.str.strip().to_list()

            not_nullable = variables.loc[slice_plantilla.nullable == False]
            not_nullable = not_nullable.str.strip().to_list()

            diccionario = {
                'tidy_data': keys,
                'variables': (slice_plantilla, ),
                'duplicates': keys,
                # 'nullity_check': not_nullable,
                'header': (df.columns, ),
                'special_characters': ...
            }

            flags_errores = {}

            set_nn = set(not_nullable)
            set_cs = set(df.columns)
            intersect_columnas = set_nn.intersection(set_cs)
            
            if intersect_columnas == set(not_nullable):
                diccionario['nullity_check'] = not_nullable
            else:
                flags_errores['nullity_check'] = (None, list(set_nn), list(set_cs))
            
            ensure_quality = make_controls(diccionario)

            quality_analysis = ensure_quality(df)
            
            for k,v in flags_errores.items():
                quality_analysis[k] = v

            partial_result['quality_checks'] = quality_analysis
            result[x.title] = partial_result

        return result
