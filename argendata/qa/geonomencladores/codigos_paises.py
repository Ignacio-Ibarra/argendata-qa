
from lingua import Language, LanguageDetectorBuilder
from typing import Tuple, Literal, Any, Callable, Optional, List
from collections.abc import Collection
from pandas import DataFrame
from argendata.utils.fuzzy_matching import evaluate_similarity, str_normalizer, get_k_similar_from
from argendata.utils.translator import auto_translator
import pandas as pd
import numpy as np

# Defino algunos tipos 
TRUE = Literal[True]
FALSE = Literal[False]
void = None
empty_tuple = Tuple[void]
empty_list = List[void]


# Defino función para normalizar strings según parámetros de entrada. 
normalize_parms : dict = {'to_lower':True, 
                          'rm_accents':True,
                          'rm_punct':True, 
                          'rm_spw':False, 
                          'rm_whitesp':True, 
                          'sort_words':False}

str_normalizer_f = str_normalizer(normalize_params=normalize_parms)

# Defino función para traducciones 
languages = [Language.ENGLISH, 
             Language.SPANISH,
             Language.FRENCH,
             Language.PORTUGUESE]

detector = LanguageDetectorBuilder.from_languages(*languages).build()
auto_translator_f = auto_translator(lang_detector=detector)

# Defino strings usuales para columnas que contengan descripciones
column_keys = [
    'country_name_abbreviation',
    'pais',
    'partner_name_short_en',
    'region',
    'partner_region_name_short_es',
    'pais_o_region',
    'pais_o_grupo_de_paises',
    'countryname',
    'region_name',
    'pais_nombre',
    'nombre_pais'
]

# Defino strings usuales para columnas que contengan codigos
code_keys = [
    'iso3_desc',
    'region_code',
    'partner_region_id',
    'iso3',
    'codigo_pais',
    'country_code',
    'partner_code',
    'iso3c',
    'iso3_desc_fundar'
]


# Función para encontrar columnas geo por fuzzy matching
def get_geo_columns_by_colnames(cols: Collection[str], similarity_func:Callable, threshold:float, k:int) -> Optional[Tuple[List[Tuple[str,float]]]]:
    result = None
    codes   = list(map(get_k_similar_from(code_keys, k=k, with_scores=True, threshold=threshold, similarity_func=similarity_func), cols))
    strings = list(map(get_k_similar_from(column_keys, k=k, with_scores=True, threshold=threshold, similarity_func=similarity_func), cols))
      
    
    if any(len(x)>0 for x in codes):
        result_codes = [x for x in list(codes) if x!=[]][0]
        result = (result_codes,)
    if any(len(x)>0 for x in strings): 
        result_strings =  [x for x in list(strings) if x!=[]][0]
        result = result + (result_strings,)

    return result


# Función para definir si una columna tiene codigos. 
def es_columna_codigo(series:pd.Series)->bool: 
    return series.apply(lambda x: len(str(x)) == 3).sum()> 0.90*len(series) 

# Función para obtener la columna que tiene códigos. 
def get_columna_codigo_iso(df:pd.DataFrame)->str:
    col_mask = df.apply(es_columna_codigo, axis=0)
    cod_cols = df.columns[col_mask].tolist()
    if len(cod_cols)==0:
        return None
    else: 
        return cod_cols

# Con esta función obtengo la cardinalidad de la relación entre dos variables de un dataset
def get_cardinality(df:pd.DataFrame, col1:str, col2:str)->Literal['1:1','1:n','n:1','n:n']:
    df_no_dup = df[[col1, col2]].drop_duplicates()

    # Obtener conteo de valores únicos para cada columna
    conteo_col1 = df_no_dup[col1].nunique()
    conteo_col2 = df_no_dup[col2].nunique()

    df_no_dup_len = len(df_no_dup)

    # Verificar la cardinalidad
    if conteo_col1 == df_no_dup_len and conteo_col2 == df_no_dup_len:
        return '1:1'
    elif conteo_col1 < df_no_dup_len and conteo_col2 == df_no_dup_len:
        return '1:n'
    elif conteo_col1 == df_no_dup_len and conteo_col2 < df_no_dup_len:
        return 'n:1'
    else:
        return 'n:n'

