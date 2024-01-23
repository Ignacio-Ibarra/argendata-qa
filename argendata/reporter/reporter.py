from argendata.utils import MethodMapping
import argendata.reporter.templates as templates
from .abstracto import Template
from argendata.utils.files import file
from argendata.utils.logger import LoggerFactory
import pandas as pd
import os

ERROR_STR = "No se pudo verificar debido a un error."

def empty_df(columns: list):
    """Devuelve un DataFrame vacío con las columnas especificadas."""
    return pd.DataFrame({c: ['-'] for c in columns})

def complete(a: list, b: list) -> tuple[list, list]: # Con largos iguales
    """
    Toma dos listas, y las completa con strings vacíos para que tengan el mismo largo.
    """
    max_length = max(len(a), len(b))

    a.extend([''] * (max_length - len(a)))
    b.extend([''] * (max_length - len(b)))

    return a, b

QAUnpacker = MethodMapping()
u"""
Desempaqueta cada sección del resultado de los verificadores.
Se corresponde con `argendata.qa.controles_calidad`
"""

@QAUnpacker.register('tipo_datos')
def unpack_tipo_dato(qa: dict):
    variables_ok: bool
    dtypes: list[tuple[str, str[type]]]
    dtypes_symdif: list[tuple[str, str[type]]]
    variables_ok, dtypes, dtypes_symdif = qa['variables']
    
    columns_variables = ['Variable Nombre',
                         'Tipo de Dato Efectivo', 
                         'Tipo de Dato Declarado']

    tipo_dato_df: pd.DataFrame
    if len(dtypes_symdif) == 0:
        tipo_dato_df = empty_df(columns_variables)
    else:
        set_dif_simetrica = set(map(tuple, dtypes_symdif))
            
        variables_efectivas = dtypes
        set_efectivo = set(map(tuple,variables_efectivas)) 
        efvo_dict = {k:v for k,v in variables_efectivas}

        mal_declarado = set_dif_simetrica - set_efectivo

        data = []
        for var_decl, dtype_decl in mal_declarado:
            # Verificar si el valor está en lista_B
            if var_decl in efvo_dict:
                dtype_efvo = efvo_dict[var_decl]
                data.append( (var_decl, dtype_efvo, dtype_decl) )
        
        tipo_dato_df = pd.DataFrame(data, columns = columns_variables)
    
    return tipo_dato_df

@QAUnpacker.register('header')
def unpack_header(qa: dict):
    header_ok: bool
    wrong_cols: list[str]
    header_ok, wrong_cols = qa['header']

    if header_ok:
        header_result = 'OK'
    else:
        header_result = 'Se encontraron columnas con nombres mal formateados '\
                        'ver [documentación]((https://docs.google.com/document/d/1vH59Akk1eZTb0m4wIyEdhyVV_rx2q8lg4bG5k2tJP20/edit?usp=sharing))'
    
    return header_result

@QAUnpacker.register('tidy_data')
def unpack_tidy_data(qa: dict):
    tidy_data_ok: bool = qa.get('tidy_data')

    if tidy_data_ok is None:
        tidy_data_result = ERROR_STR
    elif tidy_data_ok:
        tidy_data_result = 'OK'
    else:
        tidy_data_result = \
            'Es posible que no tenga formato `long`, analizar archivo. Por favor completar [aquí]() si el dataset se encuentra o no'
        'en formato `long` para poder tomarlo en cuenta en un futuro reporte. En caso de que esté en formato `wide` por favor corregir el archivo',

    return tidy_data_result

@QAUnpacker.register('duplicates')
def unpack_duplicates(qa: dict):
    has_duplicates: bool = qa.get('duplicates')
    
    if has_duplicates is None:
        duplicates_result = ERROR_STR
    elif not has_duplicates:
        duplicates_result = 'OK'
    else:
        duplicates_result = 'Se encontraron filas duplicadas en el dataset, para las variables definidas como claves.'

    return duplicates_result

@QAUnpacker.register('nullity_check')
def unpack_nullity(qa: dict):
    nullity_ok: tuple|bool = qa['nullity_check']

    if isinstance(nullity_ok, tuple):
        nullity_result = ERROR_STR
    elif nullity_ok is True:
        nullity_result = 'OK'
    else:
        nullity_result = 'Se encontraron valores nulos para las variables definidas como NOT NULLABLE'

    return nullity_result

def compress_indices(indices, threshold=10) -> str:
    """
    Comprime una lista de indices si supera un threshold.
    Si es comprimida, el resultado es una cadena del tipo "Entre las filas A y N"
    """
    if len(indices) > threshold:
        idx_str = f"Entre las filas {min(indices)} y {max(indices)}"
    else:
        idx_str = f"En las filas {', '.join(map(str,indices))}"
    return idx_str

# Desempaqueta el resultado de `qa['special_characters']`
# No lo puedo registrar porque no se asocia con una sola clave
# sino que se asocia con múltiples.
# A lo mejor hay una manera de dividir el resultado, pero no se me ocurrió ninguna práctica.
def unpack_special_characters(qa: dict):
    special_characters_ok: bool
    per_col_analysis: dict[str, dict[str, list[int]]]
    special_characters_ok, per_col_analysis = qa['special_characters']

    columns_spch = ['Variable Nombre', 'Cadena con caracteres especiales', 'Filas']
    data = list()
    
    if special_characters_ok:
        special_characters_result = 'OK'
        special_characters_df = empty_df(columns_spch)
    else:
        special_characters_result = "Hay columnas que poseen caracteres raros, ver detalle abajo."
        for variable, sub_result in per_col_analysis.items():
            for string_error, idx_list in sub_result.items():
                idx_str = compress_indices(idx_list)
                data.append((variable, string_error, idx_str))
        
        special_characters_df = pd.DataFrame(data, columns=columns_spch)
    
    return special_characters_result, special_characters_df

def unpack_qa(qa: None | dict):
    result = {
        "tidy_data": "Error",
        "header": "Error",
        "duplicates": "Error",
        "nullity_check": "Error",
        "special_characters": "Error",
        "tipo_datos": pd.DataFrame(),
        "detalle_caracteres_especiales": pd.DataFrame()
    }

    if not qa:
        return result

    for key, method in QAUnpacker.items():
        result[key] = method(qa)

    special_characters_result, special_characters_df = unpack_special_characters(qa)

    result["special_characters"] = special_characters_result
    result["detalle_caracteres_especiales"] = special_characters_df

    return result

path_or_dict = str | dict

