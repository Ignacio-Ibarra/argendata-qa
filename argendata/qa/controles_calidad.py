from argendata.utils import MethodMapping
from pandas import DataFrame, isnull, Series
from numpy import nan
from functools import reduce
import re

# TODO: No es un Verificador per se porque tiene que tener las siguientes capacidades:
#   - Poder ser creado con un diccionario que contiene los chequeos que van a realizarse,
#     junto con los parámetros de cada uno.
# 
#   - Poder ser creado dinámicamente en función de los parámetros previamente descritos, y ser aplicado
#     de manera dinámica.
# 
# Sin embargo, *podría* ser un Verificador, si o bien ampliamos el verificador, o bien lo restringimos
# a que tenga otro comportamiento.
# 
# La diferencia más grande que tenía antes era la llamada a las funciones con parámetros dinámicos, pero
# los verificadores, al ser subclases de DynamicExecutor, ya tienen esa capacidad.
#
# En principio esto NO es una clase para aprovechar la extensibilidad del MethodMapping con los decoradores
# y mantener el código lightweight. Pero quizá usar un Verificador sea beneficioso. (?)

controles = MethodMapping()

@controles.register('tidy_data')
def is_tidy(data: DataFrame, keys: list[str], threshold: float = 0.5):
    ncols = len(data.columns)
    nkeys = len(keys)
    ratio = (nkeys / ncols)
    result = 1 - ratio
    return result <= threshold


@controles.register('nullity_check')
def number_of_nulls(data: DataFrame, non_nullable):
    nulls_per_col = {colname : column.isna().sum() for colname, column in data.items()}
    
    result = [x for x in non_nullable if nulls_per_col.get(x) > 0]
    return len(result) == 0, result

# @controles.register('cardinality')
# def check_cardinality(data: DataFrame, keys: list[str]):
#     # all(data[keys].apply(lambda x: x.nunique() == len(data))) (?)
#     real = len(data)
#     expected = 1
#     for k in keys: 
#         x : int = data[k].nunique()
#         expected = expected * x
#     return real <= expected

@controles.register('duplicates')
def check_duplicates(data: DataFrame, keys: list[str])->bool:
    """Verifica si existe filas duplicadas, tomando en cuenta sólo las columnas claves

    Args:
        data (DataFrame): dataset analizado
        keys (list[str]): lista de columnas sobre las cuales se analiza existencia 
        de duplicados

    Returns:
        bool: True tiene duplicados; False no tiene. 
    """
    return bool(data.duplicated(subset=keys).sum() > 0)

PATRON_WRONG_COLNAME = re.compile(r'[^a-z0-9_]|(^[^a-z])')
def check_wrong_colname(cadena): 
    """Devuelve True si la cadena es inválida, y False si no."""
    # Definir una expresión regular que acepte solo letras y números
    # Buscar si hay coincidencias en la cadena
    if len(cadena) == 0 or len(cadena.replace(' ', '')) == 0:
        return True
    
    coincidencias = PATRON_WRONG_COLNAME.findall(cadena)
    # Devolver True si hay coincidencias, lo que significa que hay caracteres raros
    return len(coincidencias) != 0

@controles.register('header')
def wrong_colnames(data: DataFrame, col_list: list[str]):
    """Devuelve una tupla que contiene:
        - True si ninguna columna tiene caracteres raros, False sino.
        - Una lista de las columnas que tienen caracteres raros. (Si no hay, devuelve una lista vacía)"""
    wrong_cols = list(filter(check_wrong_colname, col_list))
    return len(wrong_cols) == 0, wrong_cols

def tiene_caracteres_raros(cadena):
    """Devuelve True si la cadena es tiene caracteres raros, y False si no."""
    # Definir una expresión regular que acepte solo letras y números
    patron = re.compile(r"[^a-zA-Z0-9\s,.áéíóúüñôçÁÉÍÓÚÜÑÇ_' \-\(\)]+")
    # Buscar si hay coincidencias en la cadena
    try:
        if isnull(cadena) == False:
            coincidencias = patron.search(cadena)
            return coincidencias is not None
        else:
            return False
    except Exception as exc:
        print(f"{exc}")

def _check_special_characters(serie:Series, count_header_row=True):
    n = 2 if count_header_row else 0
        
    row_status = serie.apply(tiene_caracteres_raros)

    if row_status.sum() <= 0: # any
        return []
    
    idx = row_status[row_status == True].index.tolist()

    #return [(x+n, serie.iloc[x+n]) for x in idx]

    result = dict()
    for v,k in serie[row_status].items():
        result.setdefault(k, []).append(v)

    return result

@controles.register('special_characters')
def special_characters(data: DataFrame):
    is_ok = True
    result = dict()
    for col in [colname for colname, dtype in data.dtypes.items() if dtype == object]:
        column_analysis = _check_special_characters(data[col])
        if column_analysis:
            result[col] = column_analysis
            is_ok = False

    return is_ok, result

@controles.register('variables')
def verificar_variables(df: DataFrame, declarados: DataFrame):
    """Devuelve una tupla que contiene:
        - True si las variables declaradas en la plantilla son las mismas que las del dataset, False sino.
        - Una lista de las variables detectadas en el DataFrame.
        - La diferencia simétrica entre las variables declaradas y las detectadas.
    """
    dtypes: list[tuple[str,str]] = (df.dtypes.apply(str)
                                                .reset_index()
                                                .to_records(index=False)
                                                .tolist())

    variables: list[tuple[str,str]] = (declarados[['variable_nombre', 'tipo_dato']].drop_duplicates()
                                                                                        .to_records(index=False)
                                                                                        .tolist())
    dtypes: set[tuple[str,str]] = set(dtypes)
    variables: set[tuple[str,str]] = set(variables)
    return dtypes == variables, list(dtypes), list(dtypes.symmetric_difference(variables))

def make_controls(d: dict[str, object|tuple]):
    """Factory method para crear controles de calidad"""
    def curry_object(data: DataFrame):
        result = dict()
        for k,v in d.items():
            params = (data, *v) if isinstance(v, tuple) and len(v) > 0 else (data, ) if (not v) or (v == Ellipsis) else (data, v)
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