from typing import Protocol, TypeVar, Type, Generic, Final
from logger import LoggerFactory
import inspect
from inspect import Parameter
from types import MappingProxyType

T = TypeVar('T')

class Verificador(Protocol[T]):
    """Protocolo abstracto para que los métodos que tomen verificadores estén bien tipados y cumplan con la interfaz."""

    def __init__(self, name: str, other: object, *args, **kwargs): 
        """Ver `Verifica`"""

    def verificar_todo(self) -> dict:
        """Ejecuta todos los métodos que comiencen con el prefijo determinado. (Ver `Verifica`)
           :returns: Un diccionario que asocia <nombre_de_metodo> ~ <resultado> """


def __wrapper__(specialization_class, wrapped_class, prefix) -> Type:
    """
    Wrapper diseñado para `Verifica`.

    :param specialization_class La clase a la que se especializa el protocolo.
    :param wrapped_class La clase que va a ser decorada (envuelta).
    :param prefix El prefijo con el que se reconocen métodos de verificación.
    :returns: Una nueva clase, con el nombre artificialmente cambiado por la clase decorada.
    Se le agrega la funcionalidad de `verificar_todo()`, junto con el logger que especifica la subclase de verificador
    y la clase que verifica.
    """

    class DynamicExecutor(wrapped_class):  # Virtualmente cumple con el protocolo de Verificador.
        __name__ = wrapped_class.__name__
        _verificaciones: dict[str, tuple[callable, list[str]]] = dict()
        __specialization_classname__ = specialization_class if isinstance(specialization_class,
                                                                          str) else specialization_class.__name__

        def __init__(self, name: str, *args, **kwargs):
            self.log = \
                LoggerFactory.getLogger(f'Verificador<{self.__specialization_classname__}>.{__class__.__name__}<{name}>')
            self.name = name
            self.a_verificar = None
            wrapped_class.__init__(self, *args, **kwargs)

        def __str__(self):
            return __class__.__name__

        def verificar_todo(self) -> dict:
            result = dict()
            for name, (method, parameters) in self._verificaciones.items():
                params = tuple(getattr(self, name) for name in parameters)
                result[name] = method(self, *params)
            return result

    DynamicExecutor.__name__ = wrapped_class.__name__

    for name, method in wrapped_class.__dict__.items():
        if callable(method) and name.startswith(prefix):
            parameters: MappingProxyType[str, Parameter] = inspect.signature(method).parameters
            parameters: filter[str] = filter(lambda x: x != 'self', parameters.keys())
            parameters: list[str] = list(parameters)
            DynamicExecutor._verificaciones[name] = (method, parameters) 

    return DynamicExecutor


class Verifica(Protocol):
    """Wrapper de clase. Convierte una clase en un Verificador, dotándola de `verificar_todo()` y un logger
    especializado. `verificar_todo()` es una función especial, que al ejecutarse, ejecuta todos los métodos de la clase
    que empiecen con un prefijo determinado (en órden de declaración).
    Uso:

    @Verifica[<clase_a_verificar>, <opcional: prefijo>]
    class MiVerificador: ...

    Donde, `<clase_a_verificar>` especifica la clase que se va a verificar con la clase que se está decorando (es decir,
    la clase sobre la cual se van a ejecutar las verificaciones) y el prefijo opcional determina qué métodos van a
    ser considerados como verificaciones válidas.

    Por ejemplo,

    @Verifica[int] (prefijo predeterminado: 'verificar_')
    class VerificadorDeEnteros:
        verifica_suma_positivos(self): # Va a ser considerado como verificación válida
            return (1+1) == 2

        _verifica_suma_positivos(self): # No va a ser considerado
            return (1+1) != 2


    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("'Verifica' no puede ser inicializado.")

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("'Verifica' no puede ser inicializado.")

    @staticmethod
    def decorator(specialization_class, prefix) -> callable:
        """Version no currificada del wrapper."""

        def wrapper(wrapped_class) -> Type:
            """Currifico sólo la clase decorada"""
            return __wrapper__(specialization_class, wrapped_class, prefix=prefix)

        return wrapper

    @staticmethod
    def __class_getitem__(*args, **kwargs) -> Type:
        """Utilidad para instanciar @Verifica como un tipo genérico."""
        if not isinstance(args[0], tuple):
            return Verifica.decorator(args[0], 'verificar_')

        args: tuple[tuple, ...]
        args: tuple[Type, ...] = args[0]
        if len(args) == 0:
            raise TypeError("Verifica lleva al menos un parámetro de especialización.")

        specialization_class = args[0]
        prefix = 'verificar_'

        if len(args) > 1:
            if not isinstance(args[1], str):
                raise TypeError("El segundo argumento debe ser una 'str' por ser el prefijo.")
            args: tuple[Type, str]
            prefix = args[1]
        return Verifica.decorator(specialization_class, prefix)