# Con esta función me traigo la primer columna que venga "pareada" con mi columna de referencia
# e.g si le paso ref_col == "iso3" me va a devolver la primer columna que
# tenga una relación '1:1' con la columna 'iso3' o me devuelve None si no 
# hay ninguna columna que tenga esa relación.  
def get_paired_col(df:pd.DataFrame, ref_col:str)->Optional[str]: 
    no_ref_col = [col for col in df.columns if col!=ref_col]
    for col in no_ref_col:
        cardinality = get_cardinality(df, col1=ref_col, col2=col)
        if cardinality == "1:1":
            # print(f"La cardinalidad de {ref_col} con {col} es {get_cardinality(df, col1=ref_col, col2=col)}")
            return col 
        else:
            return None

# Función para obtner 
def get_geo_columns_by_content(df:pd.DataFrame)->Optional[dict[str,str]]: 
    cod_cols = get_columna_codigo_iso(df=df)
    result = None
    if  cod_cols: 
        result = []
        for cod_col in cod_cols: 
            desc_col = get_paired_col(df=df.select_dtypes(object), ref_col=cod_col)
            result.append((cod_col,desc_col))
    if result:
        print("Se encontraron geo columns buscando el contenido")
    return result


def get_geo_columns(df:pd.DataFrame, colnames_string_matcher:Callable)->Optional[List[Tuple[str,str]]]:
    
    # primero busco geo_columns con matcheo difuso
    col_match = get_geo_columns_by_colnames(cols=df.columns.tolist(), similarity_func=colnames_string_matcher, threshold=0.9, k=5)
    if col_match:
        if all([len(x)==1 for x in col_match]):
            print("Se encontraron geo columns mediante fuzzy matching")
            return col_match
        else:
            print("Se buscan geo columns verificando contenido de columnas")
            col_match = get_geo_columns_by_content(df=df)
    else:
        print("Se buscan geo columns verificando contenido de columnas")
        col_match =  get_geo_columns_by_content(df=df)
    return col_match
        

    


def columa_codigos_es_correcta(input_codes:list[str], universe_codes:list[str]) -> Tuple[FALSE, empty_list, list[Tuple[int,str,bool]] ] | Tuple[TRUE,  list[Tuple[int,str,bool]], list[Tuple[int,str,bool]]]:
    """Es una función que evalua para cada codigo de la lista input_codes 
    si el codigo se encuentra en el universo de codigos provisto

    Args:
        input_codes (list[str]): Lista de códigos que se quiere verificar
        universe_codes (list[str]): Universo de códigos contra el que se requiere chequear. 

    Returns:
        Tuple[TRUE, empty_list, list[Tuple[int,str,bool]] ] | Tuple[FALSE,  list[Tuple[int,str,bool]], list[Tuple[int,str,bool]]]: 
        Si todos los códigos se encuentran, devuelve: True, una lista vacía de diferencias y el listado de resultados de la comparación. 
        Si hay al menos un código que no se encuentra, devuelve: False, una lista con diferencias y el listado de resultados de la comparación. 
    """
    result = [(i,x,x in universe_codes) for i,x in enumerate(input_codes)]
    diff = list(filter(lambda x: x[2]==False, result))
    
    if len(diff) == 0:
        return True, [], result
    else:
        return False, diff, result

def descripcion_compara_universo(s1:str, desc_universe_normalized:list[str])->np.array:
    
    scores_s1 = []

    # Para cada string en desc_universe
    for s2 in desc_universe_normalized:
        scr = evaluate_similarity(s1=s1, s2=s2)
        scores_s1.append(scr)
                        
    return np.array(scores_s1)

