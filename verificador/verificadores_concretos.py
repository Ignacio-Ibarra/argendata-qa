from verificador.subtopico import Subtopico
from verificador.verificadores_abstractos import Verifica


@Verifica[Subtopico, "verificacion_"]
class Test:
    ...