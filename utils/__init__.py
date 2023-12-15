import json
from datetime import datetime, timedelta
from timeit import default_timer
from typing import TypeVar, Protocol


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

    def register(self, key):
        def wrapper(f: callable):
            self[key] = f
            return f

        return wrapper


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


class SupportsNext(Protocol[_T_co]):
    def __next__(self) -> _T_co: ...


class SupportsIter(Protocol[_T_co]):
    def __iter__(self) -> _T_co: ...
