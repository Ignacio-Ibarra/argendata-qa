from argendata.qa.subtopico import Subtopico
from argendata.utils import LoggerFactory
from argendata.utils.gwrappers.resources import GResource
from argendata.constants import ARGENDATA_FOLDER_ID
from .verificadores import ControlSubtopico

logger = LoggerFactory.getLogger("controles_calidad")

def analyze(nombre_subtopico: str, entrega: int):
    logger.info(f'Generando reporte de calidad para {nombre_subtopico}{str(entrega)}...')
    subtopico = Subtopico.from_name(nombre_subtopico, entrega)
    verificaciones = subtopico.verificar(ControlSubtopico)
    return verificaciones