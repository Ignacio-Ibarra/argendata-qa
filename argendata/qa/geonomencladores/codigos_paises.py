from typing import Iterable, Generator, Tuple, Literal, Any
from collections.abc import Collection
from pandas import DataFrame
from argendata.utils.fuzzy_matching import similar_to

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

def columa_codigos_es_correcta(columna) -> Tuple[TRUE, empty_tuple] | Tuple[FALSE, Tuple[Any]]:
    es_correcta = True

    # ...

    if es_correcta:
        return True, ()
    else:
        return False, (...)
    
def columna_nombres_es_correcta(columna) -> Tuple[TRUE, empty_tuple] | Tuple[FALSE, Tuple[Any]]:
    es_correcta = True

    # ...

    if es_correcta:
        return True, ()
    else:
        return False, (...)

# ---------------------------------------------------------------------------------------------------------------------------------

from argendata.qa.verificadores import Verifica

@Verifica[DataFrame]
class Geocontroles:
    
    def __init__(self, df: DataFrame):
        ...
