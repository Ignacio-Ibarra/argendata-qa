from typing import Iterable, Generator, Tuple, Literal, Any, Callable, Optional
from collections.abc import Collection
from pandas import DataFrame
from argendata.utils.fuzzy_matching import similar_to, evaluate_similarity, str_normalizer, auto_translate, detector
from pandas import Series
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
def get_geo_columns(cols: Collection[str]) -> str:
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
        return False, tuple(diff)
    else:
        return True, ()
    
def traer_nombre_similar(input_values:list[str], desc_values:list[str], final_thresh:float, normalizer_f:Optional[Callable]=normalizer):
    """ desc_values asumo que viene normalizado y traducido"""
    # input_values_translated = auto_translate(input_strings=input_values)
    input_values_normalized = input_values.copy()
    if normalizer_f:
        input_values_normalized = list(map(normalizer_f, input_values_normalized))
    selected = []
    for s1 in input_values_normalized: 
        scores_s1 = []
        for s2 in desc_values:
            scr = evaluate_similarity(s1=s1, s2=s2, threshs=[1, 1, 0.4, 0.1, 0.1], weights= [0.2, 0.2, 0.2, 0.2, 0.2])
            scores_s1.append(scr)
        
        scores_s_arr = np.array(scores_s1)
        sorted_ids = np.argsort(scores_s_arr)[::-1]
        scores_s_arr_sorted = scores_s_arr[sorted_ids]
        desc_values_sorted = np.array(desc_values)[sorted_ids]
        desc_values_sorted_selected = desc_values_sorted[scores_s_arr_sorted>final_thresh]
        if len(desc_values_sorted_selected)>0:
            selected.append((s1, desc_values_sorted_selected[0]))
        else:
            selected.append((s1, None))
    
    return selected


def columna_nombres_es_correcta(input_values:list[str], desc_values:list[str], normalizer_f:Optional[Callable]=normalizer) -> Tuple[TRUE, empty_tuple] | Tuple[FALSE, Tuple[Any]]:
    """ desc_values asumo que viene normalizado y traducido"""
    similares = traer_nombre_similar(input_values=input_values, desc_values=desc_values, normalizer_f=normalizer)
    no_encontrados = list(filter(lambda x: x[1]==None, similares))         
    # ...

    if len(no_encontrados)==0:
        return True, ()
    else:
        return False, tuple(no_encontrados)

# ---------------------------------------------------------------------------------------------------------------------------------

from argendata.qa.verificadores import Verifica

@Verifica[DataFrame]
class Geocontroles:
    
    def __init__(self, df: DataFrame):
        ...
