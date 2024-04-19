# 


from typing import Iterable, Generator, Tuple, Literal, Any, Callable, Optional
from collections.abc import Collection
from pandas import DataFrame
from argendata.utils.fuzzy_matching import similar_to, evaluate_similarity, str_normalizer, auto_translate, detector
import pandas as pd
import numpy as np

string_keys = [
    'country_name_abbreviation',
    'pais',
    'partner_name_short_en',
    'region',
    'partner_region_name_short_es',
    'pais_o_region',
    'pais_o_grupo_de_paises',
    'countryname',
    'region_name',
    'pais_nombre'
    'nombre_pais'
]

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

all_keys = string_keys + code_keys

def get_similarities(input: str, universe: Iterable[str], generator=False) -> list[float] | Generator[float, None, None]:
    if len(universe) == 0:
        raise ValueError("Can't compare against an empty universe")
    
    comparison = similar_to(input)
    results = map(comparison, universe)

    if generator:
        return results
    
    return list(results)
    

def get_k_similar(input: str, universe: Iterable[str], k, with_scores=False, threshold=None) -> list[str] | list[tuple[str, float]]:
    similarities = get_similarities(input, universe)
    similarities = zip(universe, similarities)
    similarities = list(similarities)
    similarities.sort(reverse=True, key=lambda x: x[1])

    if threshold is not None:
        similarities = [(x,s) for x,s in similarities if s > threshold]

    result = similarities if with_scores else [x for x,_ in similarities]
    result = result[:k]
    
    return result

def get_k_similar_from(universe: Iterable[str], k, with_scores=False, threshold=None):
    return lambda input: get_k_similar(input, universe, k, with_scores=with_scores, threshold=threshold)


# FIXME: Esto por algun motivo no funciona bien con todos los codigos,
# puede ser un problema cruzado con get_k_similar.
def get_geo_columns_by_colnames(cols: Collection[str]) -> str:
    codes   = map(get_k_similar_from(code_keys, k=60, with_scores=True, threshold=0), cols)
    strings = map(get_k_similar_from(string_keys, k=60, with_scores=True, threshold=0), cols)

    code_scores = [sum([x for _,x in y]) for y in codes]
    string_scores = [sum([x for _,x in y]) for y in strings]

    codes_result = []
    names_result = []

    result = {
        'codes': codes_result,
        'names': names_result
    }

    for x, (a,b) in zip(cols, zip(code_scores, string_scores)):
        (codes_result if a > b else names_result).append(x)
    
    return result

def es_columna_codigo(series:pd.Series)->bool: 
    return series.apply(lambda x: len(str(x)) == 3).sum()> 0.90*len(series) 

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

def get_geo_columns_by_content(df:pd.DataFrame)->Optional[dict[str,str]]: 
    cod_cols = get_columna_codigo_iso(df=df)
    if  cod_cols: 
        result = {}
        for cod_col in cod_cols: 
            desc_col = get_paired_col(df=df.select_dtypes(object), ref_col=cod_col)
            if desc_col:
                result['codigo'] = cod_col
                result['descripcion'] = desc_col
        return result
    return None

TRUE = Literal[True]
FALSE = Literal[False]
void = None
empty_tuple = Tuple[void]


# Se puede modificar acá los parámetros para normalizar un string. 
normalize_parms : dict = {'to_lower':True, 
                          'rm_accents':True,
                          'rm_punct':True, 
                          'rm_spw':False, 
                          'rm_whitesp':True, 
                          'sort_words':False}

normalizer = str_normalizer(normalize_params=normalize_parms)

def columa_codigos_es_correcta(input_codes:list[str], codes_set:set) -> Tuple[TRUE, empty_tuple] | Tuple[FALSE, Tuple[Any]]:
    # Sólo me fijo si hay diferencias en los sets de codigos
    input_set = set(input_codes)
    diff = input_set - codes_set
    
    if len(diff):
        result = tuple((input_codes.index(x),x) for x in diff)
        return False, result
    else:
        return True, ()
    
def traer_nombre_similar(input_values:list[str], desc_values:list[str], final_thresh:float, normalizer_f:Optional[Callable]=normalizer):
    """ desc_values asumo que viene normalizado y traducido"""
    # input_values_translated = auto_translate(input_strings=input_values)
    input_values_normalized = input_values.copy()
    if normalizer_f:
        input_values_normalized = list(map(normalizer_f, input_values_normalized))
    selected = []
    for i, s1 in enumerate(input_values_normalized): 
        scores_s1 = []
        for s2 in desc_values:
            scr = evaluate_similarity(s1=s1, s2=s2)
            scores_s1.append(scr)
        
        scores_s_arr = np.array(scores_s1)
        sorted_ids = np.argsort(scores_s_arr)[::-1]
        scores_s_arr_sorted = scores_s_arr[sorted_ids]
        desc_values_sorted = np.array(desc_values)[sorted_ids]
        desc_values_sorted_selected = desc_values_sorted[scores_s_arr_sorted>final_thresh]
        if len(desc_values_sorted_selected)>0:
            selected.append((i, s1, desc_values_sorted_selected[0]))
        else:
            selected.append((i, s1, None))
    
    return selected

