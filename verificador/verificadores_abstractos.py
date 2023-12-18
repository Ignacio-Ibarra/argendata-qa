from typing import Protocol, TypeVar, Type, Any
from logger import LoggerFactory

T = TypeVar('T')


class Verificador(Protocol[T]):
    class Verificador(Protocol[T]):
        """Protocolo abstracto para que los métodos que tomen verificadores
            estén bien tipados y cumplan con la interfaz."""

        def __init__(self, name: str, other: object, *args, **kwargs):
            """Ver `Verifica`"""
            ...

        def verificar_todo(self):
            """Ejecuta todos los métodos que comiencen con el prefijo determinado. (Ver `Verifica`)
               :returns: Un diccionario que asocia <nombre_de_metodo> ~ <resultado> """
            ...


class Verifica(Protocol):
    ...