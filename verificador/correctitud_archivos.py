from gwrappers import GFile
from utils import MethodMapping
from utils.files.charsets import get_codecs


class VerificadorCSV:
    verificaciones = MethodMapping()

    def verificacion(self):
        return lambda f: self.verificaciones.register(f)

    def __init__(self, archivo: GFile):
        self.archivo = archivo

    @verificaciones.register('encoding')
    def verificacion_charset(archivo: str):
        codecs = get_codecs(archivo)

        if len(codecs) > 0:
            return True
        else:
            return False

    def verificar_todo(self):
        archivo = self.archivo.download(f'./temp/{self.archivo.DEFAULT_FILENAME}')
        return {nombre: v(archivo) for nombre, v in self.verificaciones.items()}