def traer_nombre_similar(input_desc:list[str], desc_universe:list[str], final_thresh:float, normalizer_f:Optional[Callable], translator_f:Optional[Callable])->List[Tuple[int, str, int|None, str|None]]:
    """Función que trae la descripción más similar comparando con el universo de descripciones, 
    siempre que la similitud tenga un score mayor al final_thresh. 

    Args:
        input_desc (list[str]): Descripciones input de países, se asume que están en español, pero no normalizadas.
        desc_universe (list[str]): Universo de descripciones de países contra los que se compara, están en español, pero no normalizadas. 
        final_thresh (float): Umbral para indicar si un score de similitud indica similitud o no. 
        normalizer_f (Optional[Callable], optional): Función para normalizar strings.
        translator_f (Optional[Callable], optional): Función para normalizar strings.

    Returns:
        List[Tuple[int, str, int|None, str|None]]: Devuelve una lista con el indice de la descripción, 
        la descripción, el indice de la descripción similar o None y la descripción similar o None
    """
    input_desc_analyzed = input_desc.copy()
    desc_universe_analyzed = desc_universe.copy()

    if translator_f:
        print("Traduciendo descripciones antes del análisis")
        input_desc_analyzed = translator_f(input_desc_analyzed)
        desc_universe_analyzed = translator_f(desc_universe_analyzed)

    if normalizer_f:
        print("Normalizando descripciones antes del análisis")
        input_desc_analyzed = list(map(normalizer_f, input_desc_analyzed))
        desc_universe_analyzed = list(map(normalizer_f, desc_universe_analyzed))
    
    selected = []
    
    # Para cada string en input_desc_normalized
    for i, s1 in enumerate(input_desc_analyzed): 
               
        scores_s1_arr = descripcion_compara_universo(s1=s1, desc_universe_normalized=desc_universe_analyzed)
        sorted_ids = np.argsort(scores_s1_arr)[::-1]
        scores_s_arr_sorted = scores_s1_arr[sorted_ids]
        desc_values_sorted = np.array(desc_universe)[sorted_ids]
        desc_values_sorted_selected = desc_values_sorted[scores_s_arr_sorted>final_thresh]
        
        if len(desc_values_sorted_selected) > 0:
            selected.append((i, input_desc[i], sorted_ids[0], desc_values_sorted_selected[0]))
        else:
            selected.append((i, input_desc[i], None, None))
        
    return selected


def columna_nombres_es_correcta(input_desc:list[str], desc_universe:list[str], final_thresh:float, normalizer_f:Optional[Callable]=str_normalizer_f, translator_f:Optional[Callable]=auto_translator_f) -> Tuple[TRUE, empty_list, List[Tuple[int, str, int, str]]] | Tuple[FALSE, List[Tuple[int, str, None, None]], List[Tuple[int, str, int|None, str|None]]]:
    """Función que define si una columna de descripciones es correcta segun un universo de descripciones válidos. 
    En caso de que no sea correcta devuelve descripciones incorrectas.   

    Args:
        input_desc (list[str]): Descripciones input de países, se asume que están en español, pero no normalizadas.
        desc_universe (list[str]): Universo de descripciones de países contra los que se compara, están en español, pero no normalizadas. 
        final_thresh (float): Umbral para indicar si un score de similitud indica similitud o no. 
        normalizer_f (Optional[Callable], optional): Función para normalizar strings. Defaults to str_normalizer_f.
        translator_f (Optional[Callable], optional): Función para normalizar strings. Defaults to auto_translator_f.

    Returns:
        Tuple[TRUE, empty_list, List[Tuple[int, str, int, str]]] | Tuple[FALSE, List[Tuple[int, str, None, None]], List[Tuple[int, str, int|None, str|None]]]:
        Devuelve una tupla de tres elementos: 
        a) TRUE or FALSE,
        b) Lista vacía si a) TRUE or Lista de tuplas con las descripciones e índices que no encontraron similares entre las descripciones válidas. 
        c) Lista con todas los resultados encontrados para cada descripción input.
    """
    result = traer_nombre_similar(input_desc=input_desc, desc_universe=desc_universe, final_thresh=final_thresh, normalizer_f=normalizer_f, translator_f=translator_f)
    no_encontrados = list(filter(lambda x: x[2]==None, result))
    
    if len(no_encontrados)==0:
        return True, [], result
    else:
        return False, no_encontrados, result


def busco_codigos_por_nombre(nombre_buscado:str, nomenclador:DataFrame)->Optional[list[str]]:
    codigos = None
    
    # Comparo nombres normalizados

    # Si el nombre lo encuentra devuelvo una lista con los codigos que encuentra por ese nombre
    if codigos:
        print(f"Para {nombre_buscado} se encontraron los códigos {codigos}") 
    return codigos

def busco_nombre_por_codigo(codigo_buscado:str, nomenclador:DataFrame)->Optional[str]:
    nombre = None

    # Logica para buscar nombre mediante codigo. 

    # Si el codigo lo encuentra, devuelvo el nombre
    if nombre:
        print(f"Para {codigo_buscado} se encontró la entidad {nombre}")
    return nombre
# ---------------------------------------------------------------------------------------------------------------------------------

from argendata.qa.verificadores import Verifica

@Verifica[DataFrame]
class Geocontroles:
    
    def __init__(self, df: DataFrame):
        ...