def columna_nombres_es_correcta(input_values:list[str], desc_values:list[str], final_thresh:float, normalizer_f:Optional[Callable]=normalizer) -> Tuple[TRUE, empty_tuple] | Tuple[FALSE, Tuple[Any]]:
    """ desc_values asumo que viene normalizado y traducido"""
    # Debe devolver el indice, el nombre y si está o no en el nomenclador (el indice debería venir pareado
    # con el indice del codigo)
    similares = traer_nombre_similar(input_values=input_values, desc_values=desc_values, final_thresh=final_thresh, normalizer_f=normalizer)
    ids_no_encontrados = np.array(list(map(lambda x:x[0], filter(lambda x: x[2]==None, similares)) ) )
    input_values_no_encontrados = tuple(list(np.array(input_values)[ids_no_encontrados])) 
    # ...

    if len(ids_no_encontrados)==0:
        return True, ()
    else:
        return False, input_values_no_encontrados


# A) PROGRAMA PARA DETERMINAR LAS GEO_COLUMNS 
# Tengo la metadata, el df y una lista geoinfo = [...] que posee todos los niveles de agregacion de datasets geográficos válidos
# Busco geo_columns mediante get_geo_columns_joan: para ello verifico si entre las columnas del dataset hay al menos una que 
# matchean aproximadamente o bien con algun elemento de code_keys, o bien con algun elemento de string_keys, o bien con algún elemento de ambas. 
# Devuelve un diccionario o None
# Dict: Devolvió un diccionario, depende de lo que devuelva tengo distinas opciones (ver A.1.)
# None:  
## Verifico nivel_agregacion, devuelvo True o False
## True: busco las geo_columns con get_geo_columns_nacho, depende de lo que devuelva tengo distinas opciones (ver B). 
## False: pass

## A.1.) PROGRAMA QUE TRATA DICCIONARIO GENERADO POR get_geo_columns_joan 
## Devuelve list[tuple(str,str)]
### CASO1: tengo un diccionario con una etiqueta para codigo y una etiqueta para descripción. 
### Tomo como válidas esas geo_columns y devuelvo: [(cod_col1, desc_col1)]

### CASO2: tengo un diccionario con más de una etiqueta para codigo y descripción.
### Tengo que aplicarle geo_columns_nacho para poder asignar los pares  [(cod_col1, desc_col1), (cod_col2, desc_col2),...]

### CASO3: solo tengo códigos
### Reporto error: "Falta columna de descripciones para poder evaluar consistentente las referencias geográficas".
### Devuelvo una lista con la forma [(cod_col1, None), (cod_col2, None)]

### CASO4: sólo tengo descripciones
### Reporto error: "Falta columna de cópdigos para poder evaluar consistentente las referencias geográficas". 
### Devuelvo una lista con la forma [(None, desc_col1), (None, desc_col2)]

# PROGRAMA QUE VERIFICA QUE UN CODIGO ESTE EN EL NOMENCLADOR. ---buscar_codigo
# PROGRAMA QUE ATIENDE CASO3 (usar --buscar_codigo)

# PROGRAMA QUE VERIFICA QUE UNA DESCRIPCION ESTE EN EL NOMENCLADOR. ---buscar_desc
# PROGRAMA QUE ATIENDE CASO4 (usar --buscar_desc)

# PROGRAMA QUE VERIFICA EL CONTENIDO DEL PAR GEO_COLUMN (CASO1 y CASO2)
# Tengo como input:
# a) un par para las columnas codigo, descripción. 
# b) un dataframe
# 1.obtengo el distinct para esas dos columnas
# 2.normalizo las descripciones.
# 3.verifico que el codigo esté en el nomenclador (0 está y 1no está) ---buscar_codigo
# 4.verifico que la desc_norm esté o sea similar con alguna desc_norm del nomencaldor y devuelvo 1, sino 0 ---buscar_desc
# 5.devuelvo df con codigo, desc, cod_encontrado (0 o 1), desc_encontrada (0 o 1)


# PROGRAMA QUE TOMA DECISIONES CON RESPECTO A LA DEVOLUCION DEL PROGRAMA ANTERIOR. 
##########################################################################################

#   ESTA ES LA PARTE QUE DECIA PARA EMULAR LO QUE PENSAMOS EN EL CUADRO

##########################################################################################



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

# A) Si tengo codigo y desc en el dataset entonces aplico las siguientes lógicas

# 1) El codigo es incorrecto, con la descripción busco cuál o cuales podrían ser 
# los códigos correctos (asumo que una descripción podría tener más de un código, e.g Unión Europea, Unión Soviética)

# a) Si esa descripción la encuentro entonces devolver: 
# f"El codigo proporcionado no se encuentra en nuestro nomenclador, pero para esa entidad tenemos los codigos {codigos_encontrados}"

# b) Si esa descripción no la encuentro entonces devolver:
# f"El codigo proporcionado no se encuentra en nuestro nomenclador y para esa entidad no tenemos códigos asignados. Comunicate con tu referente del equipo de Datos de ArgenData"

def devolverA1():
    ...

# 2) El codigo es correcto, busco el nombre y me fijo que sea el mismo que el del nomenclador

# a) Si la descripción en el nomenclador es la misma que la que tiene el usuario, no devolver nada.  

# a) Si la descripción en el nomenclador NO es la misma que la que tiene el usuario, devolver: 
# La descripción que tenemos para el codigo buscado y el codigo para la descripción que tiene el usuario


# ---------------------------------------------------------------------------------------------------------------------------------

from argendata.qa.verificadores import Verifica

@Verifica[DataFrame]
class Geocontroles:
    
    def __init__(self, df: DataFrame):
        ...
