from src.utils.files import FileIterator, get_file_size
from src.utils.files.charsets.constants import ESP_CHARSET, PRIORITY_ENCODINGS


# TODO: Acá necesito saltearme las comillas porque los archivos .csv traen 'quoting' variable.
#   el criterio de ésta función es "sólo encargarse del encoding" es decir, no estoy chequeando si hay o no
#   quotes donde no deberían; simplemente estoy chequeando que esté bien codificado.
#   Sin embargo, ¿Hay alguna manera de NO hacer eso? Es difícil limpiar quotes si no conocemos el encoding,
#   pero al ser compatibles con ASCII quizá son fácilmente detectables indistintamente del encoding (?)
def has_errors(s: str, valid_charset=ESP_CHARSET) -> bool:
    """
    Determina si todos los caracteres de una string tiene caracteres inválidos o no. (Respecto al charset).
    Saltea las comillas y los newline.
    :param s: String a chequear
    :param valid_charset: Caracteres válidos
    :return: True si tiene errores, False sino.
    """
    for x in s:
        if x in ('"', '\n'):
            continue
        if x not in valid_charset:
            return True
    return False


# TODO: Parametrizar ésta función de manera proporcional al tamaño del archivo.
#   Pues con archivos suficientemente chicos, para un 'n' fijo, el tamaño de cada bloque puede ser cero.
#   Una forma puede ser fijando 'n' según el tamaño del archivo. (Parametrizar externamente)
#   Otra forma puede ser modificando la función para tener un piso del tamaño mínimo de bytes de cada bloque.
def __get_codecs(file: str, n: int, codecs: list[str], proportion: float, cutoff: int = 10) -> list[tuple[str, float]]:
    """
    Analiza un archivo para detectar cuál es la codifiación más probable con el que se codificó.
    :param file: Ruta al archivo
    :param n: Cantidad de bloques
    :param codecs: Lista de los nombres de los códecs validos (tiene que estar incluida en los codecs de Python)
    :param proportion: Proporcion a testear del archivo.
    :param cutoff: Es la cantidad de bloques contiguos después
    :return: list[tuple[str, float]] donde:
         - La primera coordenada es el encoding
         - La segunda coordenada ('b') es un float que cumple:
            - (1 >= b > 0) si no hubo errores. Donde el número es el porcentaje de bloques que pasó.
            - (b == 0) si sólo pudo leer el header
            - (b == -1) si hubo una excepción antes de leerse por primera vez.
            - (b == -2) si hubo un error leyendo la primer línea.
    """
    # constantes
    FIRST_LINE_ERRORS = -2
    UNINITIALIZED = -1

    # variables
    size = get_file_size(file)
    k = size // n
    block_size = int(k * proportion)

    score = [UNINITIALIZED for _ in codecs]
    data = [list() for _ in codecs]

    # print(f"Analyzing '{file}' on {n} blocks of size {block_size} (in bytes). "
    #       f"They represent {(100 * block_size * n) / size:.0f}% of the file.")

    # La primera iteracion me guardo la primer linea,
    # luego siguen n bloques.
    for j in range(n + 1):
        for i, codec in enumerate(codecs):

            if score[i] == FIRST_LINE_ERRORS:
                continue

            if j >= cutoff and score[i] < 0:
                continue

            with open(file, encoding=codec) as fp:
                try:
                    if len(data[i]) == 0:  # La primera vez, cargo la primera linea
                        initial_loader = FileIterator.lines
                        first_line = next(initial_loader(fp))
                        score[i] = -2 if has_errors(first_line) else 0

                        if score[i] == 0:  # Si no dio error, guardo los datos relevantes
                            data[i].append(first_line)
                            data[i].append(str())
                    else:
                        fp.seek(j * k)
                        iterator = FileIterator.chunks(block_size)
                        chunk = next(iterator(fp))
                        data[i][1] = chunk

                        # Chequeo que [primera linea] + [chunk]
                        # no tenga errores. Esto es necesario porque algunos codecs
                        # necesitan los bytes de comienzo del archivo.
                        score[i] += (0 if has_errors("".join(data[i])) else 1)

                except Exception:
                    continue

    return zip(codecs, map(lambda x: x if x < 0 else x / n, score))


def get_codecs(file: str,
               n: int = 100,
               codecs: list[str] = PRIORITY_ENCODINGS,
               proportion: float = 0.1,
               cutoff: int = 10) -> list[tuple[str, float]]:
    """
    Ver `__get_codecs`. Acá se filtran los resultados erróneos, y se los ordena según:
    - Primero, descendentemente según el score,
    - Si empatan, según el orden en el que aparecen en la lista de codecs.
    """
    result = __get_codecs(file, n, codecs, proportion, cutoff)
    result = filter(lambda x: x[1] > 0, result)
    result = list(result)
    result.sort(key=lambda x: (-x[1], codecs.index(x[0])))
    return result
