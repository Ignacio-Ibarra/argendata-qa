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