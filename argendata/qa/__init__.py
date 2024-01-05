from argendata.qa.subtopico import Subtopico
from argendata.utils import LoggerFactory
from argendata.utils.gwrappers.resources import GResource
from argendata.constants import ARGENDATA_FOLDER_ID
from .verificadores import ControlSubtopico

logger = LoggerFactory.getLogger("controles_calidad")

def analyze(nombre_subtopico: str):
    subtopico = Subtopico.from_name(nombre_subtopico)
    verificaciones = subtopico.verificar(ControlSubtopico)
    return verificaciones