from .logger import LoggerFactory, inject_logger

import json
from datetime import datetime, timedelta
from timeit import default_timer
from typing import TypeVar, Protocol, Generic


class Singleton(type):
    """
    Metaclase que implementa el patrón de singleton.
    Las clases que la heredan no pueden ser instanciadas más de una vez.
    Provee un método 'get_instance' que es heredado, el cual:
    - Si la clase no está instanciada, la crea.
    - Si está instanciada, la devuelve.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
            return instance

        raise RuntimeError("Class already instantiated. Use get_instance()")

    def get_instance(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class MethodMapping(dict):
    """Diccionario que asocia claves a funciones. Sirve para crear selectores de estrategia."""

    def __register__(self, key, f):
        self[key] = f
        return f

    def register(self, key_or_alias):
        match key_or_alias:
            case alias if isinstance(key_or_alias, str):
                return lambda f: self.__register__(alias, f)
            case function if callable(key_or_alias):
                return self.__register__(function.__name__, function)


class staticproperty(property):
    """Utilidad para crear propiedades estáticas (que no tomen el puntero a self)"""

    def __get__(self, cls, owner):
        return staticmethod(self.fget).__get__(None, owner)()


class now:
    # noinspection PyMethodParameters
    @staticproperty
    def string():
        return datetime.now().strftime('%d-%m-%y_%H%M%S')


def json_to_file(filepath: str, obj, *args, **kwargs):
    with open(filepath, 'w') as fp:
        json.dump(fp=fp, obj=obj, *args, **kwargs)


def stopwatch(f: callable, *args, **kwargs):
    start = default_timer()
    result = f(*args, **kwargs)
    elapsed_time = default_timer() - start
    return result, timedelta(seconds=elapsed_time)


def keys_included(required_keys, data):
    """Chequea si una lista de claves está incluída en las claves de un dict."""
    return all(key in data for key in required_keys)


# Typing utils
# Algunas cosas que no están incluídas en typing por algún motivo.


_T_co = TypeVar('_T_co')
_T = TypeVar('_T')


class SupportsNext(Protocol[_T_co]):
    def __next__(self) -> _T_co: ...


class SupportsIter(Protocol[_T_co]):
    def __iter__(self) -> _T_co: ...


class Attribute(Generic[_T]): pass

class Final(Generic[_T]):
    """Indica que la variable no puede ser reasignada, pero si puede mutar."""


class Mutable(Generic[_T]):
    """Indica que la variable puede ser reasignada y mutar"""


class Inmutable(Generic[_T]):
    """Indica que la variable no puede ser reasignada ni mutar"""


def getattrc(attr: str):
    """Versión currificada de 'getattr'. La 'c' es de 'curry'."""
    return lambda obj: getattr(obj, attr)


# Utils Verificaciones =================================================================================================

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