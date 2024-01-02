import os
import pandas as pd
from pandas import DataFrame
import numpy as np

dtypes_conversion = {
    'alfanumerico': 'object', 
    'dicotomico': 'bool',
    'entero': 'int64', 
    'real': 'float64', 
    '': 'no completo'
    }

def useattr(obj, attr: str):
    return getattr(obj, attr)

def strips(x: str) -> str:
    return useattr(x, 'strip')()

def strip_accents(input_str: str) -> str:
    accent_map = {
        'ÀÁÂÃÄÅ': 'A',
        'àáâãäå': 'a',
        'ÈÉÊË': 'E',
        'èéêë': 'e',
        'ÌÍÎÏ': 'I',
        'ìíîï': 'i',
        'ÒÓÔÕÖØ': 'O',
        'òóôõöø': 'o',
        'ÙÚÛÜ': 'U',
        'ùúûü': 'u',
        'Ý': 'Y',
        'ýÿ': 'y',
        'Ñ': 'N',
        'ñ': 'n',
        'Ç': 'C',
        'ç': 'c'
    }

    for accented_chars, unaccented_char in accent_map.items():
        for accented_char in accented_chars:
            input_str = input_str.replace(accented_char, unaccented_char)

    return input_str


# Verificaciones ======================================================================================================

COLUMNAS_VERIFICACION_NIVEL_REGISTRO = ['orden_grafico','dataset_archivo','script_archivo',
                                        'variable_nombre','url_path','fuente_nombre','institucion']

def verificacion_nivel_registro(plantilla: DataFrame, columnas=COLUMNAS_VERIFICACION_NIVEL_REGISTRO) -> None | str:
   """Verifica que no haya registros duplicados en la plantilla. Los registros son
   observablemente iguales si tienen los mismos valores en todas las columnas especificadas."""
   result = None
   n_graficos = len(set(plantilla['orden_grafico']))

   nivel_registro = plantilla.groupby(columnas).size()    
   errores = np.unique(nivel_registro[nivel_registro > 1].index.get_level_values('orden_grafico').tolist())
   if len(errores) > 0:
      result = ", ".join(map(str, errores))
      
   return result


def verificacion_datasets(plantilla: DataFrame, datasets: list, dtype_map=dtypes_conversion):
    """Verifica que los datasets declarados en la plantilla sean los mismos que los efectivos"""

    columnas = ['dataset_archivo','variable_nombre','tipo_dato','primary_key','nullable']
    datasets_declarados_df: DataFrame = plantilla[columnas].drop_duplicates()

    # Cambiar el tipo de dato acá no cumple ningún propósito para lo que hace
    # la función en sí misma, pero introduce un efecto colateral.
    _tipo_dato = datasets_declarados_df.loc[:, 'tipo_dato']
    _tipo_dato = _tipo_dato.str.lower().apply(strip_accents)
    _tipo_dato = _tipo_dato.map(dtype_map).fillna("no completo")

    datasets_declarados_df.loc[:, 'tipo_dato'] = _tipo_dato

    datasets_declarados: set[str] = set(map(lambda x: x.strip(), datasets_declarados_df['dataset_archivo']))

    datasets_efectivos: set[str] = set(datasets)

    datasets_interseccion = datasets_declarados.intersection(datasets_efectivos)

    return (datasets_interseccion == datasets_declarados == datasets_efectivos), datasets_interseccion, datasets_declarados_df


def verificacion_scripts(plantilla, scripts):
    efectivos = set(scripts)
    declarados = set(plantilla.script_archivo)
    return efectivos.intersection(declarados) == declarados == efectivos, efectivos.intersection(declarados)


def verificacion_variables(declarados: DataFrame, df: DataFrame, filename: str):
    dtypes = df.dtypes.apply(str).reset_index().to_records(index=False).tolist()

    slice_dataset = declarados[declarados.dataset_archivo == filename]
    variables = slice_dataset[['variable_nombre', 'tipo_dato']].to_records(index=False).tolist()

    return dtypes == variables


def verificar_variables(declarados: DataFrame, filepath):
    filename = os.path.basename(filepath)
    df = pd.read_csv(filepath)
    return verificacion_variables(declarados, df, filename)


def verificacion_completitud(plantilla: DataFrame, interseccion: set[str], not_target: list[str] = ['seccion_desc','nivel_agregacion', 'unidad_medida']) -> DataFrame:
    """Busca filas incompletas"""
    _plantilla = plantilla.copy()
    _plantilla = _plantilla.loc[_plantilla.dataset_archivo.isin(interseccion), _plantilla.columns.difference(not_target)] 
    _plantilla = _plantilla.groupby('dataset_archivo').agg(lambda x: x.isna().sum())
    _plantilla = _plantilla.stack().reset_index()
    _plantilla.columns = ['dataset_archivo','columna_plantilla','filas_incompletas']
    _plantilla = _plantilla[_plantilla.filas_incompletas > 0]

    return _plantilla


def inspeccion_fuentes(plantilla, columnas=['fuente_nombre', 'institucion']):
    return plantilla[columnas].dropna().drop_duplicates()