import errno
import os
from enum import Enum
from functools import partial
from io import TextIOWrapper
from typing import Callable, TextIO, Generator
from utils import SupportsIter, SupportsNext


def file(filename: str):
    """
    Utilidad para crear archivos. Crea todos las carpetas necesarias para que valga la ruta.
    :param filename: Ruta completa a un archivo. Ejemplo: '/path/to/file.bin'
    :return: Repite el filename.
    """
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    return filename


def get_file_size(file: TextIOWrapper | TextIO | str) -> int:  # (bytes)
    """
    :param file: Puntero o ruta al archivo.
    :return: Tamaño del archivo en bytes
    """
    if isinstance(file, str):
        with open(file) as fp:
            return get_file_size(fp)  # Recursión con casteo
    elif isinstance(file, TextIOWrapper):
        result = file.seek(0, 2)  # Indice 0 relativo al final.
        file.seek(0, 0)  # Devuelvo al principio el puntero.
        return result


def read_in_chunks(file_object: TextIOWrapper, chunk_bytesize=64) -> Generator[str, None, None]:
    """Devuelve un generador, donde cada próxima iteración es un bloque de 'chunk_bytesize' bytes de tamaño.
       :param file_object: Puntero a un archivo.
       :param chunk_bytesize: Tamaño del próximo bloque. (Valor predeterminado: 64 bytes)
       :return: Un generador donde cada iteración es un bloque de bytes.
       """
    while data := file_object.read(chunk_bytesize):
        if not data:
            break
        yield data


class FileIterator(Enum):
    lines: Callable[[SupportsIter[SupportsNext]], SupportsNext] = \
        staticmethod(iter)

    chunks: Callable[[int], Callable[[TextIO], Generator]] = \
        staticmethod(lambda bytesize: partial(read_in_chunks, chunk_bytesize=bytesize))

    def __call__(self):  # Existe sólo para que el static typechecker vea a FileIterator como 'callable'.
        raise NotImplementedError()