class Reporter:
    report: dict

    def __init__(self, subtopico: str, date: str, report: path_or_dict):
        self.subtopico = subtopico
        self.date = date
        self.log = LoggerFactory.getLogger(f'reporter<{subtopico}>')
        match report:
            case json if isinstance(report, str):
                self.log.debug(f"Cargando reporte desde {report}")
                with open(report, 'r', encoding='utf-8') as fp:
                    self.report = json.load(fp)
                self.log.debug("Listo!")
            case dicc if isinstance(report, dict):
                self.report = dicc

    @staticmethod
    def encoding_resultado_str(encoding: str):
        is_valid = encoding == 'utf_8'

        if is_valid:
            return 'Encoding válido. (UTF-8)'
        else:
            return f'Encoding inválido. ({encoding}) Debería ser UTF-8.'

    @staticmethod
    def delimiter_resultado_str(delimiter: str):
        is_valid = delimiter == ','

        if is_valid:
            return "Delimitador válido. (,)"
        else:
            return f"Delimitador inválido. ({delimiter}) Debería ser ','"

    @staticmethod
    def process_column_error_str(errores: str):
        columnas_errores = filter(lambda e: 'BadColumnsException' in e, errores)
        columna_errores: str = next(columnas_errores)

        start_index = columna_errores.find('{')
        end_index = columna_errores.find('}')
        decl_no_efvo = columna_errores[start_index:end_index+1]

        start_index = columna_errores.find('{', start_index+1)
        end_index = columna_errores.find('}', end_index+1)
        efvo_no_decl = columna_errores[start_index:end_index+1]

        decl_no_efvo = decl_no_efvo[1:-1].split(', ')
        decl_no_efvo = list(map(lambda x: str(x[1:-1]), decl_no_efvo))

        efvo_no_decl = efvo_no_decl[1:-1].split(', ')
        efvo_no_decl = list(map(lambda x: str(x[1:-1]), efvo_no_decl))

        decl_no_efvo, efvo_no_decl = complete(decl_no_efvo, efvo_no_decl)
        __data = list(zip(decl_no_efvo, efvo_no_decl))
        return __data

    @staticmethod
    def reporte_dataset(nombre: str, qad: dict) -> dict:
        columns = ['Declaradas Faltantes', 'Sin Declarar']

        if not (error_str := qad.get('errors')):
            columnas_errores = empty_df(columns)
        else:
            data = Reporter.process_column_error_str(error_str)
            columnas_errores = pd.DataFrame(data, columns=columns)
        
        encoding: str = qad['detected_encoding']
        encoding: str = encoding.lower()
        encoding: str = encoding.replace('-', '_')
        encoding: str = encoding.replace('_', '')

        encodings = {
            'utf8': 'UTF-8',
            'utf8sig': 'UTF-8-SIG',
            'iso88591': 'latin1',
        }

        if encoding in encodings:
            encoding = encodings[encoding]

        encoding_resultado: str = Reporter.encoding_resultado_str(encoding)

        delimiter: str = qad['delimiter']
        delimiter_resultado: str = Reporter.delimiter_resultado_str(delimiter)

        quality_checks: None | dict = qad.get('quality_checks')
        quality_checks: dict = unpack_qa(quality_checks)
        
        reporte = {
            'nombre': nombre,
            'columnas_errores': columnas_errores, 
            'encoding': encoding,
            'encoding_resultado': encoding_resultado,
            'delimiter': delimiter,
            'delimiter_resultado': delimiter_resultado,
            **quality_checks
        }

        return reporte

    @staticmethod
    def string_errores_graficos(errores: list):
        """
        Devuelve una string con los errores de graficos.
        """
        return f"{len(errores)} errores graficos." + '' if len(errores) == 0 \
                else f"Graficos {', '.join(map(str, errores))}"
    
    @staticmethod
    def make_list(df, columns):
        tabla = empty_df(columns=columns)
        if len(df) > 0:
            tabla = pd.DataFrame({k: df for k in columns})
        return tabla

    def generar_reporte(self, output_folder=None, merge_to=None):
        if not output_folder:
            output_folder = f'./output/{self.subtopico}/'

        output_folder = file(output_folder)
        self.log.info(f"Generando reporte para {self.subtopico} en {output_folder}")
        template_queue: list[Template] = []
        outfiles: list[str] = []

        # Gutter

        gutter = templates.Gutter.from_dict({'subtopico': self.subtopico, 
                                             'fecha_verificacion': self.date})
        
        gutter_outfile = 'gutter.md'

        template_queue.append(gutter)
        outfiles.append(gutter_outfile)

        # Resumen

        cant_graficos, errores = self.report['verificacion_nivel_registro']

        filesystem_analysis_result = self.report['verificacion_sistema_de_archivos'][1]

        datasets_declarados = set(filesystem_analysis_result['datasets']['declarados'])
        datasets_efectivos = set(filesystem_analysis_result['datasets']['efectivos'])
        datasets_interseccion = set(filesystem_analysis_result['datasets']['interseccion'])
        datasets_no_declarados = list(datasets_efectivos - datasets_declarados)
        datasets_no_cargados  = list(datasets_declarados - datasets_efectivos)
        
        scripts_declarados = set(filesystem_analysis_result['scripts']['declarados'])
        scripts_efectivos = set(filesystem_analysis_result['scripts']['efectivos'])
        scripts_interseccion = set(filesystem_analysis_result['scripts']['interseccion'])
        scripts_no_declarados = list(scripts_efectivos - scripts_declarados)
        scripts_no_cargados   = list(scripts_declarados - scripts_efectivos)

        tabla_resumen_ = {
            'Datasets': list(map(len, [datasets_declarados, datasets_efectivos,
                                       datasets_interseccion, 
                                       datasets_no_declarados, 
                                       datasets_no_cargados])),
                                       
            'Scripts' : list(map(len, [scripts_declarados, scripts_efectivos, 
                                       scripts_interseccion, scripts_no_declarados, 
                                       scripts_no_cargados]))
        }

        tabla_resumen = pd.DataFrame(tabla_resumen_, index = ['Declarados', 
                                                              'Efectivos', 
                                                              'Interseccion', 
                                                              'No declarados', 
                                                              'No cargados'])
        

        tabla_datasets_no_declarados = Reporter.make_list(datasets_no_declarados, 
                                                          ['Datasets no declarados'])
        
        tabla_datasets_no_cargados = Reporter.make_list(datasets_no_cargados, 
                                                        ['Datasets no cargados'])
        
        tabla_scripts_no_declarados = Reporter.make_list(scripts_no_declarados, 
                                                         ['Scripts no declarados'])
        
        tabla_scripts_no_cargados = Reporter.make_list(scripts_no_cargados, 
                                                       ['Scripts no cargados'])

        resumen = {
            'cant_graficos' : cant_graficos,
            'string_errores_graficos' : Reporter.string_errores_graficos(errores),
            'tabla_resumen' : tabla_resumen,
            'tabla_datasets_no_cargados' : tabla_datasets_no_cargados,
            'tabla_datasets_no_declarados' : tabla_datasets_no_declarados,
            'tabla_scripts_no_cargados' : tabla_scripts_no_cargados,
            'tabla_scripts_no_declarados' : tabla_scripts_no_declarados
        }

        resumen = templates.Resumen.from_dict(resumen)
        template_queue.append(resumen)
        outfiles.append('resumen.md')

        # Inspeccion Fuentes

        fuentes, instituciones = list(zip(*self.report['verificacion_fuentes']))
        fuentes_df = pd.DataFrame({'Fuente': fuentes, 'Institución': instituciones})

        inspeccion_fuentes = {'data': fuentes_df}
        inspeccion_fuentes = templates.InspeccionFuentes.from_dict(inspeccion_fuentes)
        template_queue.append(inspeccion_fuentes)
        outfiles.append('inspeccion_fuentes.md')

        # Metadatos Incompletos

        metadatos_incompletos_ = self.report['verificacion_sistema_de_archivos'][2]
        metadatos_incompletos = empty_df(columns=['Dataset Archivo', 
                                                   'Columna Plantilla', 
                                                   'Filas Incompletas'])

        if len(metadatos_incompletos_.keys()) > 0:
            metadatos_incompletos = metadatos_incompletos_

        metadatos_incompletos_df = pd.DataFrame.from_dict(metadatos_incompletos)
        metadatos_incompletos = {'data': metadatos_incompletos_df}
        metadatos_incompletos = templates.MetadatosIncompletos \
                                            .from_dict(metadatos_incompletos)
        template_queue.append(metadatos_incompletos)
        outfiles.append('metadatos_incompletos.md')

        # Dataset titulo

        datasest_verificados_df = Reporter.make_list(list(datasets_interseccion), 
                                                     ['Datasets Verificados'])
        
        dataset_titulo = {'data': datasest_verificados_df}
        dataset_titulo = templates.DatasetTitulo.from_dict(dataset_titulo)
        template_queue.append(dataset_titulo)
        outfiles.append('dataset_titulo.md')

        # Datasets 

        chequeos = self.report['verificacion_datasets'][0]
        reportes: list[templates.ReporteDataset] = [None for _ in chequeos]
        outfiles_datasets = [None for _ in chequeos]

        for i, chequeo in enumerate(chequeos.items()):
            reporte_i = self.reporte_dataset(*chequeo)
            reportes[i] = templates.ReporteDataset.from_dict(reporte_i)
            outfiles_datasets[i] = chequeo[0]+".md"
        

        template_queue += reportes
        outfiles += outfiles_datasets

        outfiles = map(lambda x: os.path.join(output_folder, x), outfiles)
        outfiles = list(outfiles)

        for template, outfile in zip(template_queue, outfiles):
            template.render(outfile)
        
        if merge_to:
            merge_to = file(os.path.join(output_folder, merge_to))
            outfiles.append(merge_to)

            with open(merge_to, 'w', encoding='utf-8') as merged_file: 
                for archivo in outfiles:
                    if not os.path.isfile(archivo):
                        continue

                    merged_file.write(open(archivo, encoding='utf-8').read())
            
        return outfiles

