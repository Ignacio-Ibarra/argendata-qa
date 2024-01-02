from argendata.utils import MethodMapping
from pandas import DataFrame

controles = MethodMapping()

@controles.register('tidy_data')
def is_tidy(data: DataFrame, keys: list[str], threshold: float = 0.5):
    ...
    return True

@controles.register
def number_of_nulls(data: DataFrame):
    ...
    return True

@controles.register('cardinality')
def check_cardinality(data: DataFrame, keys: list[str]):
    ...
    return True

@controles.register('header')
def wrong_colnames(col_list: list[str]):
    ...
    return True

def check_special_characters(data: DataFrame):
    ...
    return object()

@controles.register('special_characters')
def special_characters(data: DataFrame):
    ...
    return check_special_characters(data)

def make_controls(d: dict[str, object|tuple]):
    def curry_object(data: DataFrame):
        result = dict()
        for k,v in d.items():
            params = (data, *v) if isinstance(v, tuple) and len(v) > 0 else (data, ) if not v else (data, v)
            result[k] = controles[k](*params)
        return result
    return curry_object




# Uso:
# 
# Para NO realizar un chequeo, no tiene que ser clave. Para realizarlo, tiene que ser clave y tener un valor.
# Los valores son los argumentos adicionales de cada función. Si el valor es falsy, entonces se llama sólo con el
# dataframe a verificar, sin parámetros adicionales. 
#
# ensure_quality = make_controls({
#     'tidy_data': ['a'],
#     'number_of_nulls': None,
#     'cardinality': ['a'],
#     'header': None,
#     'special_characters': None
# })
# 
# ensure_quality(DataFrame())

# > {'tidy_data': True,
# >  'number_of_nulls': True,
# >  'cardinality': True,
# >  'header': True,
# >  'special_characters': <object at 0x7f6ab053b7d0>}