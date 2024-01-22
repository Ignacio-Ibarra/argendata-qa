import csv
from typing import TextIO, Iterable
from pandas import DataFrame, read_csv
from pandas.errors import ParserError
import numpy as np
from argendata.utils.gwrappers import GResource, GFile
from argendata.utils import getattrc, strip_accents, dtypes_conversion as dtype_map
from argendata.utils.files.charsets import get_codecs
from .subtopico import Subtopico
from .verificador.abstracto import Verifica
from .controles_calidad import make_controls
import chardet
import re

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
            self.log.debug('Usando programa propio para detectar encoding.')
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

class BadColumnsException(ValueError):
    def __init__(self, __object: str, __expected: Iterable[str], __got: Iterable[str]) -> None:
        self.object = __object
        self.expected = set(__expected)
        self.got = set(__got)
    
    def __str__(self) -> str:
        declarado_no_efvo = self.expected - self.got
        efvo_no_declarado = self.got - self.expected

        result = f'BadColumnsException: {self.object}'
        if declarado_no_efvo:
            result += f'\n\tThe following columns are in the template, but not in the dataset: {declarado_no_efvo}'

        if efvo_no_declarado:
            result += f'\n\tThe following columns are in the dataset, but not in the template {efvo_no_declarado}'

        return result

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
        _tipo_dato = _tipo_dato.fillna("no completo").str.lower().apply(strip_accents)
        _tipo_dato = _tipo_dato.map(dtype_map)

        plantilla.loc[:, 'tipo_dato'] = _tipo_dato

        plantilla['variable_nombre'].apply(lambda x: str(x).strip())

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
        # if len(errores) > 0:
        #     result = ", ".join(map(str, errores))

        # return result
        return n_graficos, list(map(int, errores))

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

        datasets = ControlSubtopico.ConteoArchivos()
        datasets.declarados = set(plantilla['dataset_archivo'])
        datasets.efectivos = set(
            map(getattrc('title'), a_verificar.dataset.resources))
        
        datasets.efectivos = set(map(lambda x: x.strip(), datasets.efectivos))
        datasets.declarados = set(map(lambda x: x.strip(), datasets.declarados))

        self.datasets = datasets.interseccion

        # Lo agrego a mano para loggearlo pero habría que estructurar el resultado
        datasets_no_cargados = datasets.declarados - datasets.efectivos
        datasets_no_declarados = datasets.efectivos - datasets.declarados

        self.log.debug(f'#Datasets declarados = {len(datasets.declarados)}')
        self.log.debug(f'#Datasets efectivos = {len(datasets.efectivos)}')
        self.log.debug(f'#Intersección = {len(self.datasets)}')

        self.log.debug(f"#Datasts no cargados = {len(datasets_no_cargados)}")
        if len(datasets_no_cargados)>0: 
            self.log.debug("\n".join("\t'"+x+"'" for x in datasets_no_cargados))

        self.log.debug(f"#Datasts no declarados = {len(datasets_no_declarados)}")
        if len(datasets_no_declarados) > 0: 
            self.log.debug("\n".join("\t'"+x+"'" for x in datasets_no_declarados))

        scripts_carpeta = a_verificar.carpeta.find_by_name('scripts')
        scripts = ControlSubtopico.ConteoArchivos()
        scripts.declarados = set(plantilla['script_archivo'])
        scripts.efectivos = set(
            map(getattrc('title'), scripts_carpeta.resources))
        
        scripts.efectivos = set(map(lambda x: x.strip(), scripts.efectivos))
        scripts.declarados = set(map(lambda x: x.strip(), scripts.declarados))

        self.scripts = scripts.interseccion
        
        # Lo agrego a mano para loggearlo pero habría que estructurar el resultado
        scripts_no_cargados = scripts.declarados - scripts.efectivos
        scripts_no_declarados = scripts.efectivos - scripts.declarados

        self.log.debug(f'#Scripts declarados = {len(scripts.declarados)}')
        self.log.debug(f'#Scripts efectivos = {len(scripts.efectivos)}')
        self.log.debug(f'#Intersección = {len(self.scripts)}')
        
        self.log.debug(f"#Scripts no cargados = {len(scripts_no_cargados)}")
        if len(scripts_no_cargados)>0: 
            self.log.debug("\n".join("\t'"+x+"'" for x in scripts_no_cargados))

        self.log.debug(f"#Scripts no declarados = {len(scripts_no_declarados)}")
        if len(scripts_no_declarados)>0: 
            self.log.debug("\n".join("\t'"+x+"'" for x in scripts_no_declarados))

        completitud = ControlSubtopico.verificar_completitud(plantilla, self.datasets)
        self.log.info('No hay filas incompletas' if completitud.empty else 'Hay filas incompletas')

        resultado_info = {
            'datasets': {'declarados': list(datasets.declarados), 'efectivos': list(datasets.efectivos), 'interseccion': list(self.datasets)},
            'scripts':  {'declarados': list(scripts.declarados),  'efectivos': list(scripts.efectivos),  'interseccion': list(self.scripts)}
        }

        return completitud.empty, resultado_info, completitud.to_dict()

    def verificar_dataset(self, dataset: GFile, plantilla: DataFrame):
        partial_result = dict()
        variables = plantilla.loc[:, 'variable_nombre']

        path = dataset.download(f'./tmp/{dataset.DEFAULT_FILENAME}')

        resultados_csv = ControlCSV(dataset.title, path).verificar_todo()

        encoding = resultados_csv['verificacion_encoding']
        delimiter = resultados_csv['verificacion_delimiter']
        partial_result['detected_encoding'] = encoding
        partial_result['delimiter'] = delimiter

        df = read_csv(path, delimiter=delimiter, encoding=encoding)
        df.columns = df.columns.map(lambda x: x.strip())

        expected = set(map(lambda x: x.strip(), variables.to_list()))
        self.log.debug(f'Columnas esperadas = {expected}')
        got = set(df.columns)
        self.log.debug(f'Columnas encontradas = {got}')

        if got != expected:
            partial_result.setdefault('errors', []).append(BadColumnsException(dataset.title, (expected), (got)))
            if len(got) != len(expected):
                return partial_result

        keys = variables.loc[plantilla.primary_key == True]
        keys = keys.str.strip().to_list()

        not_nullable = variables.loc[plantilla.nullable == False]
        not_nullable = not_nullable.str.strip().to_list()

        diccionario = {
            # 'tidy_data': keys,
            'variables': (plantilla, ),
            # 'duplicates': keys,
            # 'nullity_check': not_nullable,
            'header': (df.columns, ),
            'special_characters': ...
        }

        flags_errores = {}

        if len(keys) > 0:
            diccionario['tidy_data'] = diccionario['duplicates'] = keys

        set_nn = set(not_nullable)
        set_cs = set(df.columns)
        intersect_columnas = set_nn.intersection(set_cs)
        
        if intersect_columnas == set(not_nullable):
            diccionario['nullity_check'] = not_nullable if len(not_nullable) > 0 else (not_nullable, )
        else:
            flags_errores['nullity_check'] = (None, list(set_nn), list(set_cs))
        
        ensure_quality = make_controls(diccionario)

        quality_analysis = ensure_quality(df)
        
        for k,v in flags_errores.items():
            quality_analysis[k] = v
        
        partial_result['quality_checks'] = quality_analysis
        return partial_result
    
    def error_handler(self, e: Exception, x):
            if isinstance(e, UnicodeDecodeError):
                self.log.error(f"No se pudo abrir {x.title}")
                self.log.error(str(e))
            if isinstance(e, ParserError):
                if re.match(pattern=".*Expected .* fields in line .* saw .*", string=str(e)):
                    self.log.critical("Error en "+x.title)
                    self.log.critical(str(e))
            if isinstance(e, BadColumnsException):
                self.log.error("Error en "+x.title)
                self.log.error(f'Columnas mal formadas en {x}')
            
            return str(e)

    def verificacion_datasets(self, a_verificar):
        csvs: filter[GFile] = filter(lambda x: x.title in self.datasets, a_verificar.dataset.resources)
        result = dict()
        errors = []
        for x in csvs:
            if 'geojson' in x.title.lower():
                self.log.info(f'Salteando {x.title} por ser GeoJSON')
                continue
            slice_plantilla = a_verificar.plantilla.loc[a_verificar.plantilla.dataset_archivo.str.strip() == x.title]
            partial_result: dict
            try:
                partial_result = self.verificar_dataset(x, slice_plantilla)

                if 'errors' in partial_result:
                    for i, error in enumerate(partial_result['errors']):
                        self.log.error(str(error))
                        partial_result['errors'][i] = str(error)
                        # partial_result.setdefault('errors', []).append(str(error))
                    errors.append((x.title, partial_result['errors']))

                result[x.title] = partial_result
            except Exception as e:
                errors.append((x.title, str(e)))
        
        if len(errors) > 0:
            print()
            self.log.error("Los siguientes datasets tuvieron errores:")
            for error in errors:
                self.log.error("\t"+error[0])
            print()

        return result, errors